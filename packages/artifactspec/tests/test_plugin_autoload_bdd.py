"""Installed plugin discovery remains static while rendering autoloads code."""

import json
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when
from typer.testing import CliRunner

from artifactspec.cli import app

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "plugin_autoload.feature")
)


@pytest.fixture
def state():
    return {}


@given("an installed rendering plugin with an import marker")
@given("a rendering plugin installed in the environment")
@given("a rendering plugin available for explicit selection")
def plugin(state, tmp_path, monkeypatch, installed_plugin_factory):
    marker = tmp_path / "loaded"
    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Output image."},
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [{"name": "example-svg", "outputs": []}],
    }
    source = f"""from pathlib import Path
Path({str(marker)!r}).write_text("loaded")
from artifactspec.plugins import Plugin
plugin = Plugin("example", "1.0", outputs=("image",), output_syntax={{"image": "Output image."}})
@plugin.renderer("example-svg")
def render(ctx):
    ctx.emit(b"example artifact", media_type="image/svg+xml", editable=True)
"""
    fixture = installed_plugin_factory(manifest=manifest, module_source=source)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    state["marker"] = marker
    state["source"] = tmp_path / "scene.art"
    state["source"].write_text("Output image.\nCreate text named t.", encoding="utf-8")
    state["destination"] = tmp_path / "scene.svg"


@when("I inspect installed capabilities")
def capabilities(state):
    state["result"] = CliRunner().invoke(app, ["capabilities", "--details"])


@then("the plugin is listed without executing its code")
def static_discovery(state):
    assert state["result"].exit_code == 0, state["result"].output
    assert any(
        item["id"] == "example"
        for item in json.loads(state["result"].stdout)["plugins"]
    )
    assert not state["marker"].exists()


def run(state, extra):
    state["result"] = CliRunner().invoke(
        app,
        [
            "render",
            str(state["source"]),
            "--representation",
            "diagram",
            "--renderer",
            "example-svg",
            "--output",
            str(state["destination"]),
            *extra,
        ],
    )


@when("I render with its backend without naming the plugin")
def automatic(state):
    run(state, [])


@when("I disable plugin autoload and render without selecting it")
def disable(state):
    run(state, ["--no-plugin-autoload"])


@when("I explicitly select that plugin with autoload disabled")
def explicit(state):
    run(state, ["--no-plugin-autoload", "--plugin", "example", "--plugin", "svg"])


@then("rendering fails without importing the plugin")
def not_loaded(state):
    assert state["result"].exit_code == 1
    assert not state["marker"].exists()
    assert not state["destination"].exists()


@then("the plugin is loaded and the artifact is written")
def loaded(state):
    assert state["result"].exit_code == 0, state["result"].output
    assert state["marker"].exists()
    assert state["destination"].read_bytes() == b"example artifact"


def test_autoload_rejects_conflicts_before_importing_plugins(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Output image."},
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [{"name": "svg", "outputs": []}],
    }
    fixture = installed_plugin_factory(manifest=manifest)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "scene.art"
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
    assert json.loads(result.stdout)["error"]["code"] == "plugin_error"
    assert "conflicting renderers" in json.loads(result.stdout)["error"]["message"]
    assert not fixture["marker"].exists()
    selected = CliRunner().invoke(
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
            "--no-plugin-autoload",
            "--plugin",
            "svg",
        ],
    )
    assert selected.exit_code == 0, selected.output
    assert not fixture["marker"].exists()


def test_autoload_failure_can_be_avoided_with_explicit_opt_out(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Output image."},
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [{"name": "broken", "outputs": []}],
    }
    fixture = installed_plugin_factory(
        manifest=manifest, module_source="raise RuntimeError('import failed')\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "scene.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    args = [
        "render",
        str(source),
        "--representation",
        "diagram",
        "--renderer",
        "svg",
        "--output",
        str(tmp_path / "out.svg"),
    ]
    failure = CliRunner().invoke(app, args)
    assert failure.exit_code == 2 and "import failed" in failure.output
    success = CliRunner().invoke(
        app, [*args, "--no-plugin-autoload", "--plugin", "svg"]
    )
    assert success.exit_code == 0, success.output


def test_validation_and_language_server_do_not_import_plugins(
    tmp_path, monkeypatch, installed_plugin_factory
):
    from artifactspec.editor import lsp

    fixture = installed_plugin_factory(
        module_source="raise RuntimeError('must not import')\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "scene.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    validation = CliRunner().invoke(app, ["validate", str(source), "--format", "json"])
    assert validation.exit_code == 0, validation.output
    assert json.loads(validation.stdout)["valid"]
    started = []

    class FakeServer:
        def start_io(self):
            started.append(True)

    monkeypatch.setattr(lsp, "create_server", lambda catalog: FakeServer())
    lsp.start()
    assert started == [True]
    assert not fixture["marker"].exists()
