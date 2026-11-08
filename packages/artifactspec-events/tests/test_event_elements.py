from xml.etree import ElementTree

import pytest
from artifactspec_events.elements import EventText
from hypothesis import given
from hypothesis import strategies as st


@given(
    st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"), blacklist_characters="\ufffe\uffff"
        )
    )
)
def test_event_svg_text_escapes_content(value):
    assert (ElementTree.fromstring(str(EventText(1, 2, value))).text or "") == value


def test_event_svg_text_rejects_xml_control_characters():
    with pytest.raises(ValueError, match="forbidden by XML"):
        str(EventText(1, 2, "bad\0"))


def test_event_svg_text_rejects_invalid_coordinates():
    with pytest.raises(ValueError, match="finite numbers"):
        EventText('1" onload="x', 2, "unsafe")


def test_event_svg_text_requires_string_content():
    with pytest.raises(TypeError, match="text must be a string"):
        EventText(1, 2, None)
