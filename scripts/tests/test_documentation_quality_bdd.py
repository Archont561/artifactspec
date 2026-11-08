"""Exercise the repository Vale policy using the real linter."""

import json
import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
scenarios(str(ROOT / "scripts/tests/features/documentation_quality.feature"))
VALE = ROOT / "node_modules/@taskless/vale-linux-x64/vale"


def lint_file(path):
    return subprocess.run(
        [
            str(VALE),
            f"--config={ROOT / '.vale.ini'}",
            "--no-global",
            "--output=JSON",
            str(path),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


@pytest.fixture
def state():
    return {}


@given("a documentation passage with inconsistent terminology")
def bad_term(state):
    state["text"] = "Use github actions for checks.\n"


@given("a documentation passage with terminology inside a code block")
def code_block(state):
    state["text"] = "```text\ngithub actions\n```\n"


@when("the passage is checked with Vale")
def run_vale(state, tmp_path):
    path = tmp_path / "probe.md"
    path.write_text(state["text"], encoding="utf-8")
    result = lint_file(path)
    state["exit_code"] = result.returncode
    state["output"] = result.stdout
    state["stderr"] = result.stderr


@then("Vale reports the preferred terminology")
def reports_term(state):
    assert state["exit_code"] == 1, state["stderr"]
    alerts = [
        item for alerts in json.loads(state["output"]).values() for item in alerts
    ]
    assert any(
        item["Check"] == "Project.Terms" and "GitHub Actions" in item["Message"]
        for item in alerts
    )


@then("Vale reports no findings")
def reports_nothing(state):
    assert state["exit_code"] == 0, state["stderr"]
    assert not any(json.loads(state["output"]).values())


@pytest.mark.parametrize(
    ("passage", "check", "fails"),
    [
        ("This sentsnce has a typo.\n", "Vale.Spelling", True),
        ("Use GitHub Actions for checks.\n", None, False),
        ("Use Github actions for checks.\n", "Project.Terms", True),
        ("Use GitHub\nActions for checks.\n", None, False),
        ("Run this.  Next run that.\n", "Microsoft.Spacing", True),
    ],
)
def test_vale_enforces_spelling_and_project_terms(tmp_path, passage, check, fails):
    path = tmp_path / "probe.md"
    path.write_text(passage, encoding="utf-8")
    result = lint_file(path)
    assert (result.returncode == 1) == fails, result.stderr
    alerts = [a for findings in json.loads(result.stdout).values() for a in findings]
    if check:
        assert any(item["Check"] == check for item in alerts)
    else:
        assert not alerts


@pytest.mark.parametrize(
    ("section", "has_warning"), [("docs", True), ("backlog", False)]
)
def test_backlog_has_less_aggressive_editorial_rules(tmp_path, section, has_warning):
    config = (
        (ROOT / ".vale.ini")
        .read_text(encoding="utf-8")
        .replace("StylesPath = .vale/styles", f"StylesPath = {ROOT / '.vale/styles'}")
    )
    (tmp_path / ".vale.ini").write_text(config, encoding="utf-8")
    directory = tmp_path / section
    directory.mkdir()
    (directory / "probe.md").write_text("This is very good.\n", encoding="utf-8")
    result = subprocess.run(
        [
            str(VALE),
            "--no-global",
            "--output=JSON",
            f"{section}/probe.md",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr  # Warnings are advisory.
    alerts = [a for findings in json.loads(result.stdout).values() for a in findings]
    assert any(a["Check"] == "write-good.Weasel" for a in alerts) == has_warning


def test_docs_and_full_ci_run_prose_and_repository_checks():
    import re

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for job in ("docs", "full"):
        match = re.search(
            rf"^  {job}:\n(.*?)(?=^  [a-z][\w-]*:|\Z)",
            workflow,
            re.MULTILINE | re.DOTALL,
        )
        assert match is not None
        assert "pixi run --locked lint-prose" in match.group(1)
        assert "pixi run --locked alint" in match.group(1)
