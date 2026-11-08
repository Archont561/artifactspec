"""Immutable source-level nodes for the initial controlled-language subset."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """One-based line and Unicode code-point column."""

    line: int
    column: int


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A source identifier and half-open source range."""

    source: str
    start: Position
    end: Position


@dataclass(frozen=True, slots=True)
class Reference:
    """An unresolved object name or the special reference 'it'."""

    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class StringValue:
    """A decoded JSON string and its source literal."""

    value: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class CreateStatement:
    """A registered phrase and a declared object name."""

    phrase: str
    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class SetStatement:
    """A registered property, unresolved reference, and string value."""

    property: str
    reference: Reference
    value: StringValue
    span: SourceSpan


Statement = CreateStatement | SetStatement


@dataclass(frozen=True, slots=True)
class Document:
    """Parsed statements, not yet semantically validated."""

    output: str
    output_span: SourceSpan
    statements: tuple[Statement, ...]
    span: SourceSpan
