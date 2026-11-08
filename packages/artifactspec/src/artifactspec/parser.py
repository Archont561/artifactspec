"""Strict, source-linked parsing without executing plugin handlers."""

from __future__ import annotations

import json
from typing import cast

from lark import Lark, Token, Tree
from lark.exceptions import UnexpectedInput

from artifactspec._lines import source_lines
from artifactspec.plugins import CapabilityCatalog
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

# No whitespace is ignored: separators and capability word spacing are literal.
# Earley allows grammar words such as "named" and "of" inside capability names.
_GRAMMAR = r"""
header: "Output " IDENT "."
create: "Create " capability " named " IDENT "."
set: "Set " capability " of " IDENT " to " JSON_STRING "."
capability: WORD (" " WORD)*
IDENT: /[A-Za-z][A-Za-z0-9_-]*/
WORD: /[A-Za-z0-9_-]+/
JSON_STRING: /"(?:[^"\\]|\\.)*"/
"""
_PARSER = Lark(
    _GRAMMAR,
    parser="earley",
    lexer="dynamic",
    ambiguity="explicit",
    propagate_positions=True,
    start=["header", "create", "set"],
)
_SET_PREFIX = "Set "


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


def _parse_line(
    line: str, start: str, span: SourceSpan, code: str, message: str
) -> Tree:
    try:
        tree = _PARSER.parse(line, start=start)
    except UnexpectedInput as error:
        raise ParseError(code, message, span) from error
    if tree.data == "_ambig" or any(tree.find_data("_ambig")):
        raise ParseError(
            "ambiguous_statement", "Statement has multiple interpretations", span
        )
    return tree


def _token_span(token: Token, span: SourceSpan) -> SourceSpan:
    assert token.start_pos is not None and token.end_pos is not None
    offset = span.start.column - 1
    return _span(
        span.source, span.start.line, offset + token.start_pos, offset + token.end_pos
    )


def _capability(tree: Tree) -> str:
    return " ".join(str(word) for word in tree.children)


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
    message = 'Expected Set <property> of <reference> to "<string>".'
    tree = _parse_line(line, "set", span, "malformed_statement", message)
    capability, reference, literal = tree.children
    name = _capability(cast(Tree, capability))
    reference = cast(Token, reference)
    literal = cast(Token, literal)
    try:
        value = json.loads(str(literal))
    except (ValueError, RecursionError) as error:
        raise ParseError("malformed_statement", message, span) from error
    if name not in properties:
        raise ParseError(
            "unknown_property",
            f"Property {name!r} is not registered for output {output!r}",
            span,
        )
    return SetStatement(
        name,
        Reference(str(reference), _token_span(reference, span)),
        StringValue(value, _token_span(literal, span)),
        span,
    )


def _parse_output(line: str, span: SourceSpan, outputs: set[str]) -> str:
    tree = _parse_line(
        line, "header", span, "missing_output", "First statement must be Output <name>."
    )
    output = str(tree.children[0])
    if output not in outputs:
        raise ParseError("unknown_output", f"Output {output!r} is not registered", span)
    return output


def _create_statement(
    line: str, span: SourceSpan, phrases: set[str], output: str
) -> CreateStatement:
    message = "Expected Create <phrase> named <object>."
    tree = _parse_line(line, "create", span, "malformed_statement", message)
    capability, identifier = tree.children
    phrase = _capability(cast(Tree, capability))
    name = str(identifier)
    if name == "it":
        raise ParseError("malformed_statement", message, span)
    if phrase not in phrases:
        raise ParseError(
            "unknown_phrase",
            f"Phrase {phrase!r} is not registered for output {output!r}",
            span,
        )
    return CreateStatement(phrase, name, span)


def _available_capabilities(
    registry: CapabilityCatalog, output: str
) -> tuple[set[str], set[str]]:
    """Collect phrase and property names compatible with an output."""
    manifests = registry.manifests(output=output)
    phrases = {item["name"] for manifest in manifests for item in manifest["phrases"]}
    properties = {
        item["name"] for manifest in manifests for item in manifest["properties"]
    }
    return phrases, properties


def parse(
    text: str, registry: CapabilityCatalog, *, source: str = "<memory>"
) -> Document:
    """Parse one document; no partial result is returned on an error."""
    manifests = registry.manifests()
    outputs = {output for manifest in manifests for output in manifest["outputs"]}
    output: str | None = None
    output_span: SourceSpan | None = None
    last_span: SourceSpan | None = None
    phrases: set[str] = set()
    properties: set[str] = set()
    statements: list[Statement] = []
    for line_number, raw in enumerate(source_lines(text), start=1):
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
