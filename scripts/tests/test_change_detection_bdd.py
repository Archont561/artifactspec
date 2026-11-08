import json
import subprocess
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
scenarios(str(ROOT / "scripts/tests/features/ci_change_scope.feature"))


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def state(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    (tmp_path / "seed.txt").write_text("seed", encoding="utf-8")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "chore: initial")
    return {"repo": tmp_path, "base": git(tmp_path, "rev-parse", "HEAD")}


@given(parsers.parse('a repository with a change to "{path}"'))
def change_file(state, path):
    target = state["repo"] / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("change\n", encoding="utf-8")
    git(state["repo"], "add", ".")
    git(state["repo"], "commit", "-qm", "chore: change")
    state["head"] = git(state["repo"], "rev-parse", "HEAD")


@when("CI detects the changed files")
def detect(state):
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/detect_changes.py"),
            "--repo",
            str(state["repo"]),
            "--base",
            state["base"],
            "--head",
            state["head"],
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    state["result"] = json.loads(proc.stdout)


@then(parsers.parse('the selected CI scope is "{scope}"'))
def check_scope(state, scope):
    assert state["result"]["scope"] == scope


def run_detection(state, base=None, event="push", env=None):
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/detect_changes.py"),
            "--repo",
            str(state["repo"]),
            "--base",
            state["base"] if base is None else base,
            "--head",
            git(state["repo"], "rev-parse", "HEAD"),
            "--event",
            event,
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(proc.stdout)


def test_missing_base_fails_closed(state):
    assert run_detection(state, base="not-a-commit")["scope"] == "full"
    assert run_detection(state, base="0" * 40)["scope"] == "full"


def test_mixed_docs_and_scripts_runs_both(state):
    for name in ("docs/guide.md", "scripts/ci.py"):
        target = state["repo"] / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("content\n", encoding="utf-8")
    git(state["repo"], "add", ".")
    git(state["repo"], "commit", "-qm", "chore: mixed change")
    result = run_detection(state)
    assert result["scope"] == "scripts"
    assert result["run_scripts"] == "true"
    assert result["run_docs"] == "true"
    assert result["skip_full"] == "true"


def test_renaming_code_to_docs_runs_full_ci(state):
    source = state["repo"] / "packages/app.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("example\n", encoding="utf-8")
    git(state["repo"], "add", ".")
    git(state["repo"], "commit", "-qm", "feat: add source")
    state["base"] = git(state["repo"], "rev-parse", "HEAD")
    (state["repo"] / "docs").mkdir()
    git(state["repo"], "mv", "packages/app.py", "docs/app.md")
    git(state["repo"], "commit", "-qm", "refactor: move file")
    assert run_detection(state)["scope"] == "full"


def test_outputs_are_written_for_github_actions(state, tmp_path):
    import os

    change_file(state, "docs/guide.md")
    destination = tmp_path / "github-output"
    env = os.environ.copy()
    env["GITHUB_OUTPUT"] = str(destination)
    env["GITHUB_ENV"] = str(tmp_path / "github-env")
    result = run_detection(state, env=env)
    assert result["scope"] == "docs"
    assert "run_docs=true\n" in destination.read_text(encoding="utf-8")
    assert "skip_full=true\n" in (tmp_path / "github-env").read_text(encoding="utf-8")


def test_pull_request_uses_merge_base(state):
    repo = state["repo"]
    git(repo, "checkout", "-qb", "feature")
    change_file(state, "docs/guide.md")
    git(repo, "checkout", "-qb", "base-branch", state["base"])
    source = repo / "app.py"
    source.write_text("base-only\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "feat: unrelated base change")
    updated_base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "feature")
    result = run_detection(state, base=updated_base, event="pull_request")
    assert result["scope"] == "docs"
    assert result["paths"] == ["docs/guide.md"]
