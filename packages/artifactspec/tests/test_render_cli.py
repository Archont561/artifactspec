"""Integration checks for explicit plugin approval and CLI render failures."""

import json

import pytest
from typer.testing import CliRunner

from artifactspec.cli import app


@pytest.mark.parametrize(
    "extra,expected",
    [([], "select trusted plugins"), (["--plugin", "not-installed"], "not found")],
)
def test_render_requires_explicit_known_plugins(tmp_path, extra, expected):
    source = tmp_path / "source.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    dest = tmp_path / "out.svg"
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--output",
            str(dest),
            "--representation",
            "basic",
            "--renderer",
            "svg",
            *extra,
        ],
    )
    assert result.exit_code == 2
    assert expected in result.output
    assert not dest.exists()


def test_cli_reports_validation_errors_and_leaves_old_artifact(tmp_path):
    source = tmp_path / "source.art"
    source.write_text('Output image.\nSet value of absent to "x".', encoding="utf-8")
    dest = tmp_path / "out.svg"
    dest.write_bytes(b"existing")
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--output",
            str(dest),
            "--representation",
            "basic",
            "--renderer",
            "svg",
            "--builtin-basic",
        ],
    )
    assert result.exit_code == 1
    assert "unresolved_reference" in result.output
    assert dest.read_bytes() == b"existing"


def test_cli_reports_render_failure_and_missing_input(tmp_path):
    source = tmp_path / "source.art"
    destination = tmp_path / "out.svg"
    args = [
        "render",
        str(source),
        "--output",
        str(destination),
        "--representation",
        "basic",
        "--renderer",
        "svg",
        "--builtin-basic",
    ]
    missing = CliRunner().invoke(app, args)
    assert missing.exit_code == 2
    source.write_text(
        'Output image.\nCreate text named x.\nSet color of x to "url(x)".',
        encoding="utf-8",
    )
    invalid = CliRunner().invoke(app, args)
    assert invalid.exit_code == 2
    assert "unsupported SVG color" in invalid.output
    assert not destination.exists()


def test_cli_result_surfaces_layout_limitations(tmp_path):
    source = tmp_path / "source.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    destination = tmp_path / "out.svg"
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--output",
            str(destination),
            "--representation",
            "basic",
            "--renderer",
            "svg",
            "--builtin-basic",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["limitations"]


def test_cli_loads_only_explicitly_approved_installed_plugin(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = {
        "schema_version": 2,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "phrases": [{"name": "text", "outputs": [], "object_type": "text"}],
        "properties": [{"name": "value", "outputs": [], "target_types": ["text"]}],
        "representations": [{"name": "external", "outputs": []}],
        "renderers": [{"name": "external-svg", "outputs": []}],
    }
    marker = tmp_path / "executed"
    source_code = f"""from pathlib import Path
Path({str(marker)!r}).write_text("loaded")
from artifactspec.plugins import Plugin
from artifactspec.basic import _svg
plugin = Plugin("example", "1.0", outputs=("image",), schema_version=2)
@plugin.phrase("text", object_type="text")
def create(ctx):
    ctx.create("text")
@plugin.property("value", target_types=("text",))
def apply(ctx):
    ctx.set("value", ctx.value)
@plugin.representation("external")
def layout(ctx):
    for node in ctx.content.nodes:
        ctx.text(node.name, dict(node.properties)["value"], x=5, y=20)
plugin.renderer("external-svg")(_svg)
"""
    fixture = installed_plugin_factory(manifest=manifest, module_source=source_code)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "source.art"
    source.write_text(
        'Output image.\nCreate text named t.\nSet value of t to "External".',
        encoding="utf-8",
    )
    destination = tmp_path / "result.svg"
    args = [
        "render",
        str(source),
        "--output",
        str(destination),
        "--representation",
        "external",
        "--renderer",
        "external-svg",
    ]
    rejected = CliRunner().invoke(app, args)
    assert rejected.exit_code == 2
    assert not marker.exists()
    accepted = CliRunner().invoke(app, [*args, "--plugin", "example"])
    assert accepted.exit_code == 0, accepted.output
    assert marker.exists()
    assert "External" in destination.read_text(encoding="utf-8")


def test_builtin_capabilities_and_validation_use_static_metadata(tmp_path, monkeypatch):
    import sys

    monkeypatch.delitem(sys.modules, "artifactspec.basic", raising=False)
    caps = CliRunner().invoke(
        app, ["capabilities", "--builtin-basic", "--details", "--output", "image"]
    )
    assert caps.exit_code == 0, caps.output
    plugins = json.loads(caps.output)["plugins"]
    assert any(plugin["id"] == "builtin-basic" for plugin in plugins)
    source = tmp_path / "source.art"
    source.write_text(
        'Output image.\nCreate text named t.\nSet value of t to "hello".',
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        app, ["validate", str(source), "--builtin-basic", "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["valid"] is True
    assert "artifactspec.basic" not in sys.modules


def test_builtin_static_metadata_matches_runtime_plugin():
    from artifactspec._basic_metadata import basic_manifest
    from artifactspec.basic import basic_plugin

    assert basic_manifest() == basic_plugin().manifest()


def test_cli_reports_legacy_warnings_and_explicit_no_fallback(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = {
        "schema_version": 1,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "phrases": [{"name": "text", "outputs": []}],
        "properties": [{"name": "value", "outputs": []}],
        "representations": [{"name": "legacy", "outputs": []}],
        "renderers": [{"name": "legacy-svg", "outputs": []}],
    }
    source_code = """from artifactspec.plugins import Plugin
from artifactspec.basic import _svg
plugin = Plugin("example", "1.0", outputs=("image",))
@plugin.phrase("text")
def create(ctx):
    ctx.create("text")
@plugin.property("value")
def assign(ctx):
    ctx.set("value", ctx.value)
@plugin.representation("legacy")
def layout(ctx):
    for node in ctx.content.nodes:
        ctx.text(node.name, dict(node.properties)["value"], x=5, y=20)
plugin.renderer("legacy-svg")(_svg)
"""
    fixture = installed_plugin_factory(manifest=manifest, module_source=source_code)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "source.art"
    source.write_text(
        'Output image.\nCreate text named t.\nSet value of t to "hello".',
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--plugin",
            "example",
            "--representation",
            "legacy",
            "--renderer",
            "legacy-svg",
            "--output",
            str(tmp_path / "image.svg"),
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert (data["renderer"], data["representation"], data["fallback"]) == (
        "legacy-svg",
        "legacy",
        None,
    )
    assert any(warning["code"] == "unverified_type" for warning in data["warnings"])
