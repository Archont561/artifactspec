"""Adapt an ArtifactSpec composition into an SVG artifact."""

from artifactspec.core.contexts import RendererContext
from artifactspec_svg.syntax import serialize_svg


def render_svg(context: RendererContext) -> None:
    context.emit(
        serialize_svg(context.composition), media_type="image/svg+xml", editable=True
    )
