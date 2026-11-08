"""Static built-in capabilities, independent of the executable plugin."""

from typing import Any

from artifactspec.plugins import validate_manifest


def basic_manifest() -> dict[str, Any]:
    """Return an independent static manifest without loading plugin handlers."""
    return validate_manifest(
        {
            "schema_version": 2,
            "id": "builtin-basic",
            "version": "1",
            "outputs": ["image", "report"],
            "phrases": [
                {"name": "text", "outputs": [], "object_type": "text"},
                {"name": "rectangle", "outputs": [], "object_type": "rectangle"},
                {"name": "event", "outputs": [], "object_type": "event"},
            ],
            "properties": [
                {"name": "value", "outputs": [], "target_types": ["text", "event"]},
                {"name": "date", "outputs": [], "target_types": ["event"]},
                {"name": "color", "outputs": [], "target_types": ["text", "rectangle"]},
            ],
            "representations": [{"name": "basic", "outputs": ["image", "report"]}],
            "renderers": [],
        }
    )
