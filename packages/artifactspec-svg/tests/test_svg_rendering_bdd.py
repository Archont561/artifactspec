from pathlib import Path
from xml.etree import ElementTree

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "svg_rendering.feature")
)


@pytest.fixture
def state():
    return {}


@given("a composition containing a text element")
def composition(state):
    from artifactspec.core.models import Composition, TextElement

    state["composition"] = Composition(
        "image",
        "basic",
        640,
        480,
        (TextElement(20, 40, "Hello & SVG", "navy", 20, ()),),
    )


@when("the SVG plugin renders the composition")
def render(state):
    from artifactspec_svg.renderer import render_svg

    from artifactspec.core._contexts import RendererBuilder

    state["context"] = RendererBuilder(state["composition"])
    render_svg(state["context"])


@then("the artifact contains escaped editable SVG text")
def artifact(state):
    data, media_type, editable = state["context"].artifact
    root = ElementTree.fromstring(data)
    assert root.find("{http://www.w3.org/2000/svg}text").text == "Hello & SVG"
    assert media_type == "image/svg+xml" and editable
