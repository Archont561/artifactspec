import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "validate_cli.feature")
)


@pytest.fixture
def state():
    return {}


def prepare(state, installed_plugin_factory, tmp_path, text):
    manifest = {
        "schema_version": 2,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "phrases": [{"name": "circle", "outputs": [], "object_type": "circle"}],
        "properties": [{"name": "color", "outputs": [], "target_types": ["circle"]}],
        "representations": [],
        "renderers": [],
    }
    state.update(installed_plugin_factory(manifest=manifest))
    state["file"] = tmp_path / "scene.art"
    state["file"].write_text(text, encoding="utf-8")


@given("an installed typed plugin and a valid specification file")
def valid_spec(state, installed_plugin_factory, tmp_path):
    prepare(
        state,
        installed_plugin_factory,
        tmp_path,
        'Output image.\nCreate circle named c.\nSet color of c to "red".',
    )


@given("an installed typed plugin and a specification with missing references")
def invalid_spec(state, installed_plugin_factory, tmp_path):
    prepare(
        state,
        installed_plugin_factory,
        tmp_path,
        'Output image.\nSet color of missing to "red".\nSet color of it to "blue".',
    )


@when("I validate the file as JSON")
def run_validate(state):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(state["path"]), env.get("PYTHONPATH", "")])
    state["process"] = subprocess.run(
        [
            sys.executable,
            "-m",
            "artifactspec",
            "validate",
            str(state["file"]),
            "--format",
            "json",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    state["data"] = json.loads(state["process"].stdout)


@then("validation succeeds with no diagnostics")
def success(state):
    assert state["process"].returncode == 0
    assert state["data"] == {"schema_version": 1, "valid": True, "diagnostics": []}


@then("validation fails with two source-linked errors")
def failure(state):
    assert state["process"].returncode == 1
    assert state["data"]["valid"] is False
    diagnostics = state["data"]["diagnostics"]
    assert [d["code"] for d in diagnostics] == [
        "unresolved_reference",
        "unresolved_reference",
    ]
    assert [d["span"]["start"]["line"] for d in diagnostics] == [2, 3]
    assert all(d["span"]["source"] == str(state["file"]) for d in diagnostics)


@then("the installed validation plugin is not executed")
def not_executed(state):
    assert not state["marker"].exists()
