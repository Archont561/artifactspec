"""Explicit representation selection and atomic rendering through trusted plugins."""

import tempfile
from dataclasses import dataclass
from pathlib import Path

from artifactspec._contexts import RendererBuilder, RepresentationBuilder
from artifactspec.models import Composition, Content
from artifactspec.pipeline import PipelineError, _materialize
from artifactspec.plugins import RegistrationError, Registry
from artifactspec.syntax import SourceSpan
from artifactspec.validation import Diagnostic, validate


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


def compose(
    content: Content, *, output: str, representation: str, registry: Registry
) -> Composition:
    """Select one explicit, output-compatible representation without fallback."""
    if not isinstance(registry, Registry):
        raise TypeError("composition requires a trusted runtime Registry")
    context = RepresentationBuilder(content, output, representation)
    try:
        registry.handler("representations", representation, output=output)(context)
    except Exception as exc:
        raise PipelineError(
            f"Representation {representation!r} failed for {output!r}: {exc}"
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
        raise PipelineError("Specification validation failed", validation.diagnostics)
    output = validation.document.output
    try:
        registry.handler("representations", representation, output=output)
        registry.handler("renderers", renderer, output=output)
    except RegistrationError as exc:
        raise PipelineError(
            f"Capability selection failed for {output!r}: {exc}"
        ) from exc
    content = _materialize(validation, registry, source)
    composition = compose(
        content, output=output, representation=representation, registry=registry
    )
    context = RendererBuilder(composition)
    try:
        registry.handler("renderers", renderer, output=output)(context)
        if context.artifact is None:
            raise ValueError("renderer must emit exactly one artifact")
        data, media_type, editable = context.artifact
        _write_atomically(destination, data)
    except Exception as exc:
        raise PipelineError(
            f"Renderer {renderer!r} failed for {output!r}: {exc}"
        ) from exc
    spans = tuple(
        dict.fromkeys(span for item in composition.elements for span in item.provenance)
    )
    warnings = tuple(
        item for item in validation.diagnostics if item.severity == "warning"
    )
    return RenderResult(
        Artifact(destination, media_type, editable),
        output,
        representation,
        renderer,
        warnings,
        (*composition.limitations, *context.limitations),
        spans,
    )
