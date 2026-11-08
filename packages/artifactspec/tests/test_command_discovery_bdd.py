import sys
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when
from typer.testing import CliRunner

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "command_discovery.feature")
)


@pytest.fixture
def state():
    return {}


@given(
    "a built-in command module exposes a Typer application with multiple commands and a nested group"
)
def add_command(state, tmp_path, monkeypatch):
    from artifactspec.cli import commands

    (tmp_path / "hello.py").write_text(
        """import typer
app = typer.Typer()
nested = typer.Typer()
app.add_typer(nested, name="tools")
@app.command()
def hello():
    print("hello")
@app.command()
def goodbye():
    print("goodbye")
@nested.command()
def inspect(name: str):
    print(f"inspecting {name}")
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    monkeypatch.delitem(sys.modules, "artifactspec.cli.commands.hello", raising=False)


@when("the CLI discovers command modules")
def discover(state):
    from artifactspec.cli import create_app

    state["app"] = create_app()


@then("both commands and the nested command are available from the Typer application")
def command_available(state):
    for args, expected in [
        (["hello"], "hello\n"),
        (["goodbye"], "goodbye\n"),
        (["tools", "inspect", "sample"], "inspecting sample\n"),
    ]:
        result = CliRunner().invoke(state["app"], args)
        assert result.exit_code == 0, result.output
        assert result.output == expected


@then("the module is loaded from the CLI commands package")
def command_is_under_cli():
    assert "artifactspec.cli.commands.hello" in sys.modules
    assert "artifactspec.commands.hello" not in sys.modules
