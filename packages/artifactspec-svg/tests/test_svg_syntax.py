"""SVG syntax is generated independently from the renderer adapter."""

import pytest
from hypothesis import given
from hypothesis import strategies as st


@pytest.mark.parametrize("color", ["red", "NAVY", "#abc", "#aabbccdd"])
def test_supported_svg_colors_are_retained(color):
    from artifactspec_svg.syntax import svg_color

    assert svg_color(color) == color


@pytest.mark.parametrize("color", ["", "url(x)", 'red" onload="x', "#xyz"])
def test_unsupported_svg_colors_fail(color):
    from artifactspec_svg.syntax import svg_color

    with pytest.raises(ValueError, match="unsupported SVG color"):
        svg_color(color)


@given(
    st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs", "Cc"), blacklist_characters="\ufffe\uffff"
        )
    )
)
def test_svg_text_is_xml_escaped(text):
    from xml.etree import ElementTree

    from artifactspec_svg.syntax import xml_text

    assert (ElementTree.fromstring(f"<x>{xml_text(text)}</x>").text or "") == text


def test_svg_rejects_xml_forbidden_characters():
    from artifactspec_svg.syntax import xml_text

    with pytest.raises(ValueError, match="forbidden by XML"):
        xml_text("\0")
