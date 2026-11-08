"""Check idempotent Lefthook setup without modifying the checkout's hooks."""

import os
import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/install_hooks.sh"
scenarios(str(Path(__file__).parent / "features/install_hooks.feature"))


@pytest.fixture
def hook_state(tmp_path):
    binary = tmp_path / "lefthook"
    binary.write_text(
        "#!/bin/sh\n"
        'echo "$1" >> "$HOOK_LOG"\n'
        'case "$1" in\n'
        '  check-install) [ -f "$HOOK_MARKER" ] && exit 0; exit "${CHECK_STATUS:-1}";;\n'
        '  install) [ "${INSTALL_STATUS:-0}" = 0 ] || exit "$INSTALL_STATUS"; '
        'touch "$HOOK_MARKER";;\n'
        "esac\n"
    )
    binary.chmod(0o755)
    env = os.environ.copy()
    env.update(
        PATH=f"{tmp_path}:{env['PATH']}",
        HOOK_LOG=str(tmp_path / "log"),
        HOOK_MARKER=str(tmp_path / "installed"),
    )
    return {"env": env, "log": tmp_path / "log", "marker": tmp_path / "installed"}


@given("Lefthook reports that hooks are missing", target_fixture="state")
def missing(hook_state):
    return hook_state


@given("Lefthook reports that hooks are already installed", target_fixture="state")
def installed(hook_state):
    hook_state["marker"].touch()
    return hook_state


@when("the hook installation script runs")
def run_script(state):
    state["result"] = subprocess.run(
        ["sh", str(SCRIPT)],
        env=state["env"],
        capture_output=True,
        text=True,
        check=False,
    )


@then("it installs and verifies the hooks")
def installs(state):
    assert state["result"].returncode == 0, state["result"].stderr
    assert state["log"].read_text().splitlines() == [
        "check-install",
        "install",
        "check-install",
    ]


@then("it does not reinstall the hooks")
def skips_install(state):
    assert state["result"].returncode == 0, state["result"].stderr
    assert state["log"].read_text().splitlines() == ["check-install"]


def test_failed_install_is_reported(hook_state):
    hook_state["env"]["INSTALL_STATUS"] = "2"
    run_script(hook_state)
    assert hook_state["result"].returncode != 0
    assert hook_state["log"].read_text().splitlines() == ["check-install", "install"]


def test_unexpected_check_error_is_not_treated_as_missing(hook_state):
    hook_state["env"]["CHECK_STATUS"] = "2"
    run_script(hook_state)
    assert hook_state["result"].returncode != 0
    assert hook_state["log"].read_text().splitlines() == ["check-install"]


def test_pixi_task_runs_hook_setup():
    import tomllib

    with (ROOT / "pixi.toml").open("rb") as manifest:
        tasks = tomllib.load(manifest)["tasks"]
    assert tasks["install-hooks"] == "sh scripts/install_hooks.sh"
    assert tasks["hooks-install"]["depends-on"] == ["install-hooks"]


def test_real_lefthook_install_is_idempotent(tmp_path):
    import shutil

    if shutil.which("lefthook") is None:
        pytest.skip("Lefthook is not available on PATH")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    shutil.copy(ROOT / "lefthook.yml", tmp_path / "lefthook.yml")
    for _ in range(2):
        result = subprocess.run(
            ["sh", str(SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
    assert "already installed" in result.stdout
    for hook in ("commit-msg", "pre-commit", "pre-push"):
        assert os.access(tmp_path / ".git" / "hooks" / hook, os.X_OK)
