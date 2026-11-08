"""Explicit representation selection and atomic rendering through trusted plugins."""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from artifactspec.core._contexts import RendererBuilder, RepresentationBuilder
from artifactspec.core.models import Composition, Content
from artifactspec.core.pipeline import PipelineError, _materialize
from artifactspec.core.syntax import SourceSpan
from artifactspec.core.validation import Diagnostic, ValidationResult, validate
from artifactspec.plugins import RegistrationError, Registry

ProvenanceStatus = Literal["available", "partial", "unavailable", "no_elements"]


@dataclass(frozen=True, slots=True)
class Artifact:
    path: Path
    media_type: str
    editable: bool


@dataclass(frozen=True, slots=True)
class RenderResult:
    artifact: Artifact
    output: str
    representation: str
    renderer: str
    warnings: tuple[Diagnostic, ...]
    limitations: tuple[str, ...]
    provenance: tuple[SourceSpan, ...]
    fallback: None = None
    provenance_status: ProvenanceStatus | None = None


def compose(
    content: Content, *, output: str, representation: str, registry: Registry
) -> Composition:
    """Select one explicit, output-compatible representation without fallback."""
    if not isinstance(registry, Registry):
        raise TypeError("composition requires a trusted runtime Registry")
    context = RepresentationBuilder(content, output, representation)
    try:
        registry.handler("representations", representation, output=output)
        for index, node in enumerate(content.nodes):
            context.node = node
            context.index = index
            registry.representation_handler(
                representation, node.object_type, output=output
            )(context)
    except Exception as exc:
        raise PipelineError(
            f"Representation {representation!r} failed for {output!r}: {exc}",
            code="representation_failed",
            limitations=tuple(context.limitations),
        ) from exc
    return context.finish()


def _write_atomically(path: Path, data: bytes) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = stream.name
            stream.write(data)
        Path(temporary).replace(path)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def _composition_provenance(
    composition: Composition,
) -> tuple[
    tuple[SourceSpan, ...],
    ProvenanceStatus,
]:
    """Collect source links for layout elements, not artifact byte ranges."""
    elements = composition.elements
    spans = tuple(dict.fromkeys(span for item in elements for span in item.provenance))
    status: ProvenanceStatus
    if not elements:
        status = "no_elements"
    elif all(item.provenance for item in elements):
        status = "available"
    elif any(item.provenance for item in elements):
        status = "partial"
    else:
        status = "unavailable"
    return spans, status


def render(
    text: str,
    registry: Registry,
    *,
    representation: str,
    renderer: str,
    destination: Path,
    source: str = "<memory>",
) -> RenderResult:
    """Validate, compose, and atomically replace a single artifact on success."""
    if not isinstance(registry, Registry):
        raise TypeError("rendering requires a trusted runtime Registry")
    validation = validate(text, registry, source=source)
    if not validation.valid or validation.document is None:
        raise PipelineError(
            "Specification validation failed",
            validation.diagnostics,
            code="validation_failed",
        )
    warnings = tuple(
        item for item in validation.diagnostics if item.severity == "warning"
    )
    try:
        return _render_validated(
            validation,
            registry,
            representation,
            renderer,
            destination,
            source,
            warnings,
        )
    except PipelineError as exc:
        exc.warnings = warnings
        raise


def _render_validated(
    validation: ValidationResult,
    registry: Registry,
    representation: str,
    renderer: str,
    destination: Path,
    source: str,
    warnings: tuple[Diagnostic, ...],
) -> RenderResult:
    assert validation.document is not None
    output = validation.document.output
    try:
        registry.handler("representations", representation, output=output)
        registry.handler("renderers", renderer, output=output)
    except RegistrationError as exc:
        raise PipelineError(
            f"Capability selection failed for {output!r}: {exc}",
            code="capability_selection_failed",
        ) from exc
    content = _materialize(validation, registry, source)
    composition = compose(
        content, output=output, representation=representation, registry=registry
    )
    data, media_type, editable, limitations = _invoke_renderer(
        registry, renderer, composition
    )
    try:
        spans, provenance_status = _composition_provenance(composition)
    except Exception as exc:
        raise PipelineError(
            f"Composition provenance failed: {exc}",
            code="representation_failed",
            limitations=limitations,
        ) from exc
    try:
        _write_atomically(destination, data)
    except Exception as exc:
        raise PipelineError(
            f"Artifact write failed: {exc}",
            code="output_write_failed",
            limitations=limitations,
        ) from exc
    return RenderResult(
        Artifact(destination, media_type, editable),
        output,
        representation,
        renderer,
        warnings,
        limitations,
        spans,
        provenance_status=provenance_status,
    )


def _invoke_renderer(
    registry: Registry, renderer: str, composition: Composition
) -> tuple[bytes, str, bool, tuple[str, ...]]:
    context = RendererBuilder(composition)
    try:
        registry.handler("renderers", renderer, output=composition.output)(context)
        if context.artifact is None:
            raise ValueError("renderer must emit exactly one artifact")
        data, media_type, editable = context.artifact
    except Exception as exc:
        raise PipelineError(
            f"Renderer {renderer!r} failed for {composition.output!r}: {exc}",
            code="renderer_failed",
            limitations=(*composition.limitations, *context.limitations),
        ) from exc
    return data, media_type, editable, (*composition.limitations, *context.limitations)
