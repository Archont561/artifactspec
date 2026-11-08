"""Materialize validated syntax through explicitly trusted plugin handlers."""

from artifactspec.core._contexts import PhraseBuilder, PropertyBuilder
from artifactspec.core.models import Content, ContentNode
from artifactspec.core.syntax import CreateStatement, Document, SetStatement
from artifactspec.core.validation import Diagnostic, ValidationResult, validate
from artifactspec.plugins import Registry


class PipelineError(ValueError):
    """A specification or trusted plugin failed to produce semantic content."""

    def __init__(
        self,
        message: str,
        diagnostics: tuple[Diagnostic, ...] = (),
        *,
        code: str = "pipeline_failed",
        limitations: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics
        self.code = code
        self.warnings = tuple(
            item for item in diagnostics if item.severity == "warning"
        )
        self.limitations = limitations


def build_content(
    text: str, registry: Registry, *, source: str = "<memory>"
) -> Content:
    """Validate first, then run only the handlers already trusted by the caller."""
    if not isinstance(registry, Registry):
        raise TypeError("materialization requires a trusted runtime Registry")
    return _materialize(validate(text, registry, source=source), registry, source)


def _materialize(result: ValidationResult, registry: Registry, source: str) -> Content:
    """Execute handlers only for the supplied successful validation result."""
    if not result.valid or result.document is None:
        raise PipelineError(
            "Specification validation failed",
            result.diagnostics,
            code="validation_failed",
        )
    document = result.document
    nodes = _create_nodes(document, registry, source)
    _apply_properties(result, registry, source, nodes)
    return Content(tuple(nodes.values()))


def _create_nodes(
    document: Document, registry: Registry, source: str
) -> dict[str, ContentNode]:
    declared = {
        item["name"]: item.get("object_type")
        for manifest in registry.manifests(output=document.output)
        for item in manifest["phrases"]
    }
    nodes: dict[str, ContentNode] = {}
    for statement in document.statements:
        if not isinstance(statement, CreateStatement):
            continue
        context = PhraseBuilder(statement.name, statement.span)
        try:
            registry.handler("phrases", statement.phrase, output=document.output)(
                context
            )
            if context.object_type is None:
                raise ValueError("phrase must create exactly one object")
            object_type = context.object_type
            if (
                declared[statement.phrase] is not None
                and declared[statement.phrase] != object_type
            ):
                raise ValueError("created type does not match declared object_type")
        except Exception as exc:
            raise PipelineError(
                f"Phrase {statement.phrase!r} failed at {source}:{statement.span.start.line}: {exc}",
                code="phrase_failed",
            ) from exc
        nodes[statement.name] = ContentNode(
            statement.name, object_type, (), (statement.span,)
        )
    return nodes


def _apply_properties(
    result: ValidationResult,
    registry: Registry,
    source: str,
    nodes: dict[str, ContentNode],
) -> None:
    assert result.document is not None
    targets = {
        resolution.reference: resolution.target.name
        for resolution in result.resolutions
    }
    for statement in result.document.statements:
        if not isinstance(statement, SetStatement):
            continue
        name = targets[statement.reference]
        node = nodes[name]
        context = PropertyBuilder(node, statement.value.value, statement.span)
        try:
            registry.handler(
                "properties", statement.property, output=result.document.output
            )(context)
            if context.changes == 0:
                raise ValueError("property handler must set at least one property")
        except Exception as exc:
            raise PipelineError(
                f"Property {statement.property!r} failed at {source}:{statement.span.start.line}: {exc}",
                code="property_failed",
            ) from exc
        nodes[name] = ContentNode(
            node.name,
            node.object_type,
            tuple(context.properties.items()),
            (*node.provenance, statement.span),
        )
