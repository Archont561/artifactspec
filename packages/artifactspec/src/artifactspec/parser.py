"""Strict, source-linked parsing without executing plugin handlers."""

from __future__ import annotations

import json
import re

from artifactspec.plugins import Registry
from artifactspec.syntax import (
    CreateStatement,
    Document,
    Position,
    Reference,
    SetStatement,
    SourceSpan,
    Statement,
    StringValue,
)

_SET_PREFIX = "Set "
_IDENTIFIER = r"[A-Za-z][A-Za-z0-9_-]*"
_CAPABILITY = re.compile(r"[A-Za-z0-9_-]+(?: [A-Za-z0-9_-]+)*")
_OUTPUT = re.compile(rf"Output ({_IDENTIFIER})\.")
_CREATE = re.compile(rf"Create (.+) named ({_IDENTIFIER})\.")
_SEPARATOR = re.compile(rf" of ({_IDENTIFIER}) to ")


class ParseError(ValueError):
    """A single source-linked syntax or capability diagnostic."""

    def __init__(self, code: str, message: str, span: SourceSpan) -> None:
        self.code = code
        self.message = message
        self.span = span
        super().__init__(
            f"{span.source}:{span.start.line}:{span.start.column}: {message}"
        )


def _span(source: str, line: int, start: int, end: int) -> SourceSpan:
    return SourceSpan(source, Position(line, start + 1), Position(line, end + 1))


def _set_candidates(body: str) -> list[tuple[str, re.Match[str], str]]:
    """Find syntactically valid property, reference and literal combinations."""
    candidates: list[tuple[str, re.Match[str], str]] = []
    for separator in _SEPARATOR.finditer(body):
        name = body[: separator.start()]
        literal = body[separator.end() :]
        if (
            not _CAPABILITY.fullmatch(name)
            or not literal.startswith('"')
            or not literal.endswith('"')
        ):
            continue
        try:
            value = json.loads(literal)
        except (ValueError, RecursionError):
            continue
        if not isinstance(value, str):
            continue
        candidates.append((name, separator, value))
    return candidates


def _set_statement(
    line: str,
    span: SourceSpan,
    properties: set[str],
    output: str,
) -> SetStatement:
    if not line.endswith("."):
        raise ParseError(
            "malformed_statement", "Set statements must end with a period", span
        )
    candidates = _set_candidates(line[len(_SET_PREFIX) : -1])
    if not candidates:
        raise ParseError(
            "malformed_statement",
            'Expected Set <property> of <reference> to "<string>".',
            span,
        )
    if len(candidates) != 1:
        raise ParseError(
            "ambiguous_statement", "Set statement has multiple interpretations", span
        )
    name, separator, value = candidates[0]
    if name not in properties:
        raise ParseError(
            "unknown_property",
            f"Property {name!r} is not registered for output {output!r}",
            span,
        )
    offset = span.start.column - 1
    body_start = offset + len(_SET_PREFIX)
    ref_span = _span(
        span.source,
        span.start.line,
        body_start + separator.start(1),
        body_start + separator.end(1),
    )
    value_span = _span(
        span.source,
        span.start.line,
        body_start + separator.end(),
        offset + len(line) - 1,
    )
    return SetStatement(
        name,
        Reference(separator.group(1), ref_span),
        StringValue(value, value_span),
        span,
    )


def _parse_output(line: str, span: SourceSpan, outputs: set[str]) -> str:
    match = _OUTPUT.fullmatch(line)
    if match is None:
        raise ParseError(
            "missing_output", "First statement must be Output <name>.", span
        )
    output = match.group(1)
    if output not in outputs:
        raise ParseError("unknown_output", f"Output {output!r} is not registered", span)
    return output


def _create_statement(
    line: str, span: SourceSpan, phrases: set[str], output: str
) -> CreateStatement:
    match = _CREATE.fullmatch(line)
    if (
        match is None
        or match.group(2) == "it"
        or not _CAPABILITY.fullmatch(match.group(1))
    ):
        raise ParseError(
            "malformed_statement", "Expected Create <phrase> named <object>.", span
        )
    phrase, name = match.groups()
    if phrase not in phrases:
        raise ParseError(
            "unknown_phrase",
            f"Phrase {phrase!r} is not registered for output {output!r}",
            span,
        )
    return CreateStatement(phrase, name, span)


def _available_capabilities(
    registry: Registry, output: str
) -> tuple[set[str], set[str]]:
    """Collect phrase and property names compatible with an output."""
    manifests = registry.manifests(output=output)
    phrases = {item["name"] for manifest in manifests for item in manifest["phrases"]}
    properties = {
        item["name"] for manifest in manifests for item in manifest["properties"]
    }
    return phrases, properties


def parse(text: str, registry: Registry, *, source: str = "<memory>") -> Document:
    """Parse one document; no partial result is returned on an error."""
    manifests = registry.manifests()
    outputs = {output for manifest in manifests for output in manifest["outputs"]}
    output: str | None = None
    output_span: SourceSpan | None = None
    last_span: SourceSpan | None = None
    phrases: set[str] = set()
    properties: set[str] = set()
    statements: list[Statement] = []
    for line_number, raw in enumerate(text.split("\n"), start=1):
        line = raw.strip()
        if not line:
            continue
        offset = len(raw) - len(raw.lstrip())
        span = _span(source, line_number, offset, offset + len(line))
        last_span = span
        if output is None:
            output = _parse_output(line, span, outputs)
            output_span = span
            phrases, properties = _available_capabilities(registry, output)
            continue
        if line.startswith("Output "):
            raise ParseError(
                "ambiguous_output",
                "Only one output header is allowed per document",
                span,
            )
        if line.startswith("Create "):
            statements.append(_create_statement(line, span, phrases, output))
        elif line.startswith(_SET_PREFIX):
            statements.append(_set_statement(line, span, properties, output))
        else:
            raise ParseError(
                "unknown_statement", "Unknown statement; expected Create or Set", span
            )
    if output is None or output_span is None or last_span is None:
        span = _span(source, 1, 0, 0)
        raise ParseError(
            "missing_output", "First statement must be Output <name>.", span
        )
    return Document(
        output,
        output_span,
        tuple(statements),
        SourceSpan(source, output_span.start, last_span.end),
    )
