"""Typed plugin contribution declarations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Phrase:
    """Declare the complete syntax and semantic type of an object statement."""

    name: str
    object_type: str
    syntax: str
    outputs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Property:
    """Declare the complete syntax and accepted target types of a property."""

    name: str
    target_types: tuple[str, ...]
    syntax: str
    outputs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Representation:
    """Declare an object-type-specific representation contribution."""

    name: str
    target_types: tuple[str, ...]
    outputs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Renderer:
    """Declare a rendering contribution."""

    name: str
    outputs: tuple[str, ...] = ()
