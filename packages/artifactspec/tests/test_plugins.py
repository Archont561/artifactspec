import json
import os
import subprocess
import sys
from importlib import metadata

import pytest

from artifactspec.plugin import Phrase, Property, Renderer, Representation
from artifactspec.plugins import Plugin, RegistrationError, Registry, validate_manifest
from artifactspec.plugins.discovery import capabilities, installed_plugins


def manifest():
    return {
        "schema_version": 3,
        "id": "one",
        "version": "1",
        "outputs": ["svg", "pdf"],
        "output_syntax": {"svg": "Output svg.", "pdf": "Output pdf."},
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }


def test_decorators_and_freezing():
    plugin = Plugin(
        "one",
        outputs={"svg": "Output svg.", "pdf": "Output pdf."},
        phrases=(
            Phrase("one", "one", "Create {name}."),
            Phrase("new", "new", "New {name}."),
        ),
        properties=(Property("one", ("one",), "Set {reference} {value}."),),
        representations=(Representation("one", ("one",)),),
        renderers=(Renderer("one"),),
    )

    def handler(context):
        return context

    assert plugin.phrase("one")(handler) is handler
    assert plugin.property("one")(handler) is handler
    assert plugin.representation("one")(handler) is handler
    assert plugin.renderer("one")(handler) is handler
    registry = Registry()
    registry.register(plugin)
    actual = registry.manifests()[0]
    assert actual["outputs"] == ["pdf", "svg"]
    assert (
        next(item for item in actual["phrases"] if item["name"] == "one")["syntax"]
        == "Create {name}."
    )
    assert actual["version"] is None
    assert actual["properties"][0]["target_types"] == ["one"]
    assert actual["representations"][0]["target_types"] == ["one"]
    assert actual["renderers"] == [{"name": "one", "outputs": []}]
    with pytest.raises(RegistrationError, match="frozen"):
        plugin.phrase("new")(lambda x: x)
    result = registry.manifests()
    result[0]["outputs"].clear()
    assert registry.manifests()[0]["outputs"] == ["pdf", "svg"]
    assert registry.manifests(output="gif") == []


def test_invalid_registration_is_atomic():
    registry = Registry()
    registry.register(Plugin("one", outputs={"svg": "Output svg."}))
    with pytest.raises(RegistrationError, match="duplicate plugin id"):
        registry.register(Plugin("one", outputs={}))
    with pytest.raises(RegistrationError, match="expected a Plugin"):
        registry.register(None)
    with pytest.raises(RegistrationError, match="unsupported outputs"):
        Plugin(
            "two",
            outputs={"svg": "Output svg."},
            renderers=(Renderer("bad", ("pdf",)),),
        )
    plugin = Plugin(
        "three",
        outputs={},
        properties=(Property("name", ("thing",), "Set {reference} {value}."),),
    )
    plugin.property("name")(lambda x: x)
    with pytest.raises(RegistrationError, match="duplicate"):
        plugin.property("name")(lambda x: x)
    with pytest.raises(RegistrationError, match="callable"):
        plugin.property("name")(None)
    with pytest.raises(RegistrationError, match="undeclared"):
        plugin.phrase("unknown")(lambda x: x)
    assert [p["id"] for p in registry.manifests()] == ["one"]


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda m: m.pop("id"), "exactly"),
        (lambda m: m.update(schema_version=True), "schema"),
        (lambda m: m.update(id="Bad/id"), "plugin id"),
        (lambda m: m.update(version=""), "version"),
        (lambda m: m.update(outputs="svg"), "list"),
        (lambda m: m.update(outputs=["svg", "svg"]), "duplicate"),
        (lambda m: m.update(outputs=[" svg"]), "whitespace"),
        (lambda m: m.update(phrases={}), "list"),
        (lambda m: m.update(phrases=[{"name": "x"}]), "object_type"),
        (
            lambda m: m.update(
                phrases=[
                    {
                        "name": "x",
                        "outputs": ["gif"],
                        "object_type": "x",
                        "syntax": "Create x {name}.",
                    }
                ]
            ),
            "unsupported",
        ),
        (
            lambda m: m.update(
                phrases=[
                    {
                        "name": "x",
                        "outputs": [],
                        "object_type": "x",
                        "syntax": "Create x {name}.",
                    }
                ]
                * 2
            ),
            "duplicate",
        ),
    ],
)
def test_invalid_manifest(change, message):
    data = manifest()
    change(data)
    with pytest.raises(RegistrationError, match=message):
        validate_manifest(data)


def test_manifest_expected_id():
    with pytest.raises(RegistrationError, match="does not match"):
        validate_manifest(manifest(), expected_id="other")
    with pytest.raises(RegistrationError, match="manifest must be an object"):
        validate_manifest([])


def test_object_discovery_and_loading(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory()
    monkeypatch.syspath_prepend(str(fixture["path"]))
    found = installed_plugins(only={"example"})
    assert fixture["marker"].exists()
    assert found["example"].to_dict() == validate_manifest(fixture["manifest"])
    assert capabilities(only={"example"})["plugins"][0]["capabilities"]["phrases"] == 1
    assert (
        capabilities(output="pdf", details=True, only={"example"})["plugins"][0][
            "phrases"
        ]
        == []
    )
    registry = Registry()
    registry.load_installed("example")
    assert registry.plugin("example") is found["example"]
    with pytest.raises(RegistrationError, match="duplicate plugin"):
        registry.load_installed("example")
    with pytest.raises(RegistrationError, match="not found"):
        registry.load_installed("missing")


def test_import_failures_are_reported(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory(
        module_source="raise RuntimeError('unsafe load')\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    with pytest.raises(RegistrationError, match="unsafe load"):
        installed_plugins(only={"example"})
    with pytest.raises(RegistrationError, match="unsafe load"):
        Registry().load_installed("example")


def test_entry_id_must_match_plugin_id(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory(
        module_source="from artifactspec.plugin import Plugin\nplugin = Plugin('different', outputs={})\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    with pytest.raises(RegistrationError, match="does not match"):
        Registry().load_installed("example")


def test_wrong_entrypoint_object_is_rejected(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory(module_source="plugin = object()\n")
    monkeypatch.syspath_prepend(str(fixture["path"]))
    with pytest.raises(RegistrationError, match="Plugin object"):
        installed_plugins(only={"example"})


def test_duplicate_installed_ids(installed_plugin_factory, monkeypatch):
    first = installed_plugin_factory()
    second = installed_plugin_factory(module="other_plugin")
    monkeypatch.syspath_prepend(str(first["path"]))
    with pytest.raises(RegistrationError, match="duplicate plugin id"):
        installed_plugins()
    assert not first["marker"].exists() and not second["marker"].exists()


def test_invalid_entrypoints(monkeypatch):
    entry = metadata.EntryPoint(
        name="Bad/id", value="pkg:plugin", group="artifactspec.plugins"
    )
    monkeypatch.setattr(metadata, "entry_points", lambda **kwargs: [entry])
    with pytest.raises(RegistrationError, match="invalid plugin entry"):
        installed_plugins()
    entry = metadata.EntryPoint(
        name="ok", value="not valid", group="artifactspec.plugins"
    )
    monkeypatch.setattr(metadata, "entry_points", lambda **kwargs: [entry])
    with pytest.raises(RegistrationError, match="invalid entry point"):
        installed_plugins()


def test_registration_conflicts_are_output_independent():
    a = Plugin("a", outputs={"svg": "Output svg."}, renderers=(Renderer("render"),))
    b = Plugin(
        "b",
        outputs={"pdf": "Output pdf."},
        renderers=(
            Renderer("render"),
            Renderer("still mutable"),
        ),
    )
    a.renderer("render")(lambda x: x)
    b.renderer("render")(lambda x: x)
    registry = Registry()
    registry.register(a)
    with pytest.raises(
        RegistrationError, match="conflicting renderers.*render.*'a'.*'b'"
    ):
        registry.register(b)
    assert len(registry.manifests()) == 1
    b.renderer("still mutable")(lambda x: x)


def test_handlers_respect_output_and_filter_narrows_contribution():
    plugin = Plugin(
        "draw",
        outputs={"svg": "Output svg.", "pdf": "Output pdf."},
        phrases=(Phrase("circle", "circle", "Create circle {name}.", ("svg", "pdf")),),
    )

    @plugin.phrase("circle")
    def draw(context):
        return context

    registry = Registry()
    registry.register(plugin)
    assert registry.handler("phrases", "circle", output="svg") is draw
    assert registry.manifests(output="svg")[0]["phrases"] == [
        {
            "name": "circle",
            "outputs": ["svg"],
            "object_type": "circle",
            "syntax": "Create circle {name}.",
        }
    ]
    with pytest.raises(RegistrationError, match="unknown capability"):
        registry.handler("bad", "circle")
    with pytest.raises(RegistrationError, match="no phrases"):
        registry.handler("phrases", "circle", output="gif")


def test_output_arguments_reject_strings():
    with pytest.raises(RegistrationError, match="map"):
        Plugin("a", outputs="svg")
    with pytest.raises(RegistrationError, match="list"):
        Plugin(
            "a",
            outputs={"svg": "Output svg."},
            phrases=(Phrase("a", "a", "Create {name}.", "svg"),),
        )
    with pytest.raises(RegistrationError, match="map"):
        Plugin("a", outputs=None)


def test_installed_contribution_conflicts_are_deterministic(
    installed_plugin_factory, monkeypatch
):
    first = installed_plugin_factory(plugin_id="example", module="plugin_a")
    installed_plugin_factory(plugin_id="another", module="plugin_b")
    monkeypatch.syspath_prepend(str(first["path"]))
    with pytest.raises(RegistrationError, match="phrases.*draw.*another.*example"):
        installed_plugins()
    assert first["marker"].exists()


def test_cli_summary_and_unknown_output(installed_plugin_factory):
    fixture = installed_plugin_factory()
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(fixture["path"]), env.get("PYTHONPATH", "")]
    )
    command = [sys.executable, "-m", "artifactspec", "capabilities"]
    summary = subprocess.run(
        command, env=env, text=True, capture_output=True, check=True
    )
    assert [
        item
        for item in json.loads(summary.stdout)["plugins"]
        if item["id"] == "example"
    ] == [
        {
            "id": "example",
            "version": "1.0",
            "outputs": ["pdf", "svg"],
            "capabilities": {
                "phrases": 1,
                "properties": 0,
                "representations": 0,
                "renderers": 0,
            },
        }
    ]
    filtered = subprocess.run(
        command + ["--output", "unknown"],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(filtered.stdout) == {"schema_version": 2, "plugins": []}
    assert fixture["marker"].exists()


def test_declarations_serialize_independently_and_missing_handlers_fail_cleanly():
    plugin = Plugin(
        id="standalone",
        outputs={"image": "Image."},
        phrases=[Phrase("shape", "shape", "Draw {name}.")],
        representations=[Representation("diagram", ("shape",))],
    )
    assert plugin.to_dict()["version"] is None
    data = plugin.to_dict()
    data["phrases"][0]["syntax"] = "changed"
    assert plugin.to_dict()["phrases"][0]["syntax"] == "Draw {name}."
    registry = Registry()
    registry.register(plugin)
    with pytest.raises(RegistrationError, match="no handler registered"):
        registry.handler("phrases", "shape", output="image")
    with pytest.raises(RegistrationError, match="no handler registered"):
        registry.representation_handler("diagram", "shape", output="image")


def test_cli_import_prints_cannot_corrupt_json(installed_plugin_factory, monkeypatch):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    fixture = installed_plugin_factory(
        module_source="from artifactspec.plugin import Plugin\nprint('import noise')\nplugin = Plugin('example', outputs={})\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    result = CliRunner().invoke(
        app,
        ["capabilities", "--no-plugin-autoload", "--plugin", "example", "--details"],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["plugins"][0]["id"] == "example"
    assert "import noise" in result.stderr


def test_capabilities_selection_skips_unselected_broken_plugin(
    installed_plugin_factory, monkeypatch
):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    fixture = installed_plugin_factory(module_source="raise RuntimeError('broken')\n")
    monkeypatch.syspath_prepend(str(fixture["path"]))
    runner = CliRunner()
    failed = runner.invoke(app, ["capabilities"])
    assert failed.exit_code == 1 and "broken" in failed.stderr
    selected = runner.invoke(
        app, ["capabilities", "--no-plugin-autoload", "--plugin", "svg"]
    )
    assert selected.exit_code == 0
    assert [item["id"] for item in json.loads(selected.stdout)["plugins"]] == ["svg"]


def test_distribution_identity_binding_is_consistent_and_atomic():
    plugin = Plugin("direct", outputs={})
    with pytest.raises(RegistrationError, match="version"):
        plugin._bind_distribution("first", "")
    assert plugin.to_dict()["version"] is None
    plugin._bind_distribution("first", "1.5")
    plugin._bind_distribution("first", "1.5")
    with pytest.raises(RegistrationError, match="multiple distributions"):
        plugin._bind_distribution("second", "2")
    assert plugin.to_dict()["version"] == "1.5"


def test_entrypoint_without_distribution_metadata_fails(monkeypatch):
    from types import SimpleNamespace

    plugin = Plugin("orphan", outputs={})
    entry = SimpleNamespace(
        name="orphan",
        value="orphan:plugin",
        module="orphan",
        attr="plugin",
        dist=None,
        load=lambda: plugin,
    )
    monkeypatch.setattr(metadata, "entry_points", lambda **kwargs: [entry])
    with pytest.raises(RegistrationError, match="distribution metadata missing"):
        installed_plugins()
    assert plugin.to_dict()["version"] is None
