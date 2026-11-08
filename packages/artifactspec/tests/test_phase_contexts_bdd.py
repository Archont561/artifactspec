from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "phase_contexts.feature")
)


@pytest.fixture
def state():
    return {}


@given("a typed text plugin using public phase contexts")
def text_plugin(state):
    from artifactspec.core.contexts import PhraseContext, PropertyContext
    from artifactspec.plugins import Plugin, Registry

    plugin = Plugin(
        "example",
        "1",
        outputs=("image", "report"),
        output_syntax={"image": "Output image.", "report": "Output report."},
    )

    @plugin.phrase("text", object_type="text", syntax="Create text named {name}.")
    def make_text(ctx: PhraseContext):
        ctx.create("text")

    @plugin.property(
        "value", target_types=("text",), syntax="Set value of {reference} to {value}."
    )
    def set_value(ctx: PropertyContext):
        ctx.set("value", ctx.value)

    registry = Registry()
    registry.register(plugin)
    state.update(plugin=plugin, registry=registry)


@when("a valid specification is converted into semantic content")
def build_content(state):
    from artifactspec.core.pipeline import build_content

    state["content"] = build_content(
        'Output image.\nCreate text named title.\nSet value of title to "Hello".',
        state["registry"],
        source="scene.art",
    )


@then("the content contains the declared text and source provenance")
def check_content(state):
    content = state["content"]
    assert len(content.nodes) == 1
    node = content.nodes[0]
    assert node.name == "title" and node.object_type == "text"
    assert dict(node.properties) == {"value": "Hello"}
    assert [span.start.line for span in node.provenance] == [2, 3]
    assert all(span.source == "scene.art" for span in node.provenance)


@then("the same plugin handlers can be exercised with fake contexts")
def check_fakes(state):
    from artifactspec.testing import FakePhraseContext, FakePropertyContext

    phrase = FakePhraseContext("title")
    prop = FakePropertyContext("title", "Hello")
    state["registry"].handler("phrases", "text")(phrase)
    state["registry"].handler("properties", "value")(prop)
    assert phrase.operations == [("create", "text")]
    assert prop.operations == [("set", "value", "Hello")]
