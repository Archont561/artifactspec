"""Dated event language and image/report representation."""

import re
from datetime import date

from artifactspec.core.contexts import (
    PhraseContext,
    PropertyContext,
    RepresentationContext,
)
from artifactspec.plugin import Phrase, Plugin, Property, Representation
from artifactspec_events.elements import EventText, ReportText

plugin = Plugin(
    "events",
    outputs={"image": "Output image.", "report": "Output report."},
    phrases=(Phrase("event", "event", "Create event named {name}."),),
    properties=(
        Property("date", ("event",), "Set date of {reference} to {value}."),
        Property("event-label", ("event",), "Set label of {reference} to {value}."),
    ),
    representations=(Representation("diagram", ("event",)),),
)


def _date(value: str) -> None:
    message = "event date must be a valid ISO calendar date (YYYY-MM-DD)"
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError(message)
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(message) from exc


def _label(value: str) -> None:
    if not value.strip():
        raise ValueError("event label must not be empty")


@plugin.phrase("event")
def create_event(context: PhraseContext) -> None:
    context.create("event")


@plugin.property("date")
def event_date(context: PropertyContext) -> None:
    _date(context.value)
    context.set("date", context.value)


@plugin.property("event-label")
def event_label(context: PropertyContext) -> None:
    _label(context.value)
    context.set("value", context.value)


@plugin.representation("diagram")
def represent_event(context: RepresentationContext) -> None:
    node = context.node
    properties = dict(node.properties)
    unsupported = sorted(set(properties) - {"date", "value"})
    if unsupported:
        raise ValueError(f"event diagram cannot express properties {unsupported!r}")
    if "date" not in properties or "value" not in properties:
        raise ValueError(f"event {node.name!r} requires date and label")
    _date(properties["date"])
    _label(properties["value"])
    y = 40 + 70 * context.index
    if y + 40 > 480:
        raise ValueError("diagram exceeds the fixed canvas height")
    context.warn(
        "Diagram uses a fixed canvas and does not wrap or measure text; inspect for clipping and font differences."
    )
    separator = " — " if context.output == "image" else ": "
    text = properties["date"] + separator + properties["value"]
    element = (
        EventText(20, y, text) if context.output == "image" else ReportText(20, y, text)
    )
    context.add(node.name, element)
