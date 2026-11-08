"""Core context implementations; plugins depend only on public protocols."""

from artifactspec.core.models import Composition, Content, ContentNode, Element
from artifactspec.core.syntax import SourceSpan


def nonempty(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(
            f"{label} must be a nonempty string without surrounding whitespace"
        )


class PhraseBuilder:
    def __init__(self, name: str, span: SourceSpan | None) -> None:
        self.name = name
        self.span = span
        self.object_type: str | None = None

    def create(self, object_type: str) -> None:
        nonempty(object_type, "object type")
        if self.object_type is not None:
            raise ValueError("phrase must create exactly one object")
        self.object_type = object_type


class PropertyBuilder:
    def __init__(self, node: ContentNode, value: str, span: SourceSpan | None) -> None:
        self.name = node.name
        self.value = value
        self.span = span
        self.object_type = node.object_type
        self.properties = dict(node.properties)
        self.changes = 0

    def set(self, key: str, value: str) -> None:
        nonempty(key, "property key")
        if not isinstance(value, str):
            raise TypeError("property value must be a string")
        self.properties[key] = value
        self.changes += 1


class RepresentationBuilder:
    def __init__(self, content: Content, output: str, representation: str) -> None:
        self.content = content
        self.node: ContentNode
        self.index = 0
        self.output = output
        self.representation = representation
        self.width = 640.0
        self.height = 480.0
        self.elements: list[Element] = []
        self.limitations: list[str] = []

    def warn(self, message: str) -> None:
        nonempty(message, "limitation")
        self.limitations.append(message)

    def _origin(self, name: str) -> tuple[SourceSpan, ...]:
        for node in self.content.nodes:
            if node.name == name:
                return node.provenance
        raise ValueError(f"unknown content object {name!r}")

    def add(self, node: str, value: object) -> None:
        self.elements.append(Element(value, self._origin(node)))

    def finish(self) -> Composition:
        from artifactspec.core.models import Composition

        return Composition(
            self.output,
            self.representation,
            self.width,
            self.height,
            tuple(self.elements),
            tuple(self.limitations),
        )


class RendererBuilder:
    def __init__(self, composition: Composition) -> None:
        self.composition = composition
        self.artifact: tuple[bytes, str, bool] | None = None
        self.limitations: list[str] = []

    def warn(self, message: str) -> None:
        nonempty(message, "limitation")
        self.limitations.append(message)

    def emit(self, data: bytes, *, media_type: str, editable: bool) -> None:
        if self.artifact is not None:
            raise ValueError("renderer must emit exactly one artifact")
        if not isinstance(data, bytes):
            raise TypeError("artifact data must be bytes")
        nonempty(media_type, "media type")
        if not isinstance(editable, bool):
            raise TypeError("editable must be a boolean")
        self.artifact = (data, media_type, editable)
