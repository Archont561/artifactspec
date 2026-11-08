from pathlib import Path
from xml.etree import ElementTree

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "plugin_elements.feature")
)


@pytest.fixture
def state():
    return {}


@given("an SVG composition with plugin-owned rectangle and text elements")
def composition(state):
    from artifactspec_svg.elements import Rectangle, Text

    from artifactspec.core.models import Composition, Element

    state["composition"] = Composition(
        "image",
        "diagram",
        640,
        480,
        (
            Element(Rectangle(1, 2, 30, 40, "navy"), ()),
            Element(Text(5, 6, "A & <B>", "black", 20), ()),
        ),
    )


@when("the SVG composition is serialized")
def serialize(state):
    from artifactspec_svg.syntax import serialize_svg

    state["root"] = ElementTree.fromstring(serialize_svg(state["composition"]))


@then("the SVG contains the elements in order with escaped text")
def check(state):
    children = list(state["root"])
    assert [child.tag.rsplit("}", 1)[-1] for child in children] == ["rect", "text"]
    assert children[0].attrib["width"] == "30"
    assert children[1].text == "A & <B>"
