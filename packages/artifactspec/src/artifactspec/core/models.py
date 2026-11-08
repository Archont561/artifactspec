"""Immutable, renderer-independent semantic content."""

from dataclasses import dataclass

from artifactspec.core.syntax import SourceSpan


@dataclass(frozen=True, slots=True)
class ContentNode:
    """An object and its string-valued semantic properties and source origins."""

    name: str
    object_type: str
    properties: tuple[tuple[str, str], ...]
    provenance: tuple[SourceSpan, ...]


@dataclass(frozen=True, slots=True)
class Content:
    """An ordered collection of semantic objects, independent of output."""

    nodes: tuple[ContentNode, ...]


@dataclass(frozen=True, slots=True)
class Element:
    """A plugin-owned representation value and the sources that produced it."""

    value: object
    provenance: tuple[SourceSpan, ...]


@dataclass(frozen=True, slots=True)
class Composition:
    """A static, output-specific layout; playback is deliberately separate."""

    output: str
    representation: str
    width: float
    height: float
    elements: tuple[Element, ...]
    limitations: tuple[str, ...] = ()
