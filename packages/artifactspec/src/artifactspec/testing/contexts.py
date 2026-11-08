"""Recording fake phase contexts for plugin authors."""

from artifactspec.core._contexts import RendererBuilder, RepresentationBuilder, nonempty
from artifactspec.core.models import Content
from artifactspec.core.syntax import SourceSpan


class FakePhraseContext:
    def __init__(self, name: str, span: SourceSpan | None = None) -> None:
        self.name = name
        self.span = span
        self.operations: list[tuple[str, str]] = []

    def create(self, object_type: str) -> None:
        nonempty(object_type, "object type")
        if self.operations:
            raise ValueError("phrase must create exactly one object")
        self.operations.append(("create", object_type))


class FakePropertyContext:
    def __init__(
        self,
        name: str,
        value: str,
        span: SourceSpan | None = None,
        *,
        object_type: str = "unknown",
    ) -> None:
        self.name = name
        self.value = value
        self.object_type = object_type
        self.span = span
        self.operations: list[tuple[str, str, str]] = []

    def set(self, key: str, value: str) -> None:
        nonempty(key, "property key")
        if not isinstance(value, str):
            raise TypeError("property value must be a string")
        self.operations.append(("set", key, value))


class FakeRepresentationContext(RepresentationBuilder):
    """Record representation elements without invoking a renderer."""

    def __init__(
        self,
        content: Content,
        output: str = "image",
        representation: str = "test",
        *,
        index: int = 0,
    ) -> None:
        super().__init__(content, output, representation)
        self.index = index
        if content.nodes:
            self.node = content.nodes[index]


class FakeRendererContext(RendererBuilder):
    """Record emitted bytes in memory without writing files."""
