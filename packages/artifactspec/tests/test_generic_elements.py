"""Core tracks source links without knowing a plugin value's concrete type."""

import pytest

from artifactspec.core.models import Content, ContentNode
from artifactspec.core.syntax import Position, SourceSpan
from artifactspec.testing import FakeRepresentationContext


def test_generic_value_is_preserved_with_its_semantic_provenance():
    span = SourceSpan("input.art", Position(1, 1), Position(1, 5))
    context = FakeRepresentationContext(
        Content((ContentNode("a", "custom", (), (span,)),))
    )
    value = {"plugin_owned": [1, 2]}
    context.add("a", value)
    element = context.finish().elements[0]
    assert element.value is value
    assert element.provenance == (span,)


def test_unknown_source_is_rejected_before_element_is_added():
    context = FakeRepresentationContext(Content(()))
    with pytest.raises(ValueError, match="unknown content object"):
        context.add("missing", object())
    assert context.finish().elements == ()
