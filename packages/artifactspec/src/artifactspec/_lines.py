"""Physical line boundaries shared by parsing and editor synchronization."""

import re


def source_lines(text: str) -> tuple[str, ...]:
    """Split on LSP line endings, preserving terminators and a final empty line."""
    lines = []
    start = 0
    for match in re.finditer(r"\r\n|\r|\n", text):
        lines.append(text[start : match.end()])
        start = match.end()
    lines.append(text[start:])
    return tuple(lines)
