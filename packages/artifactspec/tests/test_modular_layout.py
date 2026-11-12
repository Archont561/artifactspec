"""Core implementations live in focused importable packages."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "artifactspec.core.models",
        "artifactspec.core.parser",
        "artifactspec.core.pipeline",
        "artifactspec.core.rendering",
        "artifactspec.core.validation",
        "artifactspec.plugins.discovery",
        "artifactspec.core.templates",
        "artifactspec.editor.lsp",
        "artifactspec.testing.pytest_plugin",
    ],
)
def test_organized_modules_are_importable(module):
    assert importlib.import_module(module) is not None


def test_commands_live_under_cli_and_preserve_public_exports():
    from artifactspec.cli import app, create_app
    from artifactspec.cli.commands import capabilities, lsp, render, validate
    from artifactspec.plugin import Plugin
    from artifactspec.plugins import Plugin as RegistryPlugin
    from artifactspec.testing import FakePhraseContext
    from artifactspec.testing.contexts import FakePhraseContext as ImplementationContext

    assert app is not None and callable(create_app)
    assert all(
        module.app is not None for module in (capabilities, lsp, render, validate)
    )
    assert Plugin is RegistryPlugin
    assert FakePhraseContext is ImplementationContext


def _is_initializer_declaration(node):
    import ast

    is_import = isinstance(node, (ast.Import, ast.ImportFrom))
    is_docstring = (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )
    is_export_list = (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and (isinstance(node.targets[0], ast.Name) and node.targets[0].id == "__all__")
    )
    return is_import or is_docstring or is_export_list


def test_package_initializers_only_reexport_or_declare_all():
    import ast
    from pathlib import Path

    packages = Path(__file__).resolve().parents[2]
    initializers = sorted(packages.glob("*/src/**/__init__.py"))
    assert initializers
    for path in initializers:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            allowed = _is_initializer_declaration(node)
            assert allowed, (
                f"{path}: implementation in initializer on line {node.lineno}"
            )
