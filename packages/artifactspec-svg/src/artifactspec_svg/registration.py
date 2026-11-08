"""SVG plugin declaration shared by its independently organized handlers."""

from artifactspec.plugins import Plugin

plugin = Plugin(
    "svg",
    "0.1.0",
    outputs=("image",),
    schema_version=3,
    output_syntax={"image": "Output image."},
)
