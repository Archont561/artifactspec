"""Strict source-linked parsing using static plugin-defined syntax."""

from artifactspec.core.syntax import Document, Position, SourceSpan
from artifactspec.plugins import CapabilityCatalog


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


def parse(
    text: str, registry: CapabilityCatalog, *, source: str = "<memory>"
) -> Document:
    """Parse one document using only the catalog's declarative templates."""
    from artifactspec.core.template_parser import parse_templates

    return parse_templates(text, registry, source)
