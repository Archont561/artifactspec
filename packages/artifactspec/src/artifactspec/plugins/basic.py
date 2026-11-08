"""A basic plugin for reusable semantic content and static layout."""

import re
from datetime import date

from artifactspec.core.contexts import (
    PhraseContext,
    PropertyContext,
    RepresentationContext,
)
from artifactspec.core.models import ContentNode
from artifactspec.plugins import Plugin

_EVENT_DATE_ERROR = "event date must be a valid ISO calendar date (YYYY-MM-DD)"


def _event_date(value: str) -> None:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError(_EVENT_DATE_ERROR)
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(_EVENT_DATE_ERROR) from exc


def _event_label(value: str) -> None:
    if not value.strip():
        raise ValueError("event label must not be empty")


def _represent_event(
    context: RepresentationContext,
    node: ContentNode,
    properties: dict[str, str],
    y: int,
) -> None:
    if "date" not in properties or "value" not in properties:
        raise ValueError(f"event {node.name!r} requires date and value")
    _event_date(properties["date"])
    _event_label(properties["value"])
    separator = " — " if context.output == "image" else ": "
    context.text(
        node.name, properties["date"] + separator + properties["value"], x=20, y=y
    )


def _represent_rectangle(
    context: RepresentationContext,
    node: ContentNode,
    properties: dict[str, str],
    y: int,
) -> None:
    if context.output == "image":
        context.rectangle(
            node.name,
            x=20,
            y=y,
            width=120,
            height=40,
            color=properties.get("color", "black"),
        )
    else:
        context.text(
            node.name,
            f"Rectangle (color: {properties.get('color', 'black')})",
            x=20,
            y=y,
        )


def _represent(context: RepresentationContext) -> None:
    context.warn(
        "Basic layout uses a fixed canvas and does not wrap or measure text; inspect for clipping and font differences."
    )
    for index, node in enumerate(context.content.nodes):
        properties = dict(node.properties)
        allowed = {
            "text": {"value", "color"},
            "rectangle": {"color"},
            "event": {"date", "value"},
        }.get(node.object_type, set())
        unsupported = sorted(set(properties) - allowed)
        if unsupported:
            raise ValueError(
                f"basic representation cannot express properties {unsupported!r}"
            )
        y = 40 + 70 * index
        if y + 40 > 480:
            raise ValueError("basic layout exceeds the fixed canvas height")
        if node.object_type == "text":
            context.text(
                node.name,
                properties.get("value", ""),
                x=20,
                y=y,
                color=properties.get("color", "black"),
            )
        elif node.object_type == "event":
            _represent_event(context, node, properties, y)
        elif node.object_type == "rectangle":
            _represent_rectangle(context, node, properties, y)
        else:
            raise ValueError(
                f"basic representation cannot express {node.object_type!r}"
            )


def basic_plugin() -> Plugin:
    """Return a new trusted plugin for simple image/report content."""
    plugin = Plugin("builtin-basic", "1", outputs=("image", "report"), schema_version=2)

    @plugin.phrase("text", object_type="text")
    def make_text(context: PhraseContext) -> None:
        context.create("text")

    @plugin.phrase("rectangle", object_type="rectangle")
    def make_rectangle(context: PhraseContext) -> None:
        context.create("rectangle")

    @plugin.phrase("event", object_type="event")
    def make_event(context: PhraseContext) -> None:
        context.create("event")

    @plugin.property("value", target_types=("text", "event"))
    def value(context: PropertyContext) -> None:
        if context.object_type == "event":
            _event_label(context.value)
        context.set("value", context.value)

    @plugin.property("date", target_types=("event",))
    def event_date(context: PropertyContext) -> None:
        _event_date(context.value)
        context.set("date", context.value)

    @plugin.property("color", target_types=("text", "rectangle"))
    def color(context: PropertyContext) -> None:
        context.set("color", context.value)

    plugin.representation("basic", outputs=("image", "report"))(_represent)
    return plugin
