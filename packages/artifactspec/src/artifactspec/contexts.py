"""Public phase-specific interfaces implemented by core and testing contexts."""

from typing import Protocol

from artifactspec.models import Composition, Content
from artifactspec.syntax import SourceSpan


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
    def output(self) -> str: ...

    def warn(self, message: str) -> None: ...

    def text(
        self,
        node: str,
        value: str,
        *,
        x: float,
        y: float,
        size: float = 20,
        color: str = "black",
    ) -> None: ...

    def rectangle(
        self,
        node: str,
        *,
        x: float,
        y: float,
        width: float,
        height: float,
        color: str = "black",
    ) -> None: ...


class RendererContext(Protocol):
    """Consume a composition and emit exactly one complete artifact in memory."""

    @property
    def composition(self) -> Composition: ...

    def warn(self, message: str) -> None: ...

    def emit(self, data: bytes, *, media_type: str, editable: bool) -> None: ...
