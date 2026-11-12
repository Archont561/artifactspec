"""Parse statements from declarative plugin-owned templates."""

import json
import re
from dataclasses import dataclass
from typing import Any

from artifactspec.core._lines import source_lines
from artifactspec.core.parser import ParseError
from artifactspec.core.syntax import (
    CreateStatement,
    Document,
    Position,
    Reference,
    SetStatement,
    SourceSpan,
    Statement,
    StringValue,
)
from artifactspec.core.templates import compile_template
from artifactspec.plugins import CapabilityCatalog


@dataclass(frozen=True)
class _Pattern:
    kind: str
    name: str
    pattern: re.Pattern[str]


def _patterns(manifests: list[dict[str, Any]], output: str | None) -> list[_Pattern]:
    result = []
    output_patterns: set[tuple[str, str]] = set()
    for manifest in manifests:
        for name, template in manifest["output_syntax"].items():
            output_patterns.add((name, template))
        if output is None:
            continue
        for kind, fields in (
            ("phrases", {"name"}),
            ("properties", {"reference", "value"}),
        ):
            for item in manifest[kind]:
                result.append(
                    _Pattern(
                        kind, item["name"], compile_template(item["syntax"], fields)
                    )
                )
    result.extend(
        _Pattern("output", name, compile_template(template, set()))
        for name, template in sorted(output_patterns)
    )
    return result


def _span(source: str, line: int, start: int, end: int) -> SourceSpan:
    return SourceSpan(source, Position(line, start + 1), Position(line, end + 1))


def _field_span(match: re.Match[str], name: str, span: SourceSpan) -> SourceSpan:
    offset = span.start.column - 1
    return _span(
        span.source,
        span.start.line,
        offset + match.start(name),
        offset + match.end(name),
    )


def _statement(pattern: _Pattern, match: re.Match[str], span: SourceSpan) -> Statement:
    if pattern.kind == "phrases":
        name = match.group("name")
        if name == "it":
            raise ParseError("malformed_statement", "The name 'it' is reserved", span)
        return CreateStatement(pattern.name, name, span)
    try:
        value = json.loads(match.group("value"))
    except (ValueError, RecursionError) as error:
        raise ParseError(
            "malformed_statement", "Invalid string literal", span
        ) from error
    return SetStatement(
        pattern.name,
        Reference(match.group("reference"), _field_span(match, "reference", span)),
        StringValue(value, _field_span(match, "value", span)),
        span,
    )


def _line_span(raw: str, source: str, line_number: int) -> SourceSpan:
    offset = len(raw) - len(raw.lstrip())
    return _span(source, line_number, offset, offset + len(raw.strip()))


def _match_line(
    line: str, patterns: list[_Pattern], span: SourceSpan, *, output: str | None
) -> tuple[_Pattern, re.Match[str]]:
    candidates = [
        (pattern, match)
        for pattern in patterns
        if (match := pattern.pattern.fullmatch(line)) is not None
    ]
    if not candidates:
        code = "unknown_output" if output is None else "unknown_statement"
        raise ParseError(code, "No plugin syntax matches this statement", span)
    if len(candidates) > 1:
        raise ParseError(
            "ambiguous_statement", "Statement matches multiple plugin templates", span
        )
    return candidates[0]


def parse_templates(text: str, catalog: CapabilityCatalog, source: str) -> Document:
    headers = _patterns(catalog.manifests(), None)
    patterns: list[_Pattern] = []
    output: str | None = None
    first: SourceSpan | None = None
    last: SourceSpan | None = None
    statements: list[Statement] = []
    for line_number, raw in enumerate(source_lines(text), start=1):
        line = raw.strip()
        if not line:
            continue
        span = _line_span(raw, source, line_number)
        last = span
        pattern, match = _match_line(
            line, headers if output is None else patterns, span, output=output
        )
        if output is None:
            output = pattern.name
            first = span
            patterns = [
                item
                for item in _patterns(catalog.manifests(output=output), output)
                if item.kind != "output"
            ] + headers
        elif pattern.kind == "output":
            raise ParseError(
                "ambiguous_output", "Only one output declaration is allowed", span
            )
        else:
            statements.append(_statement(pattern, match, span))
    if output is None or first is None or last is None:
        raise ParseError(
            "missing_output",
            "An output declaration is required",
            _span(source, 1, 0, 0),
        )
    return Document(
        output, first, tuple(statements), SourceSpan(source, first.start, last.end)
    )
