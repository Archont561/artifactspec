"""Shared source-linked reference and static type validation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from artifactspec.core.parser import ParseError, parse
from artifactspec.core.syntax import (
    CreateStatement,
    Document,
    Reference,
    SetStatement,
    SourceSpan,
)
from artifactspec.plugins import CapabilityCatalog


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A source-linked validation finding."""

    code: str
    severity: Literal["error", "warning"]
    message: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ResolvedReference:
    """A property reference and its declared object."""

    reference: Reference
    target: CreateStatement


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Validation findings and any resolved references, not rendered output."""

    document: Document | None
    diagnostics: tuple[Diagnostic, ...]
    resolutions: tuple[ResolvedReference, ...]

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)


def _definitions(document: Document) -> dict[str, list[CreateStatement]]:
    definitions: dict[str, list[CreateStatement]] = defaultdict(list)
    for statement in document.statements:
        if isinstance(statement, CreateStatement):
            definitions[statement.name].append(statement)
    return definitions


def _resolve(
    reference: Reference,
    latest: CreateStatement | None,
    definitions: dict[str, list[CreateStatement]],
) -> tuple[CreateStatement | None, Diagnostic | None]:
    candidates = (
        ([latest] if latest is not None else [])
        if reference.name == "it"
        else definitions.get(reference.name, [])
    )
    if not candidates:
        message = (
            "Create an object before using 'it'."
            if reference.name == "it"
            else f"No object named {reference.name!r}; declare it in this document."
        )
        return None, Diagnostic(
            "unresolved_reference", "error", message, reference.span
        )
    if len(candidates) > 1:
        return None, Diagnostic(
            "ambiguous_reference",
            "error",
            f"Object {reference.name!r} has multiple declarations; use unique names.",
            reference.span,
        )
    return candidates[0], None


def _check_type(
    statement: SetStatement, object_type: str | None, accepted: list[str] | None
) -> Diagnostic | None:
    if object_type is None or accepted is None:
        return Diagnostic(
            "unverified_type",
            "warning",
            f"Cannot check property {statement.property!r}: plugin type metadata is missing.",
            statement.reference.span,
        )
    if object_type not in accepted:
        return Diagnostic(
            "wrong_type",
            "error",
            f"Property {statement.property!r} does not apply to {object_type!r}; expected {', '.join(accepted)}.",
            statement.reference.span,
        )
    return None


def _declaration_diagnostics(
    statement: CreateStatement,
    phrase_types: dict[str, str | None],
    definitions: dict[str, list[CreateStatement]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if phrase_types[statement.phrase] is None:
        diagnostics.append(
            Diagnostic(
                "unverified_type",
                "warning",
                f"Object {statement.name!r} has no declared type; plugin type metadata is missing.",
                statement.span,
            )
        )
    if len(definitions[statement.name]) > 1:
        diagnostics.append(
            Diagnostic(
                "duplicate_name",
                "error",
                f"Object {statement.name!r} is declared more than once; use unique names.",
                statement.span,
            )
        )
    return diagnostics


def _semantic_checks(
    document: Document, registry: CapabilityCatalog
) -> ValidationResult:
    manifests = registry.manifests(output=document.output)
    phrase_types = {
        item["name"]: item.get("object_type")
        for manifest in manifests
        for item in manifest["phrases"]
    }
    property_types = {
        item["name"]: item.get("target_types")
        for manifest in manifests
        for item in manifest["properties"]
    }
    definitions = _definitions(document)
    diagnostics: list[Diagnostic] = []
    resolutions: list[ResolvedReference] = []
    latest: CreateStatement | None = None
    for statement in document.statements:
        if isinstance(statement, CreateStatement):
            diagnostics.extend(
                _declaration_diagnostics(statement, phrase_types, definitions)
            )
            latest = statement
            continue
        target, error = _resolve(statement.reference, latest, definitions)
        if error is not None:
            diagnostics.append(error)
            continue
        assert target is not None
        resolutions.append(ResolvedReference(statement.reference, target))
        diagnostic = _check_type(
            statement, phrase_types[target.phrase], property_types[statement.property]
        )
        if diagnostic is not None:
            diagnostics.append(diagnostic)
    return ValidationResult(document, tuple(diagnostics), tuple(resolutions))


def validate(
    text: str, registry: CapabilityCatalog, *, source: str = "<memory>"
) -> ValidationResult:
    """Parse and validate without calling any plugin handler."""
    try:
        document = parse(text, registry, source=source)
    except ParseError as error:
        prefix = (
            f"{error.span.source}:{error.span.start.line}:{error.span.start.column}: "
        )
        return ValidationResult(
            None,
            (
                Diagnostic(
                    error.code, "error", str(error).removeprefix(prefix), error.span
                ),
            ),
            (),
        )
    return _semantic_checks(document, registry)
