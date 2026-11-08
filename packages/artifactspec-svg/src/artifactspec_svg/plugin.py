"""SVG-specific language and diagram contributions."""

from artifactspec.core.contexts import (
    PhraseContext,
    PropertyContext,
    RepresentationContext,
)
from artifactspec_svg import renderer as _renderer  # noqa: F401
from artifactspec_svg.registration import plugin


@plugin.phrase("text", object_type="text", syntax="Create text named {name}.")
def create_text(context: PhraseContext) -> None:
    context.create("text")


@plugin.phrase(
    "rectangle", object_type="rectangle", syntax="Create rectangle named {name}."
)
def create_rectangle(context: PhraseContext) -> None:
    context.create("rectangle")


@plugin.property(
    "value", target_types=("text",), syntax="Set value of {reference} to {value}."
)
def text_value(context: PropertyContext) -> None:
    context.set("value", context.value)


@plugin.property(
    "color",
    target_types=("text", "rectangle"),
    syntax="Set color of {reference} to {value}.",
)
def color(context: PropertyContext) -> None:
    context.set("color", context.value)


@plugin.representation("diagram", target_types=("text", "rectangle"))
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
        context.text(
            node.name,
            properties.get("value", ""),
            x=20,
            y=y,
            color=properties.get("color", "black"),
        )
    else:
        context.rectangle(
            node.name,
            x=20,
            y=y,
            width=120,
            height=40,
            color=properties.get("color", "black"),
        )
