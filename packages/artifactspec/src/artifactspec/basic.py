"""An explicitly registered basic content plugin and static SVG renderer."""

import re
from html import escape

from artifactspec.contexts import (
    PhraseContext,
    PropertyContext,
    RendererContext,
    RepresentationContext,
)
from artifactspec.models import RectangleElement, TextElement
from artifactspec.plugins import Plugin


def _xml(value: str) -> str:
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


def _color(value: str) -> str:
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


def _svg(context: RendererContext) -> None:
    composition = context.composition
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{composition.width}" height="{composition.height}" viewBox="0 0 {composition.width} {composition.height}">'
    ]
    for item in composition.elements:
        if isinstance(item, TextElement):
            parts.append(
                f'<text x="{item.x}" y="{item.y}" font-size="{item.size}" fill="{_color(item.color)}">{_xml(item.text)}</text>'
            )
        elif isinstance(item, RectangleElement):
            parts.append(
                f'<rect x="{item.x}" y="{item.y}" width="{item.width}" height="{item.height}" fill="{_color(item.color)}"/>'
            )
        else:
            raise TypeError(f"unsupported visual element {type(item).__name__}")
    parts.append("</svg>")
    context.emit(
        "\n".join(parts).encode("utf-8"), media_type="image/svg+xml", editable=True
    )


def basic_plugin() -> Plugin:
    """Return a new trusted plugin for simple image/report content."""
    plugin = Plugin("builtin-basic", "1", outputs=("image", "report"), schema_version=2)

    @plugin.phrase("text", object_type="text")
    def make_text(context: PhraseContext) -> None:
        context.create("text")

    @plugin.phrase("rectangle", object_type="rectangle")
    def make_rectangle(context: PhraseContext) -> None:
        context.create("rectangle")

    @plugin.property("value", target_types=("text",))
    def value(context: PropertyContext) -> None:
        context.set("value", context.value)

    @plugin.property("color", target_types=("text", "rectangle"))
    def color(context: PropertyContext) -> None:
        context.set("color", context.value)

    @plugin.representation("basic", outputs=("image", "report"))
    def represent(context: RepresentationContext) -> None:
        context.warn(
            "Basic layout uses a fixed canvas and does not wrap or measure text; inspect for clipping and font differences."
        )
        for index, node in enumerate(context.content.nodes):
            properties = dict(node.properties)
            allowed = {"value", "color"} if node.object_type == "text" else {"color"}
            unsupported = sorted(set(properties) - allowed)
            if unsupported:
                raise ValueError(
                    f"basic representation cannot express properties {unsupported!r}"
                )
            y = 40 + 70 * index
            if y + 40 > 480:
                raise ValueError("basic layout exceeds the fixed canvas height")
            if node.object_type == "text":
                context.text(
                    node.name,
                    properties.get("value", ""),
                    x=20,
                    y=y,
                    color=properties.get("color", "black"),
                )
            elif node.object_type == "rectangle":
                if context.output == "image":
                    context.rectangle(
                        node.name,
                        x=20,
                        y=y,
                        width=120,
                        height=40,
                        color=properties.get("color", "black"),
                    )
                else:
                    context.text(
                        node.name,
                        f"Rectangle (color: {properties.get('color', 'black')})",
                        x=20,
                        y=y,
                    )
            else:
                raise ValueError(
                    f"basic representation cannot express {node.object_type!r}"
                )

    plugin.renderer("svg", outputs=("image",))(_svg)
    return plugin
