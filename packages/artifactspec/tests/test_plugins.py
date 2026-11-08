import json
import os
import subprocess
import sys
from importlib import metadata

import pytest

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
        "1",
        outputs=("svg", "pdf"),
        output_syntax={"svg": "Output svg.", "pdf": "Output pdf."},
    )

    def handler(context):
        return context

    assert (
        plugin.phrase("one", object_type="one", syntax="Create {name}.")(handler)
        is handler
    )
    assert (
        plugin.property(
            "one", target_types=("one",), syntax="Set {reference} {value}."
        )(handler)
        is handler
    )
    assert plugin.representation("one", target_types=("one",))(handler) is handler
    assert plugin.renderer("one")(handler) is handler
    registry = Registry()
    registry.register(plugin)
    actual = registry.manifests()[0]
    assert actual["outputs"] == ["pdf", "svg"]
    assert actual["phrases"][0]["syntax"] == "Create {name}."
    assert actual["properties"][0]["target_types"] == ["one"]
    assert actual["representations"][0]["target_types"] == ["one"]
    assert actual["renderers"] == [{"name": "one", "outputs": []}]
    with pytest.raises(RegistrationError, match="frozen"):
        plugin.phrase("new", object_type="new", syntax="New {name}.")(lambda x: x)
    result = registry.manifests()
    result[0]["outputs"].clear()
    assert registry.manifests()[0]["outputs"] == ["pdf", "svg"]
    assert registry.manifests(output="gif") == []


def test_invalid_registration_is_atomic():
    registry = Registry()
    first = Plugin("one", "1", outputs=("svg",), output_syntax={"svg": "Output svg."})
    registry.register(first)
    with pytest.raises(RegistrationError, match="duplicate plugin id"):
        registry.register(Plugin("one", "2"))
    with pytest.raises(RegistrationError, match="expected a Plugin"):
        registry.register(None)
    with pytest.raises(RegistrationError, match="unsupported outputs"):
        Plugin(
            "two", "1", outputs=("svg",), output_syntax={"svg": "Output svg."}
        ).renderer("bad", outputs=("pdf",))(lambda x: x)
    plugin = Plugin("three", "1")
    plugin.property(
        "name", target_types=("thing",), syntax="Set name of {reference} to {value}."
    )(lambda x: x)
    with pytest.raises(RegistrationError, match="duplicate"):
        plugin.property(
            "name",
            target_types=("thing",),
            syntax="Set name of {reference} to {value}.",
        )(lambda x: x)
    with pytest.raises(RegistrationError, match="callable"):
        plugin.phrase("other", object_type="other", syntax="Create other {name}.")(None)
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


def test_static_discovery_and_loading(installed_plugin_factory, monkeypatch):
    source = """from artifactspec.plugins import Plugin
plugin = Plugin("example", "1.0", outputs=("svg", "pdf"), output_syntax={"svg": "Output svg.", "pdf": "Output pdf."})
@plugin.phrase("draw", outputs=("svg",), object_type="draw", syntax="Draw {name}.")
def draw(context):
    return context
"""
    fixture = installed_plugin_factory(module_source=source)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    assert "example" in installed_plugins()
    assert (
        next(item for item in capabilities()["plugins"] if item["id"] == "example")[
            "capabilities"
        ]["phrases"]
        == 1
    )
    assert (
        capabilities(output="pdf", details=True)["plugins"][0]["capabilities"][
            "phrases"
        ]
        == []
    )
    assert capabilities(output="gif")["plugins"] == []
    registry = Registry()
    registry.load_installed("example")
    assert registry.manifests()[0] == validate_manifest(fixture["manifest"])
    with pytest.raises(RegistrationError, match="duplicate plugin"):
        registry.load_installed("example")
    with pytest.raises(RegistrationError, match="not found"):
        registry.load_installed("missing")
    monkeypatch.delitem(sys.modules, "fixture_plugin", raising=False)


def test_untrusted_discovery_and_failed_load(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory(
        module_source="raise RuntimeError('unsafe load')\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    assert "example" in installed_plugins()
    with pytest.raises(RegistrationError, match="unsafe load"):
        Registry().load_installed("example")


def test_manifest_runtime_mismatch(installed_plugin_factory, monkeypatch):
    fixture = installed_plugin_factory(
        module_source="from artifactspec.plugins import Plugin\nplugin = Plugin('example', 'different')\n"
    )
    monkeypatch.syspath_prepend(str(fixture["path"]))
    with pytest.raises(RegistrationError, match="does not match"):
        Registry().load_installed("example")
    monkeypatch.delitem(sys.modules, "fixture_plugin", raising=False)


def test_broken_metadata_reports_error_without_loading(
    installed_plugin_factory, monkeypatch
):
    fixture = installed_plugin_factory()
    monkeypatch.syspath_prepend(str(fixture["path"]))
    fixture["manifest_path"].write_text("not json", encoding="utf-8")
    with pytest.raises(RegistrationError, match="cannot read manifest"):
        installed_plugins()
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(fixture["path"]), env.get("PYTHONPATH", "")]
    )
    proc = subprocess.run(
        [sys.executable, "-m", "artifactspec", "capabilities"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 1
    assert not proc.stdout and "cannot read manifest" in proc.stderr
    assert not fixture["marker"].exists()
    fixture["manifest_path"].write_text(
        json.dumps({"schema_version": 2}), encoding="utf-8"
    )
    with pytest.raises(RegistrationError, match="invalid manifest"):
        installed_plugins()
    fixture["manifest_path"].unlink()
    # importlib.metadata changed whether RECORD entries for missing files are
    # retained: both forms must fail with an actionable diagnostic.
    with pytest.raises(
        RegistrationError, match="missing or duplicated|cannot read manifest"
    ):
        installed_plugins()
    (fixture["info"] / "RECORD").write_text("", encoding="utf-8")
    with pytest.raises(RegistrationError, match="file records"):
        installed_plugins()


def test_duplicate_installed_ids(installed_plugin_factory, monkeypatch):
    first = installed_plugin_factory()
    second = installed_plugin_factory(module="other_plugin")
    monkeypatch.syspath_prepend(str(first["path"]))
    with pytest.raises(RegistrationError, match="duplicate plugin id"):
        installed_plugins()
    assert not first["marker"].exists() and not second["marker"].exists()


def test_invalid_entry_and_missing_file_records(monkeypatch):
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
    entry = metadata.EntryPoint(
        name="ok", value="pkg:plugin", group="artifactspec.plugins"
    )
    monkeypatch.setattr(metadata, "entry_points", lambda **kwargs: [entry])
    with pytest.raises(RegistrationError, match="file records"):
        installed_plugins()


def test_registration_conflicts_are_output_independent():
    a = Plugin("a", "1", outputs=("svg",), output_syntax={"svg": "Output svg."})
    b = Plugin("b", "1", outputs=("pdf",), output_syntax={"pdf": "Output pdf."})
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
        "1",
        outputs=("svg", "pdf"),
        output_syntax={"svg": "Output svg.", "pdf": "Output pdf."},
    )

    @plugin.phrase(
        "circle",
        outputs=("svg", "pdf"),
        object_type="circle",
        syntax="Create circle {name}.",
    )
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
    with pytest.raises(RegistrationError, match="not a string"):
        Plugin("a", "1", outputs="svg")
    plugin = Plugin("a", "1", outputs=("svg",), output_syntax={"svg": "Output svg."})
    with pytest.raises(RegistrationError, match="not a string"):
        plugin.phrase("a", outputs="svg", object_type="a", syntax="Create a {name}.")(
            lambda x: x
        )
    with pytest.raises(RegistrationError, match="iterable"):
        Plugin("a", "1", outputs=None)


def test_installed_contribution_conflicts_are_deterministic(
    installed_plugin_factory, monkeypatch
):
    first = installed_plugin_factory(plugin_id="example", module="plugin_a")
    installed_plugin_factory(plugin_id="another", module="plugin_b")
    monkeypatch.syspath_prepend(str(first["path"]))
    with pytest.raises(RegistrationError, match="phrases.*draw.*another.*example"):
        installed_plugins()
    assert not first["marker"].exists()


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
    assert json.loads(filtered.stdout) == {"schema_version": 1, "plugins": []}
    assert not fixture["marker"].exists()
