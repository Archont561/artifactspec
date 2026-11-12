"""Read-only catalogs of plugin capability metadata."""

from collections.abc import Iterable
from typing import Any, Protocol

from artifactspec.plugins._registry import (
    check_conflicts,
    filter_manifests,
    validate_manifest,
)


class CapabilityCatalog(Protocol):
    """Read-only capability metadata used by parsing and validation."""

    def manifests(self, *, output: str | None = None) -> list[dict[str, Any]]: ...


class ManifestCatalog:
    """Validated static metadata without importing or invoking plugin code."""

    def __init__(self, manifests: Iterable[dict[str, Any]]) -> None:
        self._manifests = [validate_manifest(item) for item in manifests]
        check_conflicts(self._manifests)

    def manifests(self, *, output: str | None = None) -> list[dict[str, Any]]:
        return filter_manifests(self._manifests, output)
