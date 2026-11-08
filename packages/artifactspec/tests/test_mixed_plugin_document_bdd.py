"""End-to-end behavior of independently installed semantic plugins."""

from pathlib import Path
from xml.etree import ElementTree

import pytest
from pytest_bdd import given, scenarios, then, when
from typer.testing import CliRunner

from artifactspec.cli import app
from artifactspec.plugins import RegistrationError, validate_manifest

scenarios(
    str(
        Path(__file__).resolve().parents[1]
        / "features"
        / "mixed_plugin_document.feature"
    )
)


@pytest.fixture
def state():
    return {}


@given("the SVG and event plugins are installed")
def installed_plugins(state, tmp_path):
    state["source"] = tmp_path / "scene.art"
    state["output"] = tmp_path / "scene.svg"
    state["source"].write_text(
        'Output image.\nCreate rectangle named box.\nSet color of box to "navy".\n'
        'Create event named launch.\nSet date of launch to "2020-01-02".\n'
        'Set label of launch to "launch day".\n',
        encoding="utf-8",
    )


@when("I render a document containing a shape and a dated event")
def render(state):
    state["result"] = CliRunner().invoke(
        app,
        [
            "render",
            str(state["source"]),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(state["output"]),
            "--no-plugin-autoload",
            "--plugin",
            "svg",
            "--plugin",
            "events",
        ],
    )


@then("the SVG contains both plugin contributions in declaration order")
def svg_contains_both(state):
    assert state["result"].exit_code == 0, state["result"].output
    root = ElementTree.parse(state["output"]).getroot()
    assert [element.tag.rsplit("}", 1)[-1] for element in root] == ["rect", "text"]
    assert root[1].text == "2020-01-02 — launch day"


@given("a legacy plugin manifest without statement templates")
def legacy_manifest(state):
    state["manifest"] = {
        "schema_version": 2,
        "id": "old",
        "version": "1",
        "outputs": ["image"],
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }


@when("I try to read its capabilities")
def read_manifest(state):
    with pytest.raises(RegistrationError) as exc:
        validate_manifest(state["manifest"])
    state["error"] = str(exc.value)


@then("the plugin must be migrated before it can be used")
def migration_required(state):
    assert "migrat" in state["error"].lower()
    assert "3" in state["error"]
