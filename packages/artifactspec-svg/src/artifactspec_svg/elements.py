"""SVG-owned, string-renderable visual elements."""

import math
from dataclasses import dataclass
from typing import ClassVar

from artifactspec_svg.syntax import svg_color, xml_text


def _numbers(*values: float) -> None:
    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in values
    ):
        raise ValueError("coordinates and dimensions must be finite numbers")


@dataclass(frozen=True, slots=True)
class Text:
    x: float
    y: float
    text: str
    color: str = "black"
    size: float = 20
    media_type: ClassVar[str] = "image/svg+xml"

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        _numbers(self.x, self.y, self.size)
        if self.size <= 0:
            raise ValueError("text size must be positive")

    def __str__(self) -> str:
        return f'<text x="{self.x}" y="{self.y}" font-size="{self.size}" fill="{svg_color(self.color)}">{xml_text(self.text)}</text>'


@dataclass(frozen=True, slots=True)
class Rectangle:
    x: float
    y: float
    width: float
    height: float
    color: str = "black"
    media_type: ClassVar[str] = "image/svg+xml"

    def __post_init__(self) -> None:
        _numbers(self.x, self.y, self.width, self.height)
        if self.width <= 0 or self.height <= 0:
            raise ValueError("rectangle dimensions must be positive")

    def __str__(self) -> str:
        return f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" fill="{svg_color(self.color)}"/>'
