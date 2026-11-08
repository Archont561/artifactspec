"""Test the devcontainer bootstrap without network or container access."""

import json
import os
import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]
SETUP = ROOT / ".devcontainer/setup.sh"
scenarios(str(Path(__file__).parent / "features/devcontainer_setup.feature"))


@pytest.fixture
def container(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "pixi.log"
    pixi = bin_dir / "pixi"
    pixi.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$PIXI_TEST_LOG"\n')
    pixi.chmod(0o755)
    uname = bin_dir / "uname"
    uname.write_text(
        '#!/bin/sh\ncase "$1" in -s) echo "${TEST_OS:-Linux}";; '
        '-m) echo "${TEST_ARCH:-x86_64}";; esac\n'
    )
    uname.chmod(0o755)
    env = os.environ.copy()
    env.update(
        HOME=str(tmp_path),
        PATH=f"{bin_dir}:{env['PATH']}",
        PIXI_TEST_LOG=str(log),
        ARTIFACTSPEC_INSTALL_OPENCODE="0",
    )
    return {"env": env, "log": log}


@given("a supported development container with Pixi available", target_fixture="state")
def supported_container(container):
    return container


@when("its setup script runs")
def run_setup(state):
    state["result"] = subprocess.run(
        ["bash", str(SETUP)],
        cwd=ROOT,
        env=state["env"],
        text=True,
        capture_output=True,
        check=False,
    )


@then("the developer tools and locked project environments are installed")
def project_is_ready(state):
    assert state["result"].returncode == 0, state["result"].stderr
    commands = state["log"].read_text().splitlines()
    assert "global install --channel conda-forge git gh" in commands
    assert any("pixi-sandbox=0.9.0" in command for command in commands)
    assert "install --locked --all" in commands
    assert "run --locked bun-install" in commands
    assert "run --locked install-projects" in commands


@then("optional agent tooling is not installed by default")
def no_agent_install(state):
    assert "opencode" not in state["log"].read_text()


def test_optional_opencode_install_is_explicit(container):
    container["env"]["ARTIFACTSPEC_INSTALL_OPENCODE"] = "1"
    result = subprocess.run(
        ["bash", str(SETUP)],
        cwd=ROOT,
        env=container["env"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "opencode-ai@1.19.5" in container["log"].read_text()


def test_invalid_opencode_option_fails_before_install(container):
    container["env"]["ARTIFACTSPEC_INSTALL_OPENCODE"] = "invalid"
    result = subprocess.run(
        ["bash", str(SETUP)],
        cwd=ROOT,
        env=container["env"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert not container["log"].exists()


def test_unsupported_architecture_fails_before_install(container):
    container["env"]["TEST_ARCH"] = "aarch64"
    result = subprocess.run(
        ["bash", str(SETUP)],
        cwd=ROOT,
        env=container["env"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Linux x86-64" in result.stderr
    assert not container["log"].exists()


def test_devcontainer_points_to_setup():
    config = json.loads((ROOT / ".devcontainer/devcontainer.json").read_text())
    assert config["image"] == "ghcr.io/prefix-dev/pixi:0.84.1"
    assert config["postCreateCommand"] == "bash .devcontainer/setup.sh"
