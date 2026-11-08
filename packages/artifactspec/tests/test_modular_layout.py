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
