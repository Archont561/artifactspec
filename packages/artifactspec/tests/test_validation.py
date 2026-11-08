import pytest

from artifactspec.core.validation import validate
from artifactspec.plugin import Phrase, Property
from artifactspec.plugins import (
    ManifestCatalog,
    Plugin,
    RegistrationError,
    Registry,
    validate_manifest,
)


@pytest.fixture
def typed_registry():
    plugin = Plugin(
        "typed",
        outputs={"image": "Output image.", "animation": "Output animation."},
        phrases=(
            Phrase("circle", "circle", "Create circle named {name}.", ("image",)),
            Phrase("text", "text", "Create text named {name}."),
        ),
        properties=(
            Property(
                "color", ("circle",), "Set color of {reference} to {value}.", ("image",)
            ),
        ),
    )
    plugin.phrase("circle")(lambda ctx: pytest.fail("executed"))
    plugin.phrase("text")(lambda ctx: pytest.fail("executed"))
    plugin.property("color")(lambda ctx: pytest.fail("executed"))
    registry = Registry()
    registry.register(plugin)
    return registry


def test_forward_named_and_nearest_it_are_scoped_per_document(typed_registry):
    result = validate(
        'Output image.\nSet color of a to "x".\nCreate circle named a.\nCreate circle named b.\nSet color of it to "x".',
        typed_registry,
    )
    assert result.valid
    assert [item.target.name for item in result.resolutions] == ["a", "b"]
    result = validate(
        'Output image.\nSet color of it to "x".\nSet color of a to "x".', typed_registry
    )
    assert [item.code for item in result.diagnostics] == [
        "unresolved_reference",
        "unresolved_reference",
    ]
    assert all(item.span.start.line in (2, 3) for item in result.diagnostics)


def test_duplicate_names_and_ambiguous_references_are_reported(typed_registry):
    result = validate(
        'Output image.\nCreate circle named a.\nCreate circle named a.\nSet color of a to "x".',
        typed_registry,
    )
    assert not result.valid
    assert [item.code for item in result.diagnostics] == [
        "duplicate_name",
        "duplicate_name",
        "ambiguous_reference",
    ]
    assert result.resolutions == ()


def test_invalid_type_and_unavailable_output(typed_registry):
    result = validate(
        'Output image.\nCreate text named a.\nSet color of a to "x".',
        typed_registry,
        source="in.art",
    )
    assert result.diagnostics[0].code == "wrong_type"
    assert result.diagnostics[0].span.source == "in.art"
    result = validate("Output animation.\nCreate circle named a.", typed_registry)
    assert result.diagnostics[0].code == "unknown_statement"
    assert not result.valid


def test_static_catalog_validates_without_plugin_code(typed_registry):
    catalog = ManifestCatalog(typed_registry.manifests())
    result = validate(
        'Output image.\nCreate circle named a.\nSet color of a to "x".', catalog
    )
    assert result.valid and not result.diagnostics
    assert catalog.manifests(output="animation")[0]["phrases"][0]["name"] == "text"


def test_version_three_metadata_is_required_and_preserved(typed_registry):
    manifest = typed_registry.manifests()[0]
    assert manifest["schema_version"] == 3
    assert manifest["phrases"][0]["object_type"] == "circle"
    assert manifest["properties"][0]["target_types"] == ["circle"]
    broken = {**manifest, "phrases": [{"name": "circle", "outputs": []}]}
    with pytest.raises(RegistrationError):
        validate_manifest(broken)
    broken = {
        **manifest,
        "properties": [{"name": "color", "outputs": [], "target_types": []}],
    }
    with pytest.raises(RegistrationError):
        validate_manifest(broken)


@pytest.mark.parametrize("schema_version", [1, 2])
def test_legacy_declarations_require_migration(schema_version):
    with pytest.raises(RegistrationError, match="migrate to typed Plugin declarations"):
        validate_manifest({"schema_version": schema_version})


def test_catalog_rejects_conflicts_and_never_exposes_mutable_state(typed_registry):
    source = typed_registry.manifests()
    with pytest.raises(RegistrationError, match="duplicate plugin"):
        ManifestCatalog(source + source)
    catalog = ManifestCatalog(source)
    source[0]["phrases"].clear()
    retrieved = catalog.manifests()
    assert len(retrieved[0]["phrases"]) == 2
    retrieved[0]["phrases"].clear()
    assert len(catalog.manifests()[0]["phrases"]) == 2


def test_typed_declarations_require_complete_valid_metadata():
    with pytest.raises(RegistrationError, match="target types"):
        Plugin(
            "typed",
            outputs={"image": "Output image."},
            properties=(Property("color", (), "Set color of {reference} to {value}."),),
        )
    with pytest.raises(RegistrationError, match="phrases must contain"):
        Plugin("typed", outputs={}, phrases=({"name": "circle"},))
    with pytest.raises(RegistrationError, match="object type"):
        Plugin("typed", outputs={}, phrases=(Phrase("circle", "", "Create {name}."),))


def test_bad_syntax_returns_source_linked_error(typed_registry):
    result = validate(
        "Output image.\nNot a statement.", typed_registry, source="bad.art"
    )
    assert not result.valid and result.document is None
    assert result.diagnostics[0].code == "unknown_statement"
    assert result.diagnostics[0].span.start.line == 2
    assert result.diagnostics[0].span.source == "bad.art"


def test_installed_plugin_metadata_is_available_after_import(
    installed_plugin_factory, monkeypatch
):
    from artifactspec.plugins.discovery import installed_plugins

    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Output image."},
        "phrases": [
            {
                "name": "circle",
                "outputs": [],
                "object_type": "circle",
                "syntax": "Create circle named {name}.",
            }
        ],
        "properties": [
            {
                "name": "color",
                "outputs": [],
                "target_types": ["circle"],
                "syntax": "Set color of {reference} to {value}.",
            }
        ],
        "representations": [],
        "renderers": [],
    }
    fixture = installed_plugin_factory(manifest=manifest)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    catalog = ManifestCatalog(
        item.to_dict() for item in installed_plugins(only={"example"}).values()
    )
    result = validate(
        'Output image.\nCreate circle named c.\nSet color of c to "red".', catalog
    )
    assert result.valid and not result.diagnostics
    assert fixture["marker"].exists()


def test_validation_cli_human_and_json_diagnostics(
    typed_registry, tmp_path, monkeypatch
):
    import json

    from typer.testing import CliRunner

    from artifactspec import cli
    from artifactspec.cli.commands import validate as validate_command

    monkeypatch.setattr(
        validate_command,
        "load_cli_registry",
        lambda **kwargs: typed_registry,
    )
    path = tmp_path / "scene.art"
    path.write_text('Output image.\nSet color of missing to "red".', encoding="utf-8")
    runner = CliRunner()
    text = runner.invoke(cli.app, ["validate", str(path)])
    assert text.exit_code == 1
    assert f"{path}:2:14: error [unresolved_reference]" in text.output
    result = runner.invoke(cli.app, ["validate", str(path), "--format", "json"])
    assert result.exit_code == 1
    diagnostic = json.loads(result.output)["diagnostics"][0]
    assert diagnostic["severity"] == "error" and diagnostic["message"]
    assert diagnostic["span"]["start"] == {"line": 2, "column": 14}
    path.write_text("Output image.\nCreate not-known named x.", encoding="utf-8")
    result = runner.invoke(cli.app, ["validate", str(path), "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.output)["diagnostics"][0]["code"] == "unknown_statement"
    path.write_text("Output image.\nCreate circle named x.", encoding="utf-8")
    result = runner.invoke(cli.app, ["validate", str(path)])
    assert result.exit_code == 0 and "valid" in result.output


def test_cli_reports_missing_file_without_fake_validation_result(tmp_path):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    result = CliRunner().invoke(
        app, ["validate", str(tmp_path / "missing.art"), "--format", "json"]
    )
    assert result.exit_code == 2
    assert "artifactspec:" in result.stderr


def test_capability_json_includes_plugin_syntax(installed_plugin_factory, monkeypatch):
    from artifactspec.plugins.discovery import capabilities

    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Output image."},
        "phrases": [
            {
                "name": "circle",
                "outputs": [],
                "object_type": "circle",
                "syntax": "Create circle named {name}.",
            }
        ],
        "properties": [
            {
                "name": "color",
                "outputs": [],
                "target_types": ["circle"],
                "syntax": "Set color of {reference} to {value}.",
            }
        ],
        "representations": [],
        "renderers": [],
    }
    fixture = installed_plugin_factory(manifest=manifest)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    item = capabilities(details=True, only={"example"})["plugins"][0]
    assert item["phrases"][0]["syntax"] == "Create circle named {name}."
    assert item["properties"][0]["target_types"] == ["circle"]
    assert fixture["marker"].exists()
