"""Event-owned diagram elements, independent of renderer plugins."""

import math
from dataclasses import dataclass
from html import escape
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class EventText:
    x: float
    y: float
    text: str
    media_type: ClassVar[str] = "image/svg+xml"

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            for value in (self.x, self.y)
        ):
            raise ValueError("coordinates must be finite numbers")
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")

    def __str__(self) -> str:
        if any(
            not (
                char in "\t\n\r"
                or 0x20 <= ord(char) <= 0xD7FF
                or (0xE000 <= ord(char) <= 0xFFFD or 0x10000 <= ord(char) <= 0x10FFFF)
            )
            for char in self.text
        ):
            raise ValueError("text contains a character forbidden by XML 1.0")
        text = escape(self.text, quote=True).replace("\r", "&#13;")
        return (
            f'<text x="{self.x}" y="{self.y}" font-size="20" fill="black">{text}</text>'
        )


@dataclass(frozen=True, slots=True)
class ReportText:
    x: float
    y: float
    text: str
