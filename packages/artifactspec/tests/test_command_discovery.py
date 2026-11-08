import sys

import pytest
from typer.testing import CliRunner


def test_existing_commands_remain_available():
    from artifactspec.cli import app

    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert all(name in result.output for name in ("capabilities", "validate", "lsp"))


@pytest.mark.parametrize("contents", ["", "app = 42\n", "def app(): pass\n"])
def test_invalid_command_module_is_reported(tmp_path, monkeypatch, contents):
    from artifactspec.cli import commands, create_app

    (tmp_path / "bad.py").write_text(contents, encoding="utf-8")
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    monkeypatch.delitem(sys.modules, "artifactspec.cli.commands.bad", raising=False)
    with pytest.raises(TypeError, match="bad.*Typer"):
        create_app()


@pytest.mark.parametrize(
    "first,second",
    [
        (
            "@app.command('clash')\ndef one(): pass",
            "@app.command('clash')\ndef two(): pass",
        ),
        (
            "@app.command('clash')\ndef one(): pass",
            "app.add_typer(typer.Typer(), name='clash')",
        ),
        (
            "app.add_typer(typer.Typer(), name='clash')",
            "app.add_typer(typer.Typer(), name='clash')",
        ),
        (
            "@app.command()\ndef my_name(): pass",
            "@app.command('my-name')\ndef two(): pass",
        ),
    ],
)
def test_duplicate_command_names_are_rejected(tmp_path, monkeypatch, first, second):
    from artifactspec.cli import commands, create_app

    for module, declaration in (("first", first), ("second", second)):
        (tmp_path / f"{module}.py").write_text(
            f"import typer\napp = typer.Typer()\n{declaration}\n", encoding="utf-8"
        )
        monkeypatch.delitem(
            sys.modules, f"artifactspec.cli.commands.{module}", raising=False
        )
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    with pytest.raises(ValueError, match="Duplicate CLI command"):
        create_app()


def test_private_helpers_and_subpackages_are_not_imported(tmp_path, monkeypatch):
    from artifactspec.cli import commands, create_app

    (tmp_path / "_private.py").write_text(
        'raise RuntimeError("imported private helper")', encoding="utf-8"
    )
    directory = tmp_path / "nested"
    directory.mkdir()
    (directory / "__init__.py").write_text(
        'raise RuntimeError("imported subpackage")', encoding="utf-8"
    )
    (tmp_path / "useful.py").write_text(
        "import typer\napp = typer.Typer()\n@app.command()\ndef useful(): pass\n",
        encoding="utf-8",
    )
    monkeypatch.delitem(sys.modules, "artifactspec.cli.commands.useful", raising=False)
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    assert CliRunner().invoke(create_app(), ["useful"]).exit_code == 0


def test_nested_groups_keep_callbacks_options_and_commands(tmp_path, monkeypatch):
    from artifactspec.cli import commands, create_app

    (tmp_path / "tree.py").write_text(
        """import typer
app = typer.Typer()
outer = typer.Typer()
inner = typer.Typer()
app.add_typer(outer, name="outer")
outer.add_typer(inner, name="inner")
@outer.callback()
def outer_callback(prefix: str = typer.Option("default")):
    print("prefix=" + prefix)
@inner.command()
def show(name: str):
    print("name=" + name)
@inner.command()
def other():
    print("other")
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    monkeypatch.delitem(sys.modules, "artifactspec.cli.commands.tree", raising=False)
    app = create_app()
    result = CliRunner().invoke(
        app, ["outer", "--prefix", "hello", "inner", "show", "value"]
    )
    assert result.exit_code == 0, result.output
    assert result.output == "prefix=hello\nname=value\n"
    result = CliRunner().invoke(app, ["outer", "inner", "--help"])
    assert result.exit_code == 0
    assert "show" in result.output and "other" in result.output


def test_module_app_can_supply_its_own_group_name_and_callback(tmp_path, monkeypatch):
    from artifactspec.cli import commands, create_app

    (tmp_path / "named.py").write_text(
        """import typer
app = typer.Typer(name="tools")
@app.callback()
def callback():
    print("starting tools")
@app.command()
def scan():
    print("scanning")
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(commands, "__path__", [str(tmp_path)])
    monkeypatch.delitem(sys.modules, "artifactspec.cli.commands.named", raising=False)
    result = CliRunner().invoke(create_app(), ["tools", "scan"])
    assert result.exit_code == 0, result.output
    assert result.output == "starting tools\nscanning\n"


def test_nested_unnamed_groups_flatten_and_reject_collisions():
    import typer

    from artifactspec.cli._app import _check_command_tree

    root = typer.Typer()
    named = typer.Typer()
    first = typer.Typer()
    second = typer.Typer()
    root.add_typer(named, name="outer")
    named.add_typer(first)
    named.add_typer(second)
    first.command("same")(lambda: None)
    second.command("same")(lambda: None)
    with pytest.raises(ValueError, match="Duplicate CLI command 'outer same'"):
        _check_command_tree(root, set(), (), set())


def test_same_command_name_is_allowed_in_distinct_groups():
    import typer

    from artifactspec.cli._app import _check_command_tree

    root = typer.Typer()
    for group_name in ("first", "second"):
        group = typer.Typer()
        group.command("show")(lambda: None)
        root.add_typer(group, name=group_name)
    _check_command_tree(root, set(), (), set())
    for group_name in ("first", "second"):
        assert CliRunner().invoke(root, [group_name, "show"]).exit_code == 0


def test_unnamed_group_callback_is_rejected_instead_of_silently_dropped():
    import typer

    from artifactspec.cli._app import _check_command_tree

    root = typer.Typer()
    group = typer.Typer()
    group.callback()(lambda: None)
    root.add_typer(group)
    with pytest.raises(ValueError, match="Unnamed.*callbacks"):
        _check_command_tree(root, set(), (), set())


def test_cyclic_group_tree_is_rejected():
    import typer

    from artifactspec.cli._app import _check_command_tree

    root = typer.Typer()
    child = typer.Typer()
    root.add_typer(child, name="child")
    child.add_typer(root, name="cycle")
    with pytest.raises(ValueError, match="Cyclic CLI command group"):
        _check_command_tree(root, set(), (), set())
