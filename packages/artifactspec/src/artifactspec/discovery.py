"""Read installed plugin manifests without importing plugin code."""

from __future__ import annotations

import json
import re
from importlib import metadata
from typing import Any

from artifactspec.plugins import (
    KINDS,
    RegistrationError,
    check_conflicts,
    filter_manifests,
    validate_manifest,
)


def installed_plugins() -> dict[str, tuple[metadata.EntryPoint, dict[str, Any]]]:
    """Return entry points and validated static metadata; never load them."""
    found: list[tuple[metadata.EntryPoint, dict[str, Any]]] = []
    entries = sorted(
        metadata.entry_points(group="artifactspec.plugins"),
        key=lambda ep: (ep.name, ep.value),
    )
    for entry in entries:
        if not re.fullmatch(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*", entry.name):
            raise RegistrationError(f"invalid plugin entry point id {entry.name!r}")
        try:
            module = entry.module
        except (AssertionError, AttributeError, ValueError) as exc:
            raise RegistrationError(
                f"invalid entry point for plugin {entry.name!r}"
            ) from exc
        if (
            not module
            or not all(part.isidentifier() for part in module.split("."))
            or not entry.attr
        ):
            raise RegistrationError(f"invalid entry point for plugin {entry.name!r}")
        path = f"{module.split('.')[0]}/artifactspec_plugins/{entry.name}.json"
        dist = entry.dist
        if dist is None or dist.files is None:
            raise RegistrationError(
                f"installed file records missing for plugin {entry.name!r}"
            )
        matching = [file for file in dist.files if str(file) == path]
        if len(matching) != 1:
            raise RegistrationError(
                f"manifest {path!r} missing or duplicated in installed files for plugin {entry.name!r}"
            )
        try:
            data = json.loads(matching[0].read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise RegistrationError(
                f"cannot read manifest {path!r} for plugin {entry.name!r}: {exc}"
            ) from exc
        try:
            manifest = validate_manifest(data, expected_id=entry.name)
        except RegistrationError as exc:
            raise RegistrationError(
                f"invalid manifest for plugin {entry.name!r}: {exc}"
            ) from exc
        found.append((entry, manifest))
    check_conflicts(manifest for _, manifest in found)
    return {manifest["id"]: (entry, manifest) for entry, manifest in found}


def capabilities(
    *, details: bool = False, output: str | None = None, builtin_basic: bool = False
) -> dict[str, Any]:
    """Return the versioned CLI discovery schema from static metadata."""
    sources = [item[1] for item in installed_plugins().values()]
    if builtin_basic:
        from artifactspec._basic_metadata import basic_manifest

        sources.append(basic_manifest())
    check_conflicts(sources)
    manifests = filter_manifests(sources, output)
    plugins = []
    for manifest in manifests:
        plugins.append(
            {
                "id": manifest["id"],
                "version": manifest["version"],
                "outputs": manifest["outputs"],
                "capabilities": {
                    kind: (
                        [
                            {"name": entry["name"], "outputs": entry["outputs"]}
                            for entry in manifest[kind]
                        ]
                        if details
                        else len(manifest[kind])
                    )
                    for kind in KINDS
                },
            }
        )
    return {"schema_version": 1, "plugins": plugins}
