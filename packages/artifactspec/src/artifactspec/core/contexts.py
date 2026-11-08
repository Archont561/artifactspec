"""Public phase-specific interfaces implemented by core and testing contexts."""

from typing import Protocol

from artifactspec.core.models import Composition, Content, ContentNode
from artifactspec.core.syntax import SourceSpan


class PhraseContext(Protocol):
    """Create exactly one semantic object for a declared phrase."""

    @property
    def name(self) -> str: ...

    @property
    def span(self) -> SourceSpan | None: ...

    def create(self, object_type: str) -> None: ...


class PropertyContext(Protocol):
    """Apply a parsed string value to a previously created semantic object."""

    @property
    def name(self) -> str: ...

    @property
    def value(self) -> str: ...

    @property
    def object_type(self) -> str: ...

    @property
    def span(self) -> SourceSpan | None: ...

    def set(self, key: str, value: str) -> None: ...


class RepresentationContext(Protocol):
    """Read semantic content and emit static visual elements."""

    @property
    def content(self) -> Content: ...

    @property
    def node(self) -> ContentNode: ...

    @property
    def index(self) -> int: ...

    @property
    def output(self) -> str: ...

    def warn(self, message: str) -> None: ...

    def add(self, node: str, value: object) -> None:
        """Add a plugin-owned value with source links to a semantic object."""
        ...


class RendererContext(Protocol):
    """Consume a composition and emit exactly one complete artifact in memory."""

    @property
    def composition(self) -> Composition: ...

    def warn(self, message: str) -> None: ...

    def emit(self, data: bytes, *, media_type: str, editable: bool) -> None: ...
