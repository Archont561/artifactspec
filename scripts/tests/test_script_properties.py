"""Property checks for the repository's standalone CI helpers."""

import importlib.util
import os
import string
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

SCRIPTS = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


detect_changes = load_script("detect_changes")
select_commit_range = load_script("select_commit_range")
activate = load_script("activate")

safe_name = st.text(
    alphabet=string.ascii_letters + string.digits + "_-", min_size=1, max_size=24
)
change = st.one_of(
    safe_name.map(lambda name: (f"docs/{name}.md", "docs")),
    safe_name.map(lambda name: (f"backlog/{name}.md", "docs")),
    safe_name.map(lambda name: (f"packages/{name}/README.md", "docs")),
    safe_name.map(lambda name: (f"scripts/{name}.py", "scripts")),
    safe_name.map(lambda name: (f"packages/{name}/src/main.py", "full")),
)


@given(
    changes=st.lists(change, max_size=15),
    event=st.sampled_from(["push", "pull_request", "workflow_dispatch"]),
)
def test_change_detection_selects_the_most_conservative_scope(changes, event):
    paths = [path for path, _ in changes]
    raw = b"\0".join(os.fsencode(path) for path in paths)
    calls = [b"merge-base\n", raw] if event == "pull_request" else [raw]
    with patch.object(detect_changes, "git", side_effect=calls):
        result = detect_changes.detect(Path("/unused"), "base", "head", event)
    kinds = {kind for _, kind in changes}
    expected = (
        "full"
        if not kinds or "full" in kinds
        else "scripts"
        if "scripts" in kinds
        else "docs"
    )
    assert result["scope"] == expected
    assert result["paths"] == paths
    assert result["reason"] == ("changed paths" if paths else "empty diff")


@given(base=st.one_of(st.just(""), st.text(alphabet="0", min_size=1, max_size=40)))
def test_missing_change_detection_base_always_fails_closed(base):
    with patch.object(
        detect_changes, "git", side_effect=AssertionError("must not call git")
    ):
        assert detect_changes.detect(Path("/unused"), base, "head", "push") == {
            "scope": "full",
            "reason": "no base revision",
            "paths": [],
        }


@given(
    base=safe_name.filter(lambda value: set(value) != {"0"}),
    head=safe_name,
    event=st.sampled_from(["push", "pull_request", "workflow_dispatch"]),
)
def test_explicit_commit_range_uses_the_merge_base_only_for_pull_requests(
    base, head, event
):
    with (
        patch.object(
            select_commit_range, "commit", side_effect=lambda repo, rev: f"sha-{rev}"
        ),
        patch.object(select_commit_range, "git", return_value="common") as git,
    ):
        result = select_commit_range.select_range(
            Path("/unused"), base, head, event, False, "refs/heads/work", "main"
        )
    assert (
        result
        == f"{'common' if event == 'pull_request' else 'sha-' + base}..sha-{head}"
    )
    assert git.call_count == (1 if event == "pull_request" else 0)


@given(
    head=safe_name, forced=st.booleans(), base=st.one_of(st.just(""), st.just("0" * 40))
)
def test_missing_base_on_default_branch_selects_all_reachable_commits(
    head, forced, base
):
    with (
        patch.object(
            select_commit_range, "commit", side_effect=lambda repo, rev: f"sha-{rev}"
        ),
        patch.object(
            select_commit_range,
            "git",
            side_effect=AssertionError("must not compare against itself"),
        ),
    ):
        result = select_commit_range.select_range(
            Path("/unused"), base, head, "push", forced, "refs/heads/main", "main"
        )
    assert result == f"sha-{head}"


@given(paths=st.lists(safe_name, unique=True, max_size=8))
def test_activation_preserves_inherited_paths_without_duplicate_discovered_sources(
    paths,
):
    root = Path("/workspace")
    project_records = b"one/pyproject.toml\0nested/two/pyproject.toml\0"
    source_one = str(root / "one/src")
    source_two = str(root / "nested/two/src")
    inherited = [*paths, source_one]
    with (
        patch.object(activate.subprocess, "run") as run,
        patch.object(Path, "is_file", return_value=True),
        patch.object(Path, "is_dir", return_value=True),
    ):
        run.return_value.stdout = project_records
        result = activate.python_path(root, os.pathsep.join(inherited)).split(
            os.pathsep
        )
    assert result == sorted([source_one, source_two]) + paths
    assert result.count(source_one) == 1


@pytest.mark.parametrize(
    "path,expected",
    [
        ("README.md", "docs"),
        ("CHANGELOG.md", "docs"),
        ("scripts/readme.md", "scripts"),
        ("packages/x/README.md", "docs"),
        ("packages/x/code.py", "full"),
        (".github/workflows/ci.yml", "full"),
    ],
)
def test_change_kind_known_boundaries(path, expected):
    assert detect_changes.kind(path) == expected
