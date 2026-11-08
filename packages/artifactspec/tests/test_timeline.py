"""Calendar events are semantic content, not playback schedules."""

import json
from datetime import date
from xml.etree import ElementTree

import pytest
from artifactspec_events.plugin import plugin as event_plugin
from hypothesis import given
from hypothesis import strategies as st
from typer.testing import CliRunner

from artifactspec.cli import app
from artifactspec.core.models import Content, ContentNode
from artifactspec.core.pipeline import PipelineError, build_content
from artifactspec.core.rendering import compose
from artifactspec.plugins import Registry


def registry():
    result = Registry()
    result.register(event_plugin)
    return result


def specification(event_date, label):
    return (
        "Output image.\nCreate event named item.\n"
        f"Set date of item to {json.dumps(event_date)}.\n"
        f"Set label of item to {json.dumps(label)}."
    )


@given(st.dates(min_value=date(1, 1, 1), max_value=date(9999, 12, 31)))
def test_calendar_date_is_preserved_as_content_not_playback(event_date):
    registry_ = registry()
    text = event_date.isoformat()
    content = build_content(specification(text, "Event"), registry_)
    assert dict(content.nodes[0].properties)["date"] == text
    for output, separator in (("image", " — "), ("report", ": ")):
        layout = compose(
            content, output=output, representation="diagram", registry=registry_
        )
        assert layout.elements[0].value.text == f"{text}{separator}Event"
        assert layout.elements[0].value.y == 40
        assert not hasattr(layout, "playback")


@pytest.mark.parametrize(
    "value",
    [
        "",
        "2024-2-01",
        "2024-02-30",
        "1900-02-29",
        "0000-01-01",
        "2020-01-01T00:00:00",
        "２０２０-01-01",
        " 2024-01-01",
    ],
)
def test_invalid_dates_are_rejected_during_materialization(value):
    with pytest.raises(PipelineError, match="valid ISO calendar date") as error:
        build_content(specification(value, "Event"), registry(), source="scene.art")
    assert "scene.art:3" in str(error.value)


@pytest.mark.parametrize("value", ["", "  ", "\t\n"])
def test_empty_event_labels_are_rejected(value):
    with pytest.raises(PipelineError, match="event label must not be empty"):
        build_content(specification("2000-01-01", value), registry())


@pytest.mark.parametrize(
    "properties", [(), (("date", "2001-01-01"),), (("value", "Event"),)]
)
def test_missing_event_fields_fail_composition(properties):
    content = Content((ContentNode("event", "event", properties, ()),))
    with pytest.raises(PipelineError, match="requires date and label"):
        compose(content, output="image", representation="diagram", registry=registry())


@pytest.mark.parametrize(
    "date_value,label", [("2023-02-29", "Event"), ("2000-01-01", " ")]
)
def test_direct_semantic_content_cannot_bypass_event_checks(date_value, label):
    content = Content(
        (ContentNode("event", "event", (("date", date_value), ("value", label)), ()),)
    )
    with pytest.raises(PipelineError):
        compose(content, output="report", representation="diagram", registry=registry())


def test_cli_renders_event_and_retains_dates_and_provenance(tmp_path):
    source = tmp_path / "timeline.art"
    source.write_text(
        specification("1989-11-09", "Berlin Wall opens"), encoding="utf-8"
    )
    destination = tmp_path / "timeline.svg"
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(destination),
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert [span["start"]["line"] for span in data["provenance"]] == [2, 3, 4]
    assert (
        ElementTree.parse(destination)
        .getroot()
        .find("{http://www.w3.org/2000/svg}text")
        .text
        == "1989-11-09 — Berlin Wall opens"
    )


def test_missing_event_date_does_not_replace_existing_artifact(tmp_path):
    source = tmp_path / "timeline.art"
    source.write_text(
        'Output image.\nCreate event named item.\nSet label of item to "Event".',
        encoding="utf-8",
    )
    destination = tmp_path / "timeline.svg"
    destination.write_text("old", encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(destination),
        ],
    )
    assert result.exit_code == 2
    assert "requires date and label" in result.output
    assert destination.read_text(encoding="utf-8") == "old"


def test_static_validation_does_not_claim_to_check_calendar_values():
    from artifactspec.core.validation import validate
    from artifactspec.plugins import ManifestCatalog

    text = specification("2024-02-30", "Event")
    assert validate(text, ManifestCatalog([event_plugin.manifest()])).valid
    with pytest.raises(PipelineError, match="valid ISO calendar date"):
        build_content(text, registry())


def test_animation_output_is_not_inferred_from_event_dates():
    content = build_content(specification("2000-01-01", "Event"), registry())
    with pytest.raises(PipelineError, match="compatible with output 'animation'"):
        compose(
            content, output="animation", representation="diagram", registry=registry()
        )
