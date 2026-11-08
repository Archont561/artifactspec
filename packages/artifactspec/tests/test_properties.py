"""Property-based tests for the standalone language and metadata functions."""

import json
import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from artifactspec.core.parser import ParseError, parse
from artifactspec.core.validation import validate
from artifactspec.editor.lsp import _LanguageDocument, _position
from artifactspec.plugins import (
    ManifestCatalog,
    Plugin,
    RegistrationError,
    check_conflicts,
    filter_manifests,
    validate_manifest,
)

letters = string.ascii_letters
identifier = st.builds(
    lambda head, tail: head + tail,
    st.sampled_from(letters),
    st.text(alphabet=letters + string.digits + "_-", max_size=15),
).filter(lambda name: name != "it")
value_text = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=40)


def typed_catalog():
    plugin = Plugin("shapes", "1", outputs=("image",), schema_version=2)
    plugin.phrase("circle", object_type="circle")(lambda context: pytest.fail("called"))
    plugin.property("label", target_types=("circle",))(
        lambda context: pytest.fail("called")
    )
    return ManifestCatalog([plugin.manifest()])


@settings(deadline=None)
@given(name=identifier, value=value_text, indent=st.text(alphabet=" \t", max_size=8))
def test_parse_round_trips_json_values_and_source_spans(name, value, indent):
    literal = json.dumps(value, ensure_ascii=False)
    line = f"{indent}Set label of {name} to {literal}."
    document = parse(
        f"Output image.\nCreate circle named {name}.\n{line}",
        typed_catalog(),
        source="generated.art",
    )
    statement = document.statements[1]
    assert statement.reference.name == name
    assert statement.value.value == value
    name_start = len(indent) + len("Set label of ")
    assert statement.reference.span.start.column == name_start + 1
    assert statement.reference.span.end.column == name_start + len(name) + 1
    assert statement.value.span.start.column == name_start + len(name) + len(" to ") + 1
    assert statement.value.span.end.column == len(line)
    assert statement.value.span.source == "generated.art"


@settings(deadline=None)
@given(
    names=st.lists(identifier, min_size=1, max_size=8, unique=True), value=value_text
)
def test_validation_resolves_forward_and_latest_references(names, value):
    literal = json.dumps(value, ensure_ascii=False)
    before = f"Set label of {names[0]} to {literal}."
    creates = [f"Create circle named {name}." for name in names]
    result = validate(
        "\n".join(
            ["Output image.", before, *creates, f"Set label of it to {literal}."]
        ),
        typed_catalog(),
    )
    assert result.valid
    assert result.diagnostics == ()
    assert [item.target.name for item in result.resolutions] == [names[0], names[-1]]


@settings(deadline=None)
@given(name=identifier, value=value_text)
def test_duplicate_definitions_remain_ambiguous(name, value):
    literal = json.dumps(value, ensure_ascii=False)
    result = validate(
        f"Output image.\nCreate circle named {name}.\nCreate circle named {name}.\nSet label of {name} to {literal}.",
        typed_catalog(),
    )
    assert not result.valid
    assert [item.code for item in result.diagnostics] == [
        "duplicate_name",
        "duplicate_name",
        "ambiguous_reference",
    ]
    assert result.resolutions == ()


@settings(deadline=None)
@given(name=identifier.filter(lambda name: name != "image"))
def test_unsupported_output_never_silently_parses(name):
    with pytest.raises(ParseError) as error:
        parse(f"Output {name}.", typed_catalog())
    assert error.value.code == "unknown_output"


@given(outputs=st.lists(identifier, unique=True, max_size=8))
def test_manifest_normalization_is_idempotent_and_filter_independent(outputs):
    data = {
        "schema_version": 1,
        "id": "example",
        "version": "1",
        "outputs": outputs,
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    normalized = validate_manifest(data)
    assert normalized["outputs"] == sorted(outputs)
    assert validate_manifest(normalized) == normalized
    assert filter_manifests([data]) == [normalized]
    for output in outputs:
        filtered = filter_manifests([data], output=output)
        assert len(filtered) == 1 and filtered[0]["outputs"] == [output]
    assert data["outputs"] == outputs


@given(output=identifier)
def test_duplicate_outputs_and_plugin_id_conflicts_are_rejected(output):
    data = {
        "schema_version": 1,
        "id": "example",
        "version": "1",
        "outputs": [output, output],
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    with pytest.raises(RegistrationError, match="duplicate"):
        validate_manifest(data)
    data["outputs"] = [output]
    with pytest.raises(RegistrationError, match="duplicate plugin id"):
        check_conflicts([validate_manifest(data), validate_manifest(data)])


@settings(deadline=None)
@given(object_type=identifier, target_type=identifier)
def test_declared_types_are_matched_exactly(object_type, target_type):
    plugin = Plugin("typed", "1", outputs=("image",), schema_version=2)
    plugin.phrase("thing", object_type=object_type)(lambda ctx: None)
    plugin.property("label", target_types=(target_type,))(lambda ctx: None)
    result = validate(
        'Output image.\nCreate thing named x.\nSet label of x to "x".',
        ManifestCatalog([plugin.manifest()]),
    )
    assert result.valid == (object_type == target_type)
    assert [item.code for item in result.diagnostics] == (
        [] if object_type == target_type else ["wrong_type"]
    )


@given(text=value_text, prefix_length=st.integers(min_value=0, max_value=40))
def test_lsp_positions_use_utf16_units(text, prefix_length):
    # A single line avoids client line splitting and exercises non-BMP characters.
    text = text.replace("\r", " ").replace("\n", " ")
    length = min(prefix_length, len(text))
    document = _LanguageDocument("file:///test.art", source=text)
    result = _position(document, 1, length + 1)
    assert (result.line, result.character) == (
        0,
        len(text[:length].encode("utf-16-le")) // 2,
    )


@given(
    outputs=st.lists(identifier, unique=True, max_size=8),
    details=st.booleans(),
    selected=st.one_of(st.none(), identifier),
)
def test_capability_discovery_matches_filtered_static_metadata(
    outputs, details, selected
):
    from unittest.mock import patch

    from artifactspec.plugins import discovery

    manifest = {
        "schema_version": 1,
        "id": "example",
        "version": "1",
        "outputs": outputs,
        "phrases": [{"name": "circle", "outputs": []}],
        "properties": [],
        "representations": [],
        "renderers": [],
    }
    with patch.object(
        discovery, "installed_plugins", return_value={"example": (None, manifest)}
    ):
        result = discovery.capabilities(details=details, output=selected)
    assert result["schema_version"] == 1
    if selected is not None and selected not in outputs:
        assert result["plugins"] == []
    else:
        entry = result["plugins"][0]
        assert entry["outputs"] == (sorted(outputs) if selected is None else [selected])
        assert entry["capabilities"]["phrases"] == (
            [{"name": "circle", "outputs": []}] if details else 1
        )
        assert manifest["outputs"] == outputs


@settings(max_examples=25, deadline=None)
@given(
    names=st.lists(
        st.text(alphabet=string.ascii_lowercase, min_size=2, max_size=8),
        min_size=1,
        max_size=5,
        unique=True,
    )
)
def test_command_discovery_registers_all_public_modules(names):
    import sys
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    from typer.testing import CliRunner

    from artifactspec import commands
    from artifactspec.cli import create_app

    with tempfile.TemporaryDirectory() as directory:
        for name in names:
            (Path(directory) / f"{name}.py").write_text(
                f"import typer\napp = typer.Typer()\n@app.command({name!r})\ndef run():\n    pass\n",
                encoding="utf-8",
            )
        module_names = [f"artifactspec.commands.{name}" for name in names]
        # Preserve unrelated imports and restore only modules created in this case.
        previous = {
            name: sys.modules.pop(name) for name in module_names if name in sys.modules
        }
        absent = object()
        previous_attributes = {name: getattr(commands, name, absent) for name in names}
        try:
            with patch.object(commands, "__path__", [directory]):
                app = create_app()
                result = CliRunner().invoke(app, ["--help"])
                assert result.exit_code == 0
                from typer.main import get_command

                assert sorted(get_command(app).commands) == sorted(names)
                assert [group.typer_instance for group in app.registered_groups] == [
                    sys.modules[f"artifactspec.commands.{name}"].app
                    for name in sorted(names)
                ]
        finally:
            for module_name in module_names:
                sys.modules.pop(module_name, None)
            sys.modules.update(previous)
            for name, value in previous_attributes.items():
                if value is absent:
                    if hasattr(commands, name):
                        delattr(commands, name)
                else:
                    setattr(commands, name, value)


@settings(max_examples=25, deadline=None)
@given(
    depth=st.integers(min_value=1, max_value=5),
    text=st.text(alphabet=string.ascii_letters, min_size=1, max_size=12),
)
def test_nested_command_trees_invoke_the_correct_leaf(depth, text):
    import typer
    from typer.testing import CliRunner

    from artifactspec.cli import _check_command_tree

    root = typer.Typer()
    current = root
    for _ in range(depth):
        child = typer.Typer()
        current.add_typer(child, name="next")
        current = child

        @current.command("show")
        def show():
            typer.echo(text)

    _check_command_tree(root, set(), (), set())
    for level in range(1, depth + 1):
        result = CliRunner().invoke(root, [*["next"] * level, "show"])
        assert result.exit_code == 0, result.output
        assert result.output == text + "\n"


@given(text=value_text)
def test_source_lines_preserve_content_and_only_split_lsp_newlines(text):
    import re

    from artifactspec.core._lines import source_lines

    lines = source_lines(text)
    assert "".join(lines) == text
    assert len(lines) == len(re.findall(r"\r\n|\r|\n", text)) + 1
    assert all(line.endswith(("\r", "\n")) for line in lines[:-1])
    assert "\r" not in lines[-1] and "\n" not in lines[-1]


@settings(deadline=None)
@given(newline=st.sampled_from(["\n", "\r\n", "\r"]), value=value_text)
def test_parser_positions_follow_lsp_line_endings(newline, value):
    text = newline.join(
        [
            "Output image.",
            "Create circle named x.",
            f"Set label of x to {json.dumps(value)}.",
        ]
    )
    document = parse(text, typed_catalog())
    assert document.statements[0].span.start.line == 2
    assert document.statements[1].span.start.line == 3
    assert document.statements[1].value.value == value
