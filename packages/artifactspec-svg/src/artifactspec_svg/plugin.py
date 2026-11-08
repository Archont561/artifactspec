"""Register the optional SVG renderer with ArtifactSpec."""

from artifactspec.plugins import Plugin
from artifactspec_svg.renderer import render_svg

plugin = Plugin("svg", "0.1.0", outputs=("image",), schema_version=2)
plugin.renderer("svg", outputs=("image",))(render_svg)
