"""Event plugin metadata and semantic validation."""

import pytest
from artifactspec_events.plugin import plugin

from artifactspec.core.pipeline import PipelineError, build_content
from artifactspec.core.rendering import compose
from artifactspec.plugins import Registry
from artifactspec.plugins.discovery import installed_plugins


def registry():
    result = Registry()
    result.register(plugin)
    return result


def test_installed_metadata_matches_plugin():
    assert installed_plugins(only={"events"})["events"] is plugin
    assert plugin.to_dict()["version"] == "0.1.0"


def test_event_content_can_be_composed_without_svg():
    content = build_content(
        'Output report.\nCreate event named e.\nSet date of e to "2024-02-29".\nSet label of e to "Leap day".',
        registry(),
    )
    composition = compose(
        content, output="report", representation="diagram", registry=registry()
    )
    assert composition.elements[0].value.text == "2024-02-29: Leap day"
    assert not hasattr(composition, "playback")


@pytest.mark.parametrize(
    "value", ["", "2024-2-01", "2024-02-30", "1900-02-29", "2020-01-01T00:00:00"]
)
def test_invalid_dates_fail(value):
    import json

    source = (
        f"Output image.\nCreate event named e.\nSet date of e to {json.dumps(value)}."
    )
    with pytest.raises(PipelineError, match="valid ISO calendar date"):
        build_content(source, registry())


@pytest.mark.parametrize("value", ["", "  ", "\t\n"])
def test_blank_event_labels_fail(value):
    import json

    source = (
        f"Output image.\nCreate event named e.\nSet label of e to {json.dumps(value)}."
    )
    with pytest.raises(PipelineError, match="event label must not be empty"):
        build_content(source, registry())
