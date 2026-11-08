"""Generated and regression tests for explicit, safe rendering."""

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
from artifactspec_events.plugin import plugin as event_plugin
from hypothesis import given, settings
from hypothesis import strategies as st

from artifactspec.core.models import Content, ContentNode
from artifactspec.core.pipeline import PipelineError, build_content
from artifactspec.core.rendering import compose, render
from artifactspec.plugin import Phrase, Renderer, Representation
from artifactspec.plugins import Plugin, Registry

pytest_plugins = ["artifactspec.testing.pytest_plugin"]


def registry():
    result = Registry()
    result.register(event_plugin)
    from artifactspec_svg.plugin import plugin as svg_plugin

    result.register(svg_plugin)
    return result


xml_character = st.characters(
    blacklist_categories=("Cs", "Cc"), blacklist_characters="\ufffe\uffff"
)


@settings(max_examples=50, deadline=None)
@given(value=st.text(alphabet=xml_character, max_size=80))
def test_svg_preserves_arbitrary_valid_text_and_escapes_markup(value):
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "image.svg"
        source = f"Output image.\nCreate text named t.\nSet value of t to {json.dumps(value)}."
        result = render(
            source,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=destination,
        )
        root = ElementTree.parse(destination).getroot()
        assert (root.find("{http://www.w3.org/2000/svg}text").text or "") == value
        assert result.artifact.editable


@pytest.mark.parametrize(
    "representation,renderer", [("missing", "svg"), ("diagram", "missing")]
)
def test_missing_capability_does_not_replace_existing_file(
    tmp_path, representation, renderer
):
    destination = tmp_path / "output.svg"
    destination.write_bytes(b"old")
    with pytest.raises(PipelineError):
        render(
            "Output image.\nCreate text named t.",
            registry(),
            representation=representation,
            renderer=renderer,
            destination=destination,
        )
    assert destination.read_bytes() == b"old"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize(
    "value",
    ["url(https://evil.example/)", 'red" onload="alert(1)', "#invalid", "rgb(0,0,0)"],
)
def test_unsafe_colors_are_rejected_without_replacing_output(tmp_path, value):
    destination = tmp_path / "output.svg"
    destination.write_bytes(b"old")
    spec = (
        f"Output image.\nCreate text named t.\nSet color of t to {json.dumps(value)}."
    )
    with pytest.raises(PipelineError, match="unsupported SVG color"):
        render(
            spec,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=destination,
        )
    assert destination.read_bytes() == b"old"


def test_xml_forbidden_character_does_not_create_file(tmp_path):
    destination = tmp_path / "output.svg"
    spec = 'Output image.\nCreate text named t.\nSet value of t to "\\u0000".'
    with pytest.raises(PipelineError, match="forbidden by XML"):
        render(
            spec,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=destination,
        )
    assert not destination.exists()


def test_report_representation_does_not_claim_a_report_renderer(tmp_path):
    spec = 'Output report.\nCreate event named e.\nSet date of e to "2000-01-01".\nSet label of e to "Hello".'
    content = build_content(spec, registry())
    composition = compose(
        content, output="report", representation="diagram", registry=registry()
    )
    assert composition.elements[0].text == "2000-01-01: Hello"
    with pytest.raises(PipelineError, match="no renderers"):
        render(
            spec,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=tmp_path / "report",
        )


def test_missing_or_duplicate_artifacts_are_rejected(tmp_path):
    for handler in (
        lambda ctx: None,
        lambda ctx: (
            ctx.emit(b"x", media_type="text/plain", editable=True),
            ctx.emit(b"y", media_type="text/plain", editable=True),
        ),
    ):
        plugin = Plugin(
            "custom",
            outputs={"image": "Output image."},
            renderers=(Renderer("custom", ("image",)),),
        )
        plugin.renderer("custom")(handler)
        reg = registry()
        reg.register(plugin)
        destination = tmp_path / "image"
        with pytest.raises(PipelineError, match="exactly one artifact"):
            render(
                "Output image.\nCreate text named t.",
                reg,
                representation="diagram",
                renderer="custom",
                destination=destination,
            )
        assert not destination.exists()


def test_fakes_record_representation_and_renderer_operations(
    artifactspec_representation_context, artifactspec_renderer_context
):
    content = Content((ContentNode("x", "text", (("value", "hello"),), ()),))
    rep = artifactspec_representation_context(content)
    rep.text("x", "hello", x=1, y=2)
    output = artifactspec_renderer_context(rep.finish())
    output.emit(b"hello", media_type="text/plain", editable=True)
    assert rep.elements[0].text == "hello"
    assert output.artifact == (b"hello", "text/plain", True)
    with pytest.raises(ValueError, match="unknown content"):
        rep.text("missing", "bad", x=1, y=2)


def test_same_event_content_supports_distinct_image_and_report_compositions():
    reg = registry()
    content = build_content(
        'Output image.\nCreate event named e.\nSet date of e to "2000-01-01".\nSet label of e to "Shared".',
        reg,
    )
    image = compose(content, output="image", representation="diagram", registry=reg)
    report = compose(content, output="report", representation="diagram", registry=reg)
    assert image.elements[0].text == "2000-01-01 — Shared"
    assert report.elements[0].text == "2000-01-01: Shared"
    assert image.limitations and report.limitations


def test_basic_layout_overflow_is_explicit_and_preserves_destination(tmp_path):
    destination = tmp_path / "image.svg"
    destination.write_bytes(b"old")
    text = "Output image.\n" + "\n".join(f"Create text named n{i}." for i in range(7))
    with pytest.raises(PipelineError, match="exceeds the fixed canvas"):
        render(
            text,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=destination,
        )
    assert destination.read_bytes() == b"old"


def test_carriage_return_is_preserved_in_svg_text(tmp_path):
    destination = tmp_path / "image.svg"
    text = 'Output image.\nCreate text named t.\nSet value of t to "before\\rafter".'
    result = render(
        text,
        registry(),
        representation="diagram",
        renderer="svg",
        destination=destination,
    )
    root = ElementTree.parse(destination).getroot()
    assert root.find("{http://www.w3.org/2000/svg}text").text == "before\rafter"
    assert result.limitations


def test_renderer_failure_after_emitting_does_not_replace_existing_file(tmp_path):
    def failing(ctx):
        ctx.emit(b"partial", media_type="text/plain", editable=True)
        raise RuntimeError("broken")

    plugin = Plugin(
        "broken", outputs={"image": "Output image."}, renderers=(Renderer("broken"),)
    )
    plugin.renderer("broken")(failing)
    reg = registry()
    reg.register(plugin)
    destination = tmp_path / "out.svg"
    destination.write_bytes(b"old")
    with pytest.raises(PipelineError, match="broken"):
        render(
            "Output image.\nCreate text named t.",
            reg,
            representation="diagram",
            renderer="broken",
            destination=destination,
        )
    assert destination.read_bytes() == b"old"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out.svg"]


def test_atomic_write_failure_removes_temporary_file(tmp_path, monkeypatch):
    def fail_replace(self, target):
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "replace", fail_replace)
    destination = tmp_path / "out.svg"
    destination.write_bytes(b"old")
    with pytest.raises(PipelineError, match="permission denied"):
        render(
            "Output image.\nCreate text named t.",
            registry(),
            representation="diagram",
            renderer="svg",
            destination=destination,
        )
    assert destination.read_bytes() == b"old"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out.svg"]


def test_unsupported_semantic_properties_are_not_silently_dropped():
    from artifactspec.core.models import ContentNode

    content = Content((ContentNode("x", "text", (("size", "30"),), ()),))
    with pytest.raises(PipelineError, match="cannot express properties"):
        compose(content, output="image", representation="diagram", registry=registry())


def test_invalid_named_svg_color_fails_instead_of_silent_default(tmp_path):
    spec = 'Output image.\nCreate text named x.\nSet color of x to "notacolor".'
    with pytest.raises(PipelineError, match="unsupported SVG color"):
        render(
            spec,
            registry(),
            representation="diagram",
            renderer="svg",
            destination=tmp_path / "x.svg",
        )


def test_unavailable_renderer_is_rejected_before_plugin_handlers_run(tmp_path):
    called = []
    plugin = Plugin(
        "test-preflight",
        outputs={"image": "Output image."},
        phrases=(Phrase("item", "item", "Create item named {name}."),),
        representations=(Representation("layout", ("item",)),),
    )
    plugin.phrase("item")(lambda ctx: called.append("phrase"))
    plugin.representation("layout")(lambda ctx: called.append("representation"))
    reg = Registry()
    reg.register(plugin)
    with pytest.raises(PipelineError, match="no renderers"):
        render(
            "Output image.\nCreate item named x.",
            reg,
            representation="layout",
            renderer="missing",
            destination=tmp_path / "image",
        )
    assert called == []


def test_result_explicitly_reports_no_fallback(tmp_path):
    result = render(
        "Output image.\nCreate text named x.",
        registry(),
        representation="diagram",
        renderer="svg",
        destination=tmp_path / "x.svg",
    )
    assert result.fallback is None
