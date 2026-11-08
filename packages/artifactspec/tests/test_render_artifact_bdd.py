from pathlib import Path
from xml.etree import ElementTree

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "render_artifact.feature")
)


@pytest.fixture
def state():
    return {}


def setup(state, output):
    from artifactspec.basic import basic_plugin
    from artifactspec.plugins import Registry

    registry = Registry()
    registry.register(basic_plugin())
    state["registry"] = registry
    state["spec"] = (
        f'Output {output}.\nCreate text named title.\nSet value of title to "Hello & world".\nCreate rectangle named box.'
    )


@given("an explicitly trusted basic SVG plugin and an image specification")
def image_spec(state):
    setup(state, "image")


@given("an explicitly trusted basic SVG plugin and a report specification")
def report_spec(state):
    setup(state, "report")


@when("I render it using the selected representation and renderer")
def render_image(state, tmp_path):
    from artifactspec.rendering import render

    state["path"] = tmp_path / "scene.svg"
    state["result"] = render(
        state["spec"],
        state["registry"],
        representation="basic",
        renderer="svg",
        destination=state["path"],
        source="scene.art",
    )


@then("the SVG artifact contains the described text and rectangle")
def svg_content(state):
    root = ElementTree.parse(state["path"]).getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.find("{http://www.w3.org/2000/svg}text").text == "Hello & world"
    assert root.find("{http://www.w3.org/2000/svg}rect") is not None


@then("the result identifies its renderer and source provenance")
def provenance(state):
    result = state["result"]
    assert result.renderer == "svg" and result.representation == "basic"
    assert result.artifact.path == state["path"]
    assert result.artifact.media_type == "image/svg+xml" and result.artifact.editable
    assert {span.start.line for span in result.provenance} == {2, 3, 4}
    assert all(span.source == "scene.art" for span in result.provenance)


@when("I select the report representation")
def select_report(state):
    from artifactspec.pipeline import build_content
    from artifactspec.rendering import compose

    content = build_content(state["spec"], state["registry"])
    state["composition"] = compose(
        content, output="report", representation="basic", registry=state["registry"]
    )


@then("the semantic text is represented without animation playback")
def report_composition(state):
    composition = state["composition"]
    assert composition.output == "report"
    assert any(
        getattr(item, "text", None) == "Hello & world" for item in composition.elements
    )
    assert not hasattr(composition, "playback")


@given("a specification file and explicitly selected built-in image plugin")
def cli_spec(state, tmp_path):
    state["spec_file"] = tmp_path / "spec.art"
    state["spec_file"].write_text(
        'Output image.\nCreate text named title.\nSet value of title to "CLI".',
        encoding="utf-8",
    )
    state["destination"] = tmp_path / "render.svg"


@when("I invoke the render command with explicit capabilities")
def run_cli(state):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    state["result"] = CliRunner().invoke(
        app,
        [
            "render",
            str(state["spec_file"]),
            "--builtin-basic",
            "--representation",
            "basic",
            "--renderer",
            "svg",
            "--output",
            str(state["destination"]),
        ],
    )


@then("the command writes an SVG artifact and reports its provenance")
def check_cli(state):
    import json

    assert state["result"].exit_code == 0, state["result"].output
    result = json.loads(state["result"].output)
    assert result["renderer"] == "svg" and result["representation"] == "basic"
    assert result["artifact"]["path"] == str(state["destination"])
    assert {span["start"]["line"] for span in result["provenance"]} == {2, 3}
    assert (
        ElementTree.parse(state["destination"])
        .getroot()
        .find("{http://www.w3.org/2000/svg}text")
        .text
        == "CLI"
    )
