"""Optional pytest fixtures for testing ArtifactSpec plugins."""

import pytest

from artifactspec.testing import (
    FakePhraseContext,
    FakePropertyContext,
    FakeRendererContext,
    FakeRepresentationContext,
)


@pytest.fixture
def artifactspec_phrase_context():
    """Factory for recording phrase contexts."""
    return FakePhraseContext


@pytest.fixture
def artifactspec_property_context():
    """Factory for recording property contexts."""
    return FakePropertyContext


@pytest.fixture
def artifactspec_representation_context():
    """Factory for recording representation contexts."""
    return FakeRepresentationContext


@pytest.fixture
def artifactspec_renderer_context():
    """Factory for in-memory renderer contexts."""
    return FakeRendererContext
