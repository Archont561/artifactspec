"""Check that Pixi activation exposes local sources, independent of cwd."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
scenarios(str(Path(__file__).parent / "features/pixi_activation.feature"))


@given("a caller with an existing Python path", target_fixture="state")
def caller(tmp_path):
    if not shutil.which("pixi"):
        pytest.skip("Pixi is not available on PATH")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path)
    return {"env": env, "original": str(tmp_path)}


@when("Pixi activates the default environment from a package directory")
def activate(state):
    result = subprocess.run(
        [
            "pixi",
            "run",
            "--frozen",
            "-x",
            "python",
            "-c",
            "import os; print(os.environ.get('PYTHONPATH', ''))",
        ],
        cwd=ROOT / "packages/artifactspec",
        env=state["env"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    state["paths"] = result.stdout.strip().split(os.pathsep)


@then("both package source directories are on the Python path")
def sources_visible(state):
    assert state["paths"][:2] == [
        str(ROOT / "packages/artifactspec/src"),
        str(ROOT / "packages/artifactspec-manim/src"),
    ]


@then("the caller's existing Python path is preserved")
def previous_path_preserved(state):
    assert state["original"] in state["paths"]


def test_activation_script_is_not_installed_into_gherkin_environment():
    import tomllib

    with (ROOT / "pixi.toml").open("rb") as manifest:
        config = tomllib.load(manifest)
    assert config["activation"]["scripts"] == ["scripts/activate.sh"]
    assert config["environments"]["gherkin"]["no-default-feature"] is True
