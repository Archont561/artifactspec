"""SVG-specific language and diagram contributions."""

from artifactspec.core.contexts import (
    PhraseContext,
    PropertyContext,
    RepresentationContext,
)
from artifactspec_svg import renderer as _renderer  # noqa: F401
from artifactspec_svg.elements import Rectangle, Text
from artifactspec_svg.registration import plugin


@plugin.phrase("text")
def create_text(context: PhraseContext) -> None:
    context.create("text")


@plugin.phrase("rectangle")
def create_rectangle(context: PhraseContext) -> None:
    context.create("rectangle")


@plugin.property("value")
def text_value(context: PropertyContext) -> None:
    context.set("value", context.value)


@plugin.property("color")
def color(context: PropertyContext) -> None:
    context.set("color", context.value)


@plugin.representation("diagram")
def diagram(context: RepresentationContext) -> None:
    node = context.node
    properties = dict(node.properties)
    allowed = {"value", "color"} if node.object_type == "text" else {"color"}
    unsupported = sorted(set(properties) - allowed)
    if unsupported:
        raise ValueError(f"SVG diagram cannot express properties {unsupported!r}")
    y = 40 + 70 * context.index
    if y + 40 > 480:
        raise ValueError("diagram exceeds the fixed canvas height")
    context.warn(
        "Diagram uses a fixed canvas and does not wrap or measure text; inspect for clipping and font differences."
    )
    if node.object_type == "text":
        context.add(
            node.name,
            Text(20, y, properties.get("value", ""), properties.get("color", "black")),
        )
    else:
        context.add(
            node.name, Rectangle(20, y, 120, 40, properties.get("color", "black"))
        )
