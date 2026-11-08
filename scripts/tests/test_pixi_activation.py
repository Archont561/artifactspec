"""Check that Pixi activation exposes local sources, independent of cwd."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
scenarios(str(Path(__file__).parent / "features/pixi_activation.feature"))


@given("an inherited Python path", target_fixture="state")
@given("a caller with an existing Python path", target_fixture="state")
def caller(tmp_path):
    if not shutil.which("pixi"):
        pytest.skip("Pixi is not available on PATH")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path)
    return {"env": env, "original": str(tmp_path)}


@given("a new Python project with a source directory")
def new_project(state, request):
    directory = tempfile.TemporaryDirectory(prefix="activation-test-", dir=ROOT)
    request.addfinalizer(directory.cleanup)
    project = Path(directory.name)
    (project / "pyproject.toml").write_text("[project]\nname = 'sample'\n")
    (project / "src").mkdir()
    state["new_src"] = str(project / "src")


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


@then("every project source directory is on the Python path")
def sources_visible(state):
    assert str(ROOT / "packages/artifactspec/src") in state["paths"]
    assert str(ROOT / "packages/artifactspec-manim/src") in state["paths"]


@then("the new project source directory is on the Python path")
def new_source_visible(state):
    assert state["new_src"] in state["paths"]


@then("the caller's existing Python path is preserved")
def previous_path_preserved(state):
    assert state["original"] in state["paths"]


def test_activation_script_is_not_installed_into_gherkin_environment():
    import tomllib

    with (ROOT / "pixi.toml").open("rb") as manifest:
        config = tomllib.load(manifest)
    assert "scripts/activate.py" in config["activation"]["env"]["PYTHONPATH"]
    assert config["environments"]["gherkin"]["no-default-feature"] is True


def test_discovery_includes_root_and_nested_projects_but_excludes_ignored(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("ignored/\n")
    for project in (tmp_path, tmp_path / "nested" / "other", tmp_path / "ignored"):
        project.mkdir(parents=True, exist_ok=True)
        (project / "pyproject.toml").write_text("")
        (project / "src").mkdir()
    (tmp_path / "no-src").mkdir()
    (tmp_path / "no-src" / "pyproject.toml").touch()
    env = os.environ.copy()
    env.update(PIXI_PROJECT_ROOT=str(tmp_path), PYTHONPATH="/existing")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/activate.py")],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = result.stdout.strip().split(os.pathsep)
    assert str(tmp_path / "src") in paths
    assert str(tmp_path / "nested/other/src") in paths
    assert str(tmp_path / "ignored/src") not in paths
    assert str(tmp_path / "no-src/src") not in paths
    assert paths[-1] == "/existing"


def test_pixi_activation_handles_checkout_paths_with_spaces(tmp_path):
    import json

    if not shutil.which("pixi"):
        pytest.skip("Pixi is not available on PATH")
    root = tmp_path / "workspace with spaces"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    shutil.copy(ROOT / "pixi.toml", root / "pixi.toml")
    shutil.copy(ROOT / "pixi.lock", root / "pixi.lock")
    (root / "scripts").mkdir()
    shutil.copy(ROOT / "scripts/activate.py", root / "scripts/activate.py")
    (root / "project with spaces" / "src").mkdir(parents=True)
    (root / "project with spaces" / "pyproject.toml").touch()
    env = os.environ.copy()
    env["PYTHONPATH"] = "/existing"
    result = subprocess.run(
        [
            "pixi",
            "shell-hook",
            "--locked",
            "--no-install",
            "--manifest-path",
            str(root / "pixi.toml"),
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = json.loads(result.stdout)["environment_variables"]["PYTHONPATH"].split(
        os.pathsep
    )
    assert str(root / "project with spaces/src") in paths
    assert "/existing" in paths


def test_repeated_discovery_does_not_duplicate_source_paths(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "src").mkdir()
    env = os.environ.copy()
    env.update(PIXI_PROJECT_ROOT=str(tmp_path), PYTHONPATH=str(tmp_path / "src"))
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/activate.py")],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip().split(os.pathsep) == [str(tmp_path / "src")]
