from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

from artifactspec.core.models import Content, ContentNode
from artifactspec.core.rendering import compose
from artifactspec.plugin import Representation
from artifactspec.plugins import Plugin, Registry

scenarios(
    str(
        Path(__file__).resolve().parents[1]
        / "features"
        / "composable_plugin_representations.feature"
    )
)


@pytest.fixture
def state():
    return {}


@given("independently registered shape and event plugins")
def register_plugins(state):
    shapes = Plugin(
        "shapes",
        outputs={"image": "Image."},
        representations=(Representation("diagram", ("shape",)),),
    )
    events = Plugin(
        "events",
        outputs={"image": "Image."},
        representations=(Representation("diagram", ("event",)),),
    )

    @shapes.representation("diagram")
    def shape(context):
        context.rectangle(
            context.node.name, x=0, y=context.index * 40, width=10, height=10
        )

    @events.representation("diagram")
    def event(context):
        context.text(context.node.name, "event", x=0, y=context.index * 40)

    state["registry"] = Registry()
    state["registry"].register(shapes)
    state["registry"].register(events)


@when("I compose their objects using the shared representation")
def compose_objects(state):
    content = Content(
        (ContentNode("box", "shape", (), ()), ContentNode("launch", "event", (), ()))
    )
    state["composition"] = compose(
        content, output="image", representation="diagram", registry=state["registry"]
    )


@then("their visual elements appear together in declaration order")
def check_elements(state):
    from artifactspec.core.models import RectangleElement, TextElement

    elements = state["composition"].elements
    assert isinstance(elements[0], RectangleElement)
    assert isinstance(elements[1], TextElement)
    assert elements[1].y == 40


def test_overlapping_representation_target_types_are_rejected():
    from artifactspec.plugins import RegistrationError

    registry = Registry()
    for index in range(2):
        plugin = Plugin(
            f"p{index}",
            outputs={"image": "Image."},
            representations=(Representation("diagram", ("same",)),),
        )
        plugin.representation("diagram")(lambda context: None)
        if index == 0:
            registry.register(plugin)
        else:
            with pytest.raises(RegistrationError, match="conflicting representations"):
                registry.register(plugin)


def test_unknown_representation_target_type_fails():
    from artifactspec.core.pipeline import PipelineError

    plugin = Plugin(
        "shapes",
        outputs={"image": "Image."},
        representations=(Representation("diagram", ("shape",)),),
    )
    plugin.representation("diagram")(lambda context: None)
    registry = Registry()
    registry.register(plugin)
    content = Content((ContentNode("unknown", "unregistered", (), ()),))
    with pytest.raises(PipelineError, match="no representation.*unregistered"):
        compose(content, output="image", representation="diagram", registry=registry)


def test_fake_representation_context_exposes_current_node_and_index():
    from artifactspec.testing import FakeRepresentationContext

    node = ContentNode("launch", "event", (), ())
    context = FakeRepresentationContext(Content((node,)), index=0)
    assert context.node == node
    assert context.index == 0
