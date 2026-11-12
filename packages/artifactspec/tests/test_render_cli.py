"""Integration checks for explicit plugin approval and CLI render failures."""

import json

import pytest
from typer.testing import CliRunner

from artifactspec.cli import app

_EXTERNAL_MANIFEST = {
    "schema_version": 3,
    "id": "example",
    "version": "1.0",
    "outputs": ["image"],
    "output_syntax": {"image": "Output image."},
    "phrases": [
        {
            "name": "text",
            "outputs": [],
            "object_type": "text",
            "syntax": "Create text named {name}.",
        }
    ],
    "properties": [
        {
            "name": "value",
            "outputs": [],
            "target_types": ["text"],
            "syntax": "Set value of {reference} to {value}.",
        }
    ],
    "representations": [{"name": "external", "outputs": [], "target_types": ["text"]}],
    "renderers": [{"name": "external-svg", "outputs": []}],
}


def _external_source(marker):
    return f"""from pathlib import Path
Path({str(marker)!r}).write_text("loaded")
from artifactspec.plugin import Plugin, Phrase, Property, Representation, Renderer
from html import escape
plugin = Plugin("example", outputs={{"image": "Output image."}},
    phrases=(Phrase("text", "text", "Create text named {{name}}."),),
    properties=(Property("value", ("text",), "Set value of {{reference}} to {{value}}."),),
    representations=(Representation("external", ("text",)),), renderers=(Renderer("external-svg"),))
@plugin.phrase("text")
def create(ctx):
    ctx.create("text")
@plugin.property("value")
def apply(ctx):
    ctx.set("value", ctx.value)
@plugin.representation("external")
def layout(ctx):
    for node in ctx.content.nodes:
        ctx.add(node.name, dict(node.properties)["value"])
@plugin.renderer("external-svg")
def render(ctx):
    text = escape(ctx.composition.elements[0].value)
    ctx.emit(f"<svg>{{text}}</svg>".encode(), media_type="image/svg+xml", editable=True)
"""


@pytest.mark.parametrize(
    "extra,expected",
    [(["--plugin", "not-installed"], "not found")],
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
            "diagram",
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
            "diagram",
            "--renderer",
            "svg",
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
        "diagram",
        "--renderer",
        "svg",
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
            "diagram",
            "--renderer",
            "svg",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["limitations"]


def test_cli_loads_only_explicitly_approved_installed_plugin(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = _EXTERNAL_MANIFEST
    marker = tmp_path / "executed"
    source_code = _external_source(marker)
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
        "--no-plugin-autoload",
    ]
    rejected = CliRunner().invoke(app, args)
    assert rejected.exit_code != 0
    assert not marker.exists()
    accepted = CliRunner().invoke(app, [*args, "--plugin", "example"])
    assert accepted.exit_code == 0, accepted.output
    assert marker.exists()
    assert "External" in destination.read_text(encoding="utf-8")


def test_installed_capabilities_and_validation_use_plugin_objects(tmp_path):
    caps = CliRunner().invoke(app, ["capabilities", "--details", "--output", "image"])
    assert caps.exit_code == 0, caps.output
    assert any(item["id"] == "svg" for item in json.loads(caps.output)["plugins"])
    source = tmp_path / "source.art"
    source.write_text(
        'Output image.\nCreate text named t.\nSet value of t to "hello".',
        encoding="utf-8",
    )
    result = CliRunner().invoke(app, ["validate", str(source), "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["valid"]
    assert CliRunner().invoke(app, ["capabilities", "--builtin-basic"]).exit_code != 0


def test_non_plugin_entrypoint_is_rejected(
    tmp_path, monkeypatch, installed_plugin_factory
):
    fixture = installed_plugin_factory(module_source="plugin = object()\n")
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "source.art"
    source.write_text("Output image.", encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(tmp_path / "out.svg"),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 2
    assert "Plugin object" in json.loads(result.stdout)["error"]["message"]
