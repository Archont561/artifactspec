import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

from artifactspec.plugins import Plugin, RegistrationError, Registry

scenarios(
    str(
        Path(__file__).resolve().parents[1] / "features" / "plugin_capabilities.feature"
    ),
    str(Path(__file__).resolve().parents[1] / "features" / "typer_cli.feature"),
)


@pytest.fixture
def state():
    return {}


@given("a plugin declaring SVG and PDF output")
def plugin_with_outputs(state):
    plugin = Plugin("shapes", "1.0", outputs=("pdf", "svg"))

    @plugin.phrase("draw circle", outputs=("svg",))
    def draw(context):
        return context

    @plugin.property("color")
    def color(context):
        return context

    state["plugin"] = plugin


@when("the plugin is registered")
def register_plugin(state):
    state["registry"] = Registry()
    state["registry"].register(state["plugin"])


@then("its declared capabilities are available for compatible outputs")
def capabilities_registered(state):
    manifest = state["registry"].manifests(output="svg")[0]
    assert manifest["phrases"] == [{"name": "draw circle", "outputs": ["svg"]}]
    assert manifest["properties"] == [{"name": "color", "outputs": []}]
    pdf = state["registry"].manifests(output="pdf")[0]
    assert pdf["phrases"] == []
    assert pdf["properties"] == [{"name": "color", "outputs": []}]


@given("a registry with a phrase contribution")
def registry_with_phrase(state):
    registry = Registry()
    plugin = Plugin("first", "1", outputs=("svg",))
    plugin.phrase("same")(lambda context: context)
    registry.register(plugin)
    state["registry"] = registry
    state["before"] = registry.manifests()


@when("another plugin contributes the same phrase")
def conflicting_plugin(state):
    plugin = Plugin("second", "1", outputs=("pdf",))
    plugin.phrase("same")(lambda context: context)
    with pytest.raises(RegistrationError, match="phrase.*same") as error:
        state["registry"].register(plugin)
    state["error"] = str(error.value)


@then("registration fails without changing the registry")
def registration_atomic(state):
    assert "first" in state["error"] and "second" in state["error"]
    assert state["registry"].manifests() == state["before"]


@given("an installed plugin with a static manifest")
def installed_plugin(state, installed_plugin_factory):
    state.update(installed_plugin_factory())


@given("no installed plugins")
def no_installed_plugins(state, tmp_path, monkeypatch):
    from importlib import metadata

    monkeypatch.setattr(metadata, "entry_points", lambda **kwargs: [])
    state["path"] = tmp_path
    state["empty"] = True


def run_cli(state, *args):
    if state.get("empty"):
        from typer.testing import CliRunner

        from artifactspec.cli import app

        result = CliRunner().invoke(app, ["capabilities", *args])
        assert result.exit_code == 0, result.output
        state["result"] = json.loads(result.stdout)
        return
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(state["path"]), env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-m", "artifactspec", "capabilities", *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    state["result"] = json.loads(result.stdout)


@when("capability details are requested for SVG output")
def request_svg(state):
    run_cli(state, "--details", "--output", "svg")


@when("capability details are requested")
def request_all(state):
    run_cli(state, "--details")


@then("the matching capabilities are returned as JSON")
def matching_json(state):
    assert state["result"] == {
        "schema_version": 1,
        "plugins": [
            {
                "id": "example",
                "version": "1.0",
                "outputs": ["svg"],
                "capabilities": {
                    "phrases": [{"name": "draw", "outputs": ["svg"]}],
                    "properties": [],
                    "representations": [],
                    "renderers": [],
                },
            }
        ],
    }


@then("the installed plugin module has not been executed")
def module_not_executed(state):
    assert not state["marker"].exists()


@then("discovery returns an empty plugin list")
def empty_plugins(state):
    assert state["result"] == {"schema_version": 1, "plugins": []}


@when("the Typer app is invoked with SVG capability details")
def invoke_typer_app(state, monkeypatch):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    monkeypatch.syspath_prepend(str(state["path"]))
    result = CliRunner().invoke(app, ["capabilities", "--details", "--output", "svg"])
    assert result.exit_code == 0, result.output
    state["result"] = json.loads(result.stdout)
