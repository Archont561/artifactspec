"""Plugin-owned SVG payloads validate data and control their own markup."""

from xml.etree import ElementTree

import pytest
from artifactspec_svg.elements import Rectangle, Text
from artifactspec_svg.syntax import serialize_svg
from hypothesis import given
from hypothesis import strategies as st

from artifactspec.core.models import Composition, Element


@given(
    st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"), blacklist_characters="\ufffe\uffff"
        )
    )
)
def test_text_str_preserves_unicode_and_escapes_xml(value):
    fragment = str(Text(1, 2, value))
    assert (ElementTree.fromstring(fragment).text or "") == value


@pytest.mark.parametrize("value", [float("inf"), float("nan"), True, '1" onload="x'])
def test_rectangle_rejects_invalid_coordinates(value):
    with pytest.raises(ValueError, match="finite numbers"):
        Rectangle(value, 0, 10, 10)


@pytest.mark.parametrize("width,height", [(0, 1), (1, 0), (-1, 1)])
def test_rectangle_rejects_nonpositive_dimensions(width, height):
    with pytest.raises(ValueError, match="positive"):
        Rectangle(0, 0, width, height)


def test_svg_renderer_accepts_independent_compatible_payload():
    class Circle:
        media_type = "image/svg+xml"

        def __str__(self):
            return '<circle cx="1" cy="2" r="3"/>'

    composition = Composition("image", "diagram", 10, 10, (Element(Circle(), ()),))
    root = ElementTree.fromstring(serialize_svg(composition))
    assert root[0].tag.endswith("circle")


@pytest.mark.parametrize(
    "value",
    ["<script/>", object(), type("Invalid", (), {"media_type": "image/svg+xml"})()],
)
def test_svg_renderer_rejects_non_svg_payloads(value):
    composition = Composition("image", "diagram", 10, 10, (Element(value, ()),))
    with pytest.raises(TypeError, match="unsupported visual element"):
        serialize_svg(composition)


def test_text_rejects_non_string_and_nonpositive_size():
    with pytest.raises(TypeError, match="text must be a string"):
        Text(1, 2, None)
    with pytest.raises(ValueError, match="size must be positive"):
        Text(1, 2, "x", size=0)


def test_svg_values_are_immutable():
    from dataclasses import FrozenInstanceError

    element = Rectangle(1, 2, 3, 4)
    with pytest.raises(FrozenInstanceError):
        element.width = 8
