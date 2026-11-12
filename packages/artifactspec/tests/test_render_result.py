"""Machine-readable rendering outcomes and composition-scoped provenance."""

import json
from xml.etree import ElementTree

import pytest
from artifactspec_svg.elements import Text
from hypothesis import given
from hypothesis import strategies as st
from typer.testing import CliRunner

from artifactspec.cli import app
from artifactspec.core.models import Composition, Element
from artifactspec.core.syntax import Position, SourceSpan
from artifactspec.plugin import Phrase, Representation

_EXACT_MANIFEST = {
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
    "representations": [{"name": "exact", "outputs": [], "target_types": ["text"]}],
    "renderers": [{"name": "exact-svg", "outputs": []}],
}


_EXACT_PLUGIN = """from html import escape
from artifactspec.plugin import Plugin, Phrase, Property, Representation, Renderer
plugin = Plugin("example", outputs={"image": "Output image."},
    phrases=(Phrase("text", "text", "Create text named {name}."),),
    properties=(Property("value", ("text",), "Set value of {reference} to {value}."),),
    representations=(Representation("exact", ("text",)),), renderers=(Renderer("exact-svg"),))
@plugin.phrase("text")
def create(ctx): ctx.create("text")
@plugin.property("value")
def assign(ctx): ctx.set("value", ctx.value)
@plugin.representation("exact")
def layout(ctx):
    for node in ctx.content.nodes:
        ctx.add(node.name, (20, 40, dict(node.properties)["value"]))
@plugin.renderer("exact-svg")
def render(ctx):
    x, y, text = ctx.composition.elements[0].value
    svg = f'<svg xmlns="http://www.w3.org/2000/svg"><text x="{x}" y="{y}">{escape(text)}</text></svg>'
    ctx.emit(svg.encode("utf-8"), media_type="image/svg+xml", editable=True)
"""


_BROKEN_MANIFEST = {
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
    "properties": [],
    "representations": [{"name": "layout", "outputs": [], "target_types": ["text"]}],
    "renderers": [{"name": "broken", "outputs": []}],
}


_BROKEN_PLUGIN = """from artifactspec.plugin import Plugin, Phrase, Representation, Renderer
plugin = Plugin("example", outputs={"image": "Output image."},
    phrases=(Phrase("text", "text", "Create text named {name}."),),
    representations=(Representation("layout", ("text",)),), renderers=(Renderer("broken"),))
@plugin.phrase("text")
def create(ctx): ctx.create("text")
@plugin.representation("layout")
def layout(ctx):
    ctx.warn("layout limitation")
    ctx.add(ctx.content.nodes[0].name, "x")
@plugin.renderer("broken")
def broken(ctx):
    ctx.warn("renderer limitation")
    raise ValueError("renderer broke")
"""


@given(st.lists(st.booleans(), max_size=12))
def test_provenance_status_distinguishes_missing_and_empty_elements(linked):
    from artifactspec.core.rendering import _composition_provenance

    span = SourceSpan("scene.art", Position(2, 1), Position(2, 5))
    elements = tuple(
        Element(Text(0, index, "text", "black", 20), (span,) if has_link else ())
        for index, has_link in enumerate(linked)
    )
    composition = Composition("image", "diagram", 640, 480, elements)
    spans, status = _composition_provenance(composition)
    if not linked:
        expected = "no_elements"
    elif all(linked):
        expected = "available"
    elif any(linked):
        expected = "partial"
    else:
        expected = "unavailable"
    assert status == expected
    assert spans == ((span,) if any(linked) else ())


def invoke(source, destination, *, representation="diagram", renderer="svg", extra=()):
    return CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--representation",
            representation,
            "--renderer",
            renderer,
            "--output",
            str(destination),
            "--format",
            "json",
            *extra,
        ],
    )


@pytest.mark.parametrize(
    "spec,representation,renderer,code,exit_code",
    [
        (
            'Output image.\nSet value of missing to "x".',
            "diagram",
            "svg",
            "validation_failed",
            1,
        ),
        (
            "Output image.\nCreate text named x.",
            "absent",
            "svg",
            "capability_selection_failed",
            2,
        ),
        (
            'Output image.\nCreate event named x.\nSet date of x to "2024-02-30".',
            "diagram",
            "svg",
            "property_failed",
            2,
        ),
        (
            "Output image.\nCreate event named x.",
            "diagram",
            "svg",
            "representation_failed",
            2,
        ),
        (
            'Output image.\nCreate text named x.\nSet color of x to "url(x)".',
            "diagram",
            "svg",
            "renderer_failed",
            2,
        ),
    ],
)
def test_json_failure_is_structured_and_preserves_destination(
    tmp_path, spec, representation, renderer, code, exit_code
):
    source = tmp_path / "source.art"
    source.write_text(spec, encoding="utf-8")
    destination = tmp_path / "out.svg"
    destination.write_text("existing", encoding="utf-8")
    result = invoke(
        source, destination, representation=representation, renderer=renderer
    )
    assert result.exit_code == exit_code, result.output
    data = json.loads(result.stdout)
    assert data["schema_version"] == 1 and data["status"] == "error"
    assert data["error"]["code"] == code
    assert data["error"]["message"]
    assert destination.read_text(encoding="utf-8") == "existing"
    if code == "validation_failed":
        assert data["diagnostics"][0]["code"] == "unresolved_reference"
        assert data["diagnostics"][0]["span"]["source"] == str(source)


def test_json_read_error_and_plugin_error(tmp_path):
    source = tmp_path / "missing.art"
    destination = tmp_path / "out.svg"
    result = invoke(source, destination)
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "io_error"
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
            str(destination),
            "--format",
            "json",
            "--plugin",
            "missing",
        ],
    )
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "plugin_error"


def test_empty_composition_is_distinct_from_unavailable_provenance(tmp_path):
    source = tmp_path / "source.art"
    source.write_text("Output image.", encoding="utf-8")
    destination = tmp_path / "out.svg"
    result = invoke(source, destination)
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["provenance"] == []
    assert data["provenance_status"] == "no_elements"


def test_exact_synthetic_renderer_reports_no_limitations_without_claiming_fidelity(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = _EXACT_MANIFEST
    plugin = _EXACT_PLUGIN
    fixture = installed_plugin_factory(manifest=manifest, module_source=plugin)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "source.art"
    source.write_text(
        'Output image.\nCreate text named t.\nSet value of t to "exact text".',
        encoding="utf-8",
    )
    dest = tmp_path / "out.svg"
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--no-plugin-autoload",
            "--plugin",
            "example",
            "--representation",
            "exact",
            "--renderer",
            "exact-svg",
            "--output",
            str(dest),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    element = ElementTree.parse(dest).getroot().find("{http://www.w3.org/2000/svg}text")
    assert element.text == "exact text"
    assert element.attrib == {"x": "20", "y": "40"}
    assert data["status"] == "success" and data["limitations"] == []
    assert data["fallback"] is None and data["provenance_status"] == "available"
    assert "fidelity" not in data


def _install_validation_warning(monkeypatch, rendering):
    from artifactspec.core.validation import Diagnostic, ValidationResult

    original_validate = rendering.validate

    def validate_with_warning(*args, **kwargs):
        result = original_validate(*args, **kwargs)
        warning = Diagnostic(
            "custom_warning", "warning", "check this", result.document.output_span
        )
        return ValidationResult(
            result.document, (*result.diagnostics, warning), result.resolutions
        )

    monkeypatch.setattr(rendering, "validate", validate_with_warning)


def test_failure_keeps_validation_warnings_and_phase_limitations(
    tmp_path, monkeypatch, installed_plugin_factory
):
    manifest = _BROKEN_MANIFEST
    plugin = _BROKEN_PLUGIN
    from artifactspec.core import rendering

    _install_validation_warning(monkeypatch, rendering)
    fixture = installed_plugin_factory(manifest=manifest, module_source=plugin)
    monkeypatch.syspath_prepend(str(fixture["path"]))
    source = tmp_path / "source.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    dest = tmp_path / "out.svg"
    dest.write_text("old", encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render",
            str(source),
            "--no-plugin-autoload",
            "--plugin",
            "example",
            "--representation",
            "layout",
            "--renderer",
            "broken",
            "--output",
            str(dest),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 2, result.output
    data = json.loads(result.stdout)
    assert data["error"]["code"] == "renderer_failed"
    assert any(item["code"] == "custom_warning" for item in data["warnings"])
    assert data["limitations"] == ["layout limitation", "renderer limitation"]
    assert data["fallback"] is None
    assert dest.read_text(encoding="utf-8") == "old"


def test_json_write_failure_has_separate_code(tmp_path):
    source = tmp_path / "source.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    result = invoke(source, tmp_path / "missing" / "out.svg")
    assert result.exit_code == 2
    data = json.loads(result.stdout)
    assert data["error"]["code"] == "output_write_failed"
    assert data["limitations"]


@pytest.mark.parametrize(
    "linked,expected", [([False], "unavailable"), ([True, False], "partial")]
)
def test_render_propagates_incomplete_composition_provenance(
    tmp_path, monkeypatch, linked, expected
):
    from artifactspec.core import rendering

    span = SourceSpan("scene.art", Position(2, 1), Position(2, 5))
    elements = tuple(
        Element(Text(0, index, "text", "black", 20), (span,) if has_link else ())
        for index, has_link in enumerate(linked)
    )
    composition = Composition("image", "diagram", 640, 480, elements)
    monkeypatch.setattr(rendering, "compose", lambda *args, **kwargs: composition)
    source = tmp_path / "source.art"
    source.write_text("Output image.\nCreate text named t.", encoding="utf-8")
    result = invoke(source, tmp_path / "out.svg")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["provenance_status"] == expected
    assert len(data["provenance"]) == (1 if any(linked) else 0)


def test_invalid_utf8_is_a_json_io_failure(tmp_path):
    source = tmp_path / "source.art"
    source.write_bytes(b"\xff")
    result = invoke(source, tmp_path / "out.svg")
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "io_error"


def test_default_failure_output_remains_text_on_stderr(tmp_path):
    source = tmp_path / "source.art"
    source.write_text('Output image.\nSet value of missing to "x".', encoding="utf-8")
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
        ],
    )
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "unresolved_reference" in result.stderr


def test_representation_failure_keeps_limitations_for_api_call():
    from artifactspec.core.models import Content, ContentNode
    from artifactspec.core.pipeline import PipelineError
    from artifactspec.core.rendering import compose
    from artifactspec.plugins import Plugin, Registry

    plugin = Plugin(
        "test",
        outputs={"image": "Output image."},
        representations=(Representation("layout", ("text",)),),
    )

    @plugin.representation("layout")
    def layout(context):
        context.warn("partial layout")
        raise ValueError("not supported")

    registry = Registry()
    registry.register(plugin)
    with pytest.raises(PipelineError, match="not supported") as error:
        compose(
            Content((ContentNode("x", "text", (), ()),)),
            output="image",
            representation="layout",
            registry=registry,
        )
    assert error.value.code == "representation_failed"
    assert error.value.limitations == ("partial layout",)


def test_json_format_cannot_override_typer_argument_parse_errors():
    result = CliRunner().invoke(app, ["render", "--format", "json"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "Missing" in result.stderr


def test_validation_failure_preserves_warnings_with_errors(tmp_path, monkeypatch):
    from artifactspec.core import rendering
    from artifactspec.core.pipeline import PipelineError
    from artifactspec.core.validation import Diagnostic, ValidationResult
    from artifactspec.plugins import Plugin, Registry

    plugin = Plugin(
        "test",
        outputs={"image": "Output image."},
        phrases=(Phrase("text", "text", "Create text named {name}."),),
    )
    plugin.phrase("text")(lambda ctx: ctx.create("text"))
    registry = Registry()
    registry.register(plugin)
    original = rendering.validate

    def validate_with_warning(*args, **kwargs):
        result = original(*args, **kwargs)
        warning = Diagnostic(
            "custom_warning", "warning", "check this", result.document.output_span
        )
        return ValidationResult(
            result.document, (*result.diagnostics, warning), result.resolutions
        )

    monkeypatch.setattr(rendering, "validate", validate_with_warning)
    with pytest.raises(PipelineError) as error:
        rendering.render(
            "Output image.\nCreate text named t.\nCreate text named t.",
            registry,
            representation="missing",
            renderer="missing",
            destination=tmp_path / "result",
        )
    assert error.value.code == "validation_failed"
    assert any(item.code == "duplicate_name" for item in error.value.diagnostics)
    assert any(item.code == "custom_warning" for item in error.value.warnings)
