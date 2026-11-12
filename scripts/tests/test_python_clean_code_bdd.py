"""Verify the clean code gate against the installed Rude plugin."""

import re
import subprocess
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
scenarios(str(ROOT / "scripts/tests/features/python_clean_code.feature"))


@pytest.fixture
def state():
    return {}


@given("a Python file that mutates global state")
def global_statement(state):
    state["source"] = "def update():\n    global value\n    value = 1\n"


@given("a Python file with no clean code findings")
def clean_source(state):
    state["source"] = "def double(value):\n    return value * 2\n"


@when("the Python clean code gate checks the file")
def run_gate(state, tmp_path):
    path = tmp_path / "probe.py"
    path.write_text(state["source"], encoding="utf-8")
    state["result"] = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_clean_code.py"), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@then("the gate reports the global statement and fails")
def rejects_global(state):
    assert state["result"].returncode != 0
    assert "CC308" in state["result"].stdout


@then("the gate succeeds without findings")
def accepts_clean(state):
    assert state["result"].returncode == 0, state["result"].stderr


def test_hooks_and_python_ci_scopes_run_lint():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    hooks = (ROOT / "lefthook.yml").read_text(encoding="utf-8")
    assert "run: pixi run --locked lint" in hooks
    for section in ("scripts", "full"):
        job = re.search(
            rf"^  {section}:\n(.*?)(?=^  [a-z][\w-]*:|\Z)",
            workflow,
            re.MULTILINE | re.DOTALL,
        )
        assert job is not None
        assert "pixi run --locked lint" in job.group(1)


@pytest.mark.parametrize(
    ("source", "rule"),
    [
        ("try:\n    risky()\nexcept ValueError:\n    pass\n", "SIM105"),
        ("try:\n    risky()\nexcept Exception:\n    pass\n", "S110"),
        ("result = eval(data)\n", "S307"),
        ("exec(data)\n", "S102"),
        ("import pickle\nresult = pickle.loads(data)\n", "S301"),
        ("import yaml\nresult = yaml.load(data, Loader=yaml.Loader)\n", "S506"),
        ("import subprocess\nsubprocess.run('echo hi', shell=True)\n", "S602"),
        ("import requests\nrequests.get('https://example.com')\n", "S113"),
        ("print('debug')\n", "T201"),
    ],
)
def test_upstream_python_policy_equivalents_fail(tmp_path, source, rule):
    path = tmp_path / "probe.py"
    path.write_text(source, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--config",
            str(ROOT / "ruff.toml"),
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert rule in result.stdout


def test_clean_code_gate_fails_closed_if_plugin_rules_are_unavailable(monkeypatch):
    from scripts import check_clean_code

    monkeypatch.setattr(check_clean_code, "discover_rules", lambda **kwargs: [])
    assert check_clean_code.main([]) == 1


def test_clean_code_gate_fails_closed_if_config_is_missing(monkeypatch, tmp_path):
    from scripts import check_clean_code

    monkeypatch.setattr(check_clean_code, "CONFIG", tmp_path / "missing.toml")
    assert check_clean_code.main([]) == 1


def test_rude_function_length_warning_is_a_gate_failure(tmp_path):
    path = tmp_path / "long function.py"
    path.write_text("def long_function():\n" + "    value = 1\n" * 50, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_clean_code.py"), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert "CC101" in result.stdout


def test_python_file_selection_includes_hidden_and_untracked_files(
    monkeypatch, tmp_path
):
    from scripts import check_clean_code

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "tracked.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "new file.py").write_text("x = 2\n", encoding="utf-8")
    (tmp_path / "ignored").mkdir()
    (tmp_path / "ignored" / "skip.py").write_text("x = 3\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", ".hidden/tracked.py"], check=True
    )
    monkeypatch.setattr(check_clean_code, "ROOT", tmp_path)
    assert set(check_clean_code.python_files()) == {".hidden/tracked.py", "new file.py"}


def test_lint_task_requires_the_clean_code_check():
    import tomllib

    with (ROOT / "pixi.toml").open("rb") as source:
        tasks = tomllib.load(source)["tasks"]
    assert "lint-clean-code" in tasks["lint"]["depends-on"]
    assert tasks["lint-clean-code"] == "python scripts/check_clean_code.py"


@pytest.mark.parametrize(
    ("source", "rule"),
    [
        ("# TODO clean this up\nvalue = 1\n", "CC903"),
        (
            "def translate():\n    try:\n        risky()\n    except ValueError:\n        raise RuntimeError('bad')\n",
            "CC310",
        ),
    ],
)
def test_clean_code_gate_enforces_other_upstream_rules(tmp_path, source, rule):
    path = tmp_path / "probe.py"
    path.write_text(source, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_clean_code.py"), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert rule in result.stdout
