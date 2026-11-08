"""Discover installed plugins by importing their entry-point objects."""

from __future__ import annotations

import re
from importlib import metadata
from typing import Any

from artifactspec.plugins import (
    KINDS,
    Plugin,
    RegistrationError,
    Registry,
    check_conflicts,
    filter_manifests,
)


def installed_plugins(*, only: set[str] | None = None) -> dict[str, Plugin]:
    """Import selected entry points and return their declared Plugin objects."""
    entries = sorted(
        metadata.entry_points(group="artifactspec.plugins"),
        key=lambda ep: (ep.name, ep.value),
    )
    selected = [entry for entry in entries if only is None or entry.name in only]
    names: set[str] = set()
    for entry in selected:
        if not re.fullmatch(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*", entry.name):
            raise RegistrationError(f"invalid plugin entry point id {entry.name!r}")
        try:
            module = entry.module
            attr = entry.attr
        except (AttributeError, AssertionError, ValueError) as exc:
            raise RegistrationError(
                f"invalid entry point for plugin {entry.name!r}"
            ) from exc
        if (
            not module
            or not all(part.isidentifier() for part in module.split("."))
            or not attr
        ):
            raise RegistrationError(f"invalid entry point for plugin {entry.name!r}")
        if entry.name in names:
            raise RegistrationError(f"duplicate plugin id {entry.name!r}")
        names.add(entry.name)
    plugins = {}
    for entry in selected:
        try:
            plugin = entry.load()
        except Exception as exc:
            raise RegistrationError(
                f"failed to load plugin {entry.name!r}: {exc}"
            ) from exc
        if not isinstance(plugin, Plugin):
            raise RegistrationError(
                f"entry point {entry.name!r} must reference a Plugin object"
            )
        if plugin.to_dict()["id"] != entry.name:
            raise RegistrationError(
                f"plugin id {plugin.to_dict()['id']!r} does not match entry point {entry.name!r}"
            )
        dist = entry.dist
        if dist is None or not dist.metadata["Name"] or not dist.version:
            raise RegistrationError(
                f"distribution metadata missing for plugin {entry.name!r}"
            )
        plugin._bind_distribution(dist.metadata["Name"], dist.version)
        plugins[entry.name] = plugin
    check_conflicts(plugin.to_dict() for plugin in plugins.values())
    return plugins


def capabilities(
    *,
    details: bool = False,
    output: str | None = None,
    only: set[str] | None = None,
    plugins: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return CLI discovery metadata derived from imported plugin objects."""
    sources = (
        plugins
        if plugins is not None
        else [plugin.to_dict() for plugin in installed_plugins(only=only).values()]
    )
    manifests = filter_manifests(sources, output)
    if details:
        return {"schema_version": 2, "plugins": manifests}
    summaries = [
        {
            "id": item["id"],
            "version": item["version"],
            "outputs": item["outputs"],
            "capabilities": {kind: len(item[kind]) for kind in KINDS},
        }
        for item in manifests
    ]
    return {"schema_version": 2, "plugins": summaries}


def load_registry(*, autoload: bool = True, selected: tuple[str, ...] = ()) -> Registry:
    """Load all installed plugins or only explicitly selected plugins."""
    registry = Registry()
    if autoload:
        registry.load_all_installed(required=selected)
    else:
        for name in selected:
            registry.load_installed(name)
    return registry
