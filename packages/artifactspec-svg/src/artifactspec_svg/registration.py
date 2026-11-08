"""SVG plugin declaration shared by its independently organized handlers."""

from artifactspec.plugin import Phrase, Plugin, Property, Renderer, Representation

plugin = Plugin(
    "svg",
    outputs={"image": "Output image."},
    phrases=(
        Phrase("text", "text", "Create text named {name}."),
        Phrase("rectangle", "rectangle", "Create rectangle named {name}."),
    ),
    properties=(
        Property("value", ("text",), "Set value of {reference} to {value}."),
        Property(
            "color", ("text", "rectangle"), "Set color of {reference} to {value}."
        ),
    ),
    representations=(Representation("diagram", ("text", "rectangle")),),
    renderers=(Renderer("svg", ("image",)),),
)
