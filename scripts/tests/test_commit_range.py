"""Regression tests for the revisions sent to conventional-commit lint."""

import subprocess
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

SCRIPT = Path(__file__).resolve().parents[1] / "select_commit_range.py"
scenarios(str(Path(__file__).parent / "features" / "commit_range.feature"))


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def history(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "commit", "--allow-empty", "-qm", "chore: base")
    base = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "update-ref", "refs/remotes/origin/main", base)
    git(tmp_path, "commit", "--allow-empty", "-qm", "feat: first")
    previous = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "commit", "--allow-empty", "-qm", "fix: second")
    head = git(tmp_path, "rev-parse", "HEAD")
    return tmp_path, base, previous, head


def select(history, *, base, event="push", forced="false", ref="refs/heads/feature"):
    repo, _, _, head = history
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--base",
            base,
            "--head",
            head,
            "--event",
            event,
            "--forced",
            forced,
            "--ref",
            ref,
            "--default-branch",
            "main",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@given("a branch with two commits after the default branch", target_fixture="branch")
def branch_with_two_commits(history):
    return {"history": history}


@when("CI selects the range for a force-push with a missing previous commit")
def force_push_with_missing_previous(branch):
    branch["result"] = select(branch["history"], base="a" * 40, forced="true")


@then("all branch commits since the default merge base are selected")
def full_branch_is_selected(branch):
    _, base, _, head = branch["history"]
    result = branch["result"]
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{base}..{head}"


def test_force_push_checks_full_branch_even_if_before_is_available(history):
    _, base, previous, head = history
    result = select(history, base=previous, forced="true")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{base}..{head}"


def test_force_push_to_default_branch_checks_all_reachable_commits(history):
    repo, _, previous, head = history
    git(repo, "update-ref", "refs/remotes/origin/main", head)
    result = select(history, base=previous, forced="true", ref="refs/heads/main")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == head


def test_new_branch_checks_since_default_merge_base(history):
    _, base, _, head = history
    result = select(history, base="0" * 40)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{base}..{head}"


def test_new_default_branch_checks_all_reachable_commits(history):
    repo, _, _, head = history
    git(repo, "update-ref", "refs/remotes/origin/main", head)
    result = select(history, base="0" * 40, ref="refs/heads/main")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == head


def test_regular_push_uses_before_revision(history):
    _, _, previous, head = history
    result = select(history, base=previous)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{previous}..{head}"


def test_missing_before_on_nonforced_push_fails_closed(history):
    result = select(history, base="a" * 40)
    assert result.returncode != 0
    assert not result.stdout.strip()


def test_pull_request_uses_merge_base(history):
    _, base, _, head = history
    result = select(history, base=base, event="pull_request")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"{base}..{head}"


def test_manual_run_without_base_checks_all_reachable_commits(history):
    _, _, _, head = history
    result = select(history, base="", event="workflow_dispatch", ref="refs/heads/main")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == head


def test_force_push_missing_default_branch_fails_closed(history):
    repo, _, _, _ = history
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    result = select(history, base="a" * 40, forced="true")
    assert result.returncode != 0
    assert not result.stdout.strip()


def test_force_push_without_common_ancestor_fails_closed(history):
    repo, _, _, head = history
    tree = git(repo, "rev-parse", f"{head}^{{tree}}")
    unrelated = git(repo, "commit-tree", tree, "-m", "chore: unrelated")
    git(repo, "update-ref", "refs/remotes/origin/main", unrelated)
    result = select(history, base="a" * 40, forced="true")
    assert result.returncode != 0
    assert not result.stdout.strip()


def test_pull_request_without_base_fails_closed(history):
    result = select(history, base="", event="pull_request")
    assert result.returncode != 0
    assert not result.stdout.strip()


def test_missing_head_fails_closed(history):
    repo, base, previous, _ = history
    result = select((repo, base, previous, "a" * 40), base=previous, forced="true")
    assert result.returncode != 0
    assert not result.stdout.strip()


def test_workflow_uses_forced_event_and_range_selector():
    workflow = (SCRIPT.parents[1] / ".github/workflows/ci.yml").read_text()
    assert "EVENT_FORCED: ${{ github.event.forced }}" in workflow
    assert "python scripts/select_commit_range.py" in workflow
    assert 'convco check --merges "$RANGE"' in workflow
