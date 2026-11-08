"""Tests for phase protocols, their fakes and trusted materialization."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from artifactspec.core.pipeline import PipelineError, build_content
from artifactspec.plugins import ManifestCatalog, Plugin, Registry
from artifactspec.testing import FakePhraseContext, FakePropertyContext

pytest_plugins = ["artifactspec.testing.pytest_plugin"]


def make_registry(phrase, property_handler):
    plugin = Plugin("test", "1", outputs=("image",), schema_version=2)
    plugin.phrase("text", object_type="text")(phrase)
    plugin.property("value", target_types=("text",))(property_handler)
    registry = Registry()
    registry.register(plugin)
    return registry


@given(value=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=50))
def test_content_property_round_trips_value_and_forward_reference(value):
    import json

    registry = make_registry(
        lambda ctx: ctx.create("text"), lambda ctx: ctx.set("value", ctx.value)
    )
    content = build_content(
        f"Output image.\nSet value of x to {json.dumps(value)}.\nCreate text named x.",
        registry,
    )
    assert dict(content.nodes[0].properties) == {"value": value}
    assert content.nodes[0].name == "x"
    assert [span.start.line for span in content.nodes[0].provenance] == [3, 2]


@pytest.mark.parametrize(
    "handler",
    [
        lambda ctx: None,
        lambda ctx: ctx.create("other"),
        lambda ctx: (ctx.create("text"), ctx.create("text")),
    ],
)
def test_invalid_phrase_behavior_is_rejected(handler):
    registry = make_registry(handler, lambda ctx: None)
    with pytest.raises(PipelineError, match="Phrase.*failed"):
        build_content("Output image.\nCreate text named x.", registry)


def test_validation_errors_never_execute_plugin_handlers():
    called = []
    registry = make_registry(
        lambda ctx: called.append("phrase"), lambda ctx: called.append("property")
    )
    with pytest.raises(PipelineError) as error:
        build_content(
            'Output image.\nCreate text named x.\nSet value of missing to "x".',
            registry,
        )
    assert error.value.diagnostics[0].code == "unresolved_reference"
    assert called == []
    with pytest.raises(TypeError, match="trusted runtime Registry"):
        build_content("Output image.", ManifestCatalog(registry.manifests()))


@pytest.mark.parametrize("bad_type", ["", " text", "text ", 42])
def test_fake_phrase_context_rejects_invalid_object_types(bad_type):
    with pytest.raises(ValueError):
        FakePhraseContext("x").create(bad_type)


@pytest.mark.parametrize("key", ["", " a", "a "])
def test_fake_property_context_rejects_invalid_keys(key):
    with pytest.raises(ValueError):
        FakePropertyContext("x", "v").set(key, "v")


def test_public_pytest_fixtures_supply_recording_fakes(
    artifactspec_phrase_context, artifactspec_property_context
):
    phrase = artifactspec_phrase_context("x")
    prop = artifactspec_property_context("x", "hello")
    phrase.create("text")
    prop.set("value", prop.value)
    assert phrase.operations == [("create", "text")]
    assert prop.operations == [("set", "value", "hello")]


def test_property_handler_must_make_an_assignment():
    registry = make_registry(lambda ctx: ctx.create("text"), lambda ctx: None)
    with pytest.raises(PipelineError, match="must set at least one property"):
        build_content(
            'Output image.\nCreate text named x.\nSet value of x to "v".', registry
        )


def test_property_handler_failure_is_source_linked():
    def fail(ctx):
        raise ValueError("unacceptable value")

    registry = make_registry(lambda ctx: ctx.create("text"), fail)
    with pytest.raises(
        PipelineError,
        match="Property 'value' failed at scene.art:3: unacceptable value",
    ):
        build_content(
            'Output image.\nCreate text named x.\nSet value of x to "v".',
            registry,
            source="scene.art",
        )
