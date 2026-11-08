"""Dated event language and image/report representation."""

import re
from datetime import date

from artifactspec.core.contexts import (
    PhraseContext,
    PropertyContext,
    RepresentationContext,
)
from artifactspec.plugins import Plugin

plugin = Plugin(
    "events",
    "0.1.0",
    outputs=("image", "report"),
    schema_version=3,
    output_syntax={"image": "Output image.", "report": "Output report."},
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


@plugin.phrase("event", object_type="event", syntax="Create event named {name}.")
def create_event(context: PhraseContext) -> None:
    context.create("event")


@plugin.property(
    "date", target_types=("event",), syntax="Set date of {reference} to {value}."
)
def event_date(context: PropertyContext) -> None:
    _date(context.value)
    context.set("date", context.value)


@plugin.property(
    "event-label",
    target_types=("event",),
    syntax="Set label of {reference} to {value}.",
)
def event_label(context: PropertyContext) -> None:
    _label(context.value)
    context.set("value", context.value)


@plugin.representation("diagram", target_types=("event",))
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
    context.text(
        node.name, properties["date"] + separator + properties["value"], x=20, y=y
    )
