"""Safe declarative template parsing and validation."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from artifactspec.core.templates import TemplateError, compile_template
from artifactspec.plugin import Phrase, Property


@given(st.from_regex(r"[A-Za-z][A-Za-z0-9_-]{0,30}", fullmatch=True))
def test_name_template_matches_complete_identifiers(name):
    template = compile_template("Draw {name}.", {"name"})
    match = template.fullmatch(f"Draw {name}.")
    assert match is not None
    assert match.group("name") == name
    assert template.fullmatch(f"Draw {name}. extra") is None


@pytest.mark.parametrize(
    ("template", "fields"),
    [
        ("Draw {name}{name}.", {"name"}),
        ("Draw {name}{reference}.", {"name", "reference"}),
        ("Draw {name!r}.", {"name"}),
        ("Draw {name:20}.", {"name"}),
        ("Draw {unknown}.", {"name"}),
        ("Draw {name.", {"name"}),
        ("Draw nothing.", {"name"}),
    ],
)
def test_invalid_templates_are_rejected(template, fields):
    with pytest.raises(TemplateError):
        compile_template(template, fields)


def test_plugin_decorators_declare_templates_without_executing_handlers():
    from artifactspec.core.validation import validate
    from artifactspec.plugins import Plugin, Registry

    plugin = Plugin(
        "label",
        outputs={"image": "Make an image."},
        phrases=(Phrase("label", "label", "Draw {name}."),),
        properties=(
            Property("content", ("label",), "Write {value} onto {reference}."),
        ),
    )
    called = []

    @plugin.phrase("label")
    def label(context):
        called.append(context)

    @plugin.property("content")
    def content(context):
        called.append(context)

    registry = Registry()
    registry.register(plugin)
    result = validate(
        'Make an image.\nDraw title.\nWrite "Hello" onto title.', registry
    )
    assert result.valid, result.diagnostics
    assert called == []


def test_ambiguous_templates_are_reported_not_guessed():
    from artifactspec.core.validation import validate
    from artifactspec.plugins import ManifestCatalog

    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1",
        "outputs": ["image"],
        "output_syntax": {"image": "Image."},
        "phrases": [
            {
                "name": "one",
                "outputs": [],
                "object_type": "one",
                "syntax": "Draw {name}.",
            },
            {
                "name": "two",
                "outputs": [],
                "object_type": "two",
                "syntax": "Draw {name}.",
            },
        ],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    result = validate("Image.\nDraw a.", ManifestCatalog([manifest]))
    assert not result.valid
    assert result.diagnostics[0].code == "ambiguous_statement"
    assert result.diagnostics[0].span.start.line == 2


@pytest.mark.parametrize("version", [1, 2])
def test_legacy_manifest_versions_require_migration(version):
    from artifactspec.plugins import RegistrationError, validate_manifest

    legacy = {
        "schema_version": version,
        "id": "legacy",
        "version": "1",
        "outputs": ["image"],
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    with pytest.raises(RegistrationError, match="migrate to typed Plugin declarations"):
        validate_manifest(legacy)


def test_second_output_declaration_is_rejected_even_if_it_names_another_output():
    from artifactspec.core.validation import validate
    from artifactspec.plugins import ManifestCatalog

    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1",
        "outputs": ["image", "report"],
        "output_syntax": {"image": "Image.", "report": "Report."},
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    result = validate("Image.\nReport.", ManifestCatalog([manifest]))
    assert not result.valid
    assert result.diagnostics[0].code == "ambiguous_output"


def test_installed_template_metadata_validates_after_import(
    monkeypatch, installed_plugin_factory
):
    from artifactspec.core.validation import validate
    from artifactspec.plugins import ManifestCatalog
    from artifactspec.plugins.discovery import installed_plugins

    manifest = {
        "schema_version": 3,
        "id": "example",
        "version": "1.0",
        "outputs": ["image"],
        "output_syntax": {"image": "Image."},
        "phrases": [
            {
                "name": "square",
                "outputs": [],
                "object_type": "square",
                "syntax": "Square {name}.",
            }
        ],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    fixture = installed_plugin_factory(manifest=manifest)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    entries = installed_plugins(only={"example"})
    result = validate(
        "Image.\nSquare one.", ManifestCatalog([entries["example"].to_dict()])
    )
    assert result.valid, result.diagnostics
    assert fixture["marker"].exists()
