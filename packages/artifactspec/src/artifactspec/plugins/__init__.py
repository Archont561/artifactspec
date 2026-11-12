"""Public plugin declaration, registry, and catalog API."""

from artifactspec.plugins._catalog import CapabilityCatalog, ManifestCatalog
from artifactspec.plugins._registry import (
    KINDS,
    Phrase,
    Plugin,
    Property,
    RegistrationError,
    Registry,
    Renderer,
    Representation,
    check_conflicts,
    filter_manifests,
    validate_manifest,
)

__all__ = [
    "KINDS",
    "CapabilityCatalog",
    "ManifestCatalog",
    "Phrase",
    "Plugin",
    "Property",
    "RegistrationError",
    "Registry",
    "Renderer",
    "Representation",
    "check_conflicts",
    "filter_manifests",
    "validate_manifest",
]
