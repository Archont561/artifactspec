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
    from artifactspec_events.plugin import plugin as event_plugin

    from artifactspec.plugins import Registry

    registry = Registry()
    registry.register(event_plugin)
    from artifactspec_svg.plugin import plugin as svg_plugin

    registry.register(svg_plugin)
    state["registry"] = registry
    if output == "report":
        state["spec"] = (
            'Output report.\nCreate event named title.\nSet date of title to "2000-01-01".\nSet label of title to "Hello & world".'
        )
    else:
        state["spec"] = (
            'Output image.\nCreate text named title.\nSet value of title to "Hello & world".\nCreate rectangle named box.'
        )


@given("trusted SVG and event plugins and an image specification")
def image_spec(state):
    setup(state, "image")


@given("trusted SVG and event plugins and a report specification")
def report_spec(state):
    setup(state, "report")


@when("I render it using the selected representation and renderer")
def render_image(state, tmp_path):
    from artifactspec.core.rendering import render

    state["path"] = tmp_path / "scene.svg"
    state["result"] = render(
        state["spec"],
        state["registry"],
        representation="diagram",
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
    assert result.renderer == "svg" and result.representation == "diagram"
    assert result.artifact.path == state["path"]
    assert result.artifact.media_type == "image/svg+xml" and result.artifact.editable
    assert {span.start.line for span in result.provenance} == {2, 3, 4}
    assert all(span.source == "scene.art" for span in result.provenance)


@when("I select the report representation")
def select_report(state):
    from artifactspec.core.pipeline import build_content
    from artifactspec.core.rendering import compose

    content = build_content(state["spec"], state["registry"])
    state["composition"] = compose(
        content, output="report", representation="diagram", registry=state["registry"]
    )


@then("the semantic text is represented without animation playback")
def report_composition(state):
    composition = state["composition"]
    assert composition.output == "report"
    assert any(
        getattr(item.value, "text", None) == "2000-01-01: Hello & world"
        for item in composition.elements
    )
    assert not hasattr(composition, "playback")


@given("a specification file and an installed SVG plugin")
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
            "--representation",
            "diagram",
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
    assert result["renderer"] == "svg" and result["representation"] == "diagram"
    assert result["artifact"]["path"] == str(state["destination"])
    assert {span["start"]["line"] for span in result["provenance"]} == {2, 3}
    assert (
        ElementTree.parse(state["destination"])
        .getroot()
        .find("{http://www.w3.org/2000/svg}text")
        .text
        == "CLI"
    )


@given("a timeline of two dated events in declaration order")
def timeline_spec(state):
    from artifactspec_events.plugin import plugin as event_plugin

    from artifactspec.core.pipeline import build_content
    from artifactspec.plugins import Registry

    registry = Registry()
    registry.register(event_plugin)
    text = (
        "Output image.\nCreate event named first.\n"
        'Set date of first to "2001-01-01".\nSet label of first to "First".\n'
        "Create event named second.\n"
        'Set date of second to "1900-02-03".\nSet label of second to "Second".'
    )
    state["registry"] = registry
    state["content"] = build_content(text, registry, source="timeline.art")


@when("I compose the same semantic timeline for image and report")
def timeline_compositions(state):
    from artifactspec.core.rendering import compose

    content = state["content"]
    state["forms"] = [
        compose(
            content, output=output, representation="diagram", registry=state["registry"]
        )
        for output in ("image", "report")
    ]


@then("both forms preserve the event dates and labels in declaration order")
def timeline_forms(state):
    content = state["content"]
    assert [(n.object_type, dict(n.properties)) for n in content.nodes] == [
        ("event", {"date": "2001-01-01", "value": "First"}),
        ("event", {"date": "1900-02-03", "value": "Second"}),
    ]
    assert [
        [element.value.text for element in form.elements] for form in state["forms"]
    ] == [
        ["2001-01-01 — First", "1900-02-03 — Second"],
        ["2001-01-01: First", "1900-02-03: Second"],
    ]
    for form in state["forms"]:
        assert [
            [span.start.line for span in item.provenance] for item in form.elements
        ] == [[2, 3, 4], [5, 6, 7]]
        assert all(
            span.source == "timeline.art"
            for item in form.elements
            for span in item.provenance
        )


@then("the event dates are not animation playback timing")
def no_playback(state):
    for form in state["forms"]:
        assert not hasattr(form, "playback")
        assert not hasattr(form.elements[0], "time")
    assert state["forms"][0].elements[0].value.y == 40
    assert state["forms"][0].elements[1].value.y == 110


@given("a specification that produces a source-linked SVG image")
def inspectable_spec(state, tmp_path):
    state["spec_file"] = tmp_path / "scene.art"
    state["spec_file"].write_text(
        'Output image.\nCreate text named t.\nSet value of t to "Hello".',
        encoding="utf-8",
    )
    state["destination"] = tmp_path / "scene.svg"


@given("a specification with an unsupported SVG color and an existing artifact")
def invalid_color_spec(state, tmp_path):
    state["spec_file"] = tmp_path / "scene.art"
    state["spec_file"].write_text(
        'Output image.\nCreate text named t.\nSet color of t to "url(x)".',
        encoding="utf-8",
    )
    state["destination"] = tmp_path / "scene.svg"
    state["destination"].write_text("existing", encoding="utf-8")


@when("I request a machine-readable render result")
def run_json_render(state):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    state["result"] = CliRunner().invoke(
        app,
        [
            "render",
            str(state["spec_file"]),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(state["destination"]),
            "--format",
            "json",
        ],
    )


@then(
    "the result reports composition provenance and limitations without asserting fidelity"
)
def check_inspectable_result(state):
    import json

    assert state["result"].exit_code == 0, state["result"].output
    data = json.loads(state["result"].stdout)
    assert data["status"] == "success"
    assert data["provenance_status"] == "available"
    assert {span["start"]["line"] for span in data["provenance"]} == {2, 3}
    assert data["limitations"] and data["fallback"] is None
    assert "fidelity" not in data


@then("the result identifies the rendering error without replacing the artifact")
def check_inspectable_error(state):
    import json

    assert state["result"].exit_code == 2
    data = json.loads(state["result"].stdout)
    assert data["schema_version"] == 1 and data["status"] == "error"
    assert data["error"]["code"] == "renderer_failed"
    assert "unsupported SVG color" in data["error"]["message"]
    assert state["destination"].read_text(encoding="utf-8") == "existing"
