"""SVG-specific XML escaping and color syntax."""

import re
from html import escape

from artifactspec.core.models import Composition


def xml_text(value: str) -> str:
    if any(
        not (
            char in "\t\n\r"
            or 0x20 <= ord(char) <= 0xD7FF
            or 0xE000 <= ord(char) <= 0xFFFD
            or 0x10000 <= ord(char) <= 0x10FFFF
        )
        for char in value
    ):
        raise ValueError("text contains a character forbidden by XML 1.0")
    return escape(value, quote=True).replace("\r", "&#13;")


def svg_color(value: str) -> str:
    names = {
        "black",
        "white",
        "red",
        "green",
        "blue",
        "yellow",
        "navy",
        "gray",
        "grey",
        "orange",
        "purple",
        "cyan",
        "magenta",
        "transparent",
    }
    if value.lower() not in names and not re.fullmatch(
        r"(?:#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8})", value
    ):
        raise ValueError(f"unsupported SVG color {value!r}")
    return value


def serialize_svg(composition: Composition) -> bytes:
    """Encode a static composition as a complete SVG document."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{composition.width}" height="{composition.height}" viewBox="0 0 {composition.width} {composition.height}">'
    ]
    for item in composition.elements:
        value = item.value
        if (
            getattr(value, "media_type", None) != "image/svg+xml"
            or type(value).__str__ is object.__str__
        ):
            raise TypeError(f"unsupported visual element {type(value).__name__}")
        parts.append(str(value))
    parts.append("</svg>")
    return "\n".join(parts).encode("utf-8")
