"""Plugin declarations and explicit, trusted runtime registration."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any, Protocol, TypeVar

KINDS = ("phrases", "properties", "representations", "renderers")
F = TypeVar("F", bound=Callable[..., Any])


class RegistrationError(ValueError):
    """A plugin declaration or registration is invalid or conflicts."""


def _name(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise RegistrationError(
            f"{field} must be a nonempty string without surrounding whitespace"
        )
    return value


def _outputs(values: Any, field: str) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise RegistrationError(f"{field} must be a list of output names")
    result = [_name(value, field) for value in values]
    if len(set(result)) != len(result):
        raise RegistrationError(f"{field} contains duplicate outputs")
    return sorted(result)


def _declared_outputs(values: Iterable[str]) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise RegistrationError(
            "outputs must be an iterable of output names, not a string"
        )
    try:
        return list(values)
    except TypeError as exc:
        raise RegistrationError("outputs must be an iterable of output names") from exc


def validate_manifest(data: Any, *, expected_id: str | None = None) -> dict[str, Any]:
    """Validate and normalize a static or runtime manifest."""
    if not isinstance(data, dict) or set(data) != {
        "schema_version",
        "id",
        "version",
        "outputs",
        *KINDS,
    }:
        raise RegistrationError(
            "manifest must contain exactly schema_version, id, version, outputs and all capability lists"
        )
    if type(data["schema_version"]) is not int or data["schema_version"] not in (1, 2):
        raise RegistrationError("unsupported manifest schema_version; expected 1 or 2")
    schema_version = data["schema_version"]
    plugin_id = _name(data["id"], "plugin id")
    if not re.fullmatch(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*", plugin_id):
        raise RegistrationError(f"invalid plugin id {plugin_id!r}")
    if expected_id is not None and plugin_id != expected_id:
        raise RegistrationError(
            f"manifest id {plugin_id!r} does not match entry point {expected_id!r}"
        )
    result: dict[str, Any] = {
        "schema_version": schema_version,
        "id": plugin_id,
        "version": _name(data["version"], "version"),
        "outputs": _outputs(data["outputs"], "outputs"),
    }
    for kind in KINDS:
        result[kind] = _normalize_entries(
            data[kind], kind, schema_version, result["outputs"], plugin_id
        )
    return result


def _normalize_entries(
    entries: Any,
    kind: str,
    schema_version: int,
    plugin_outputs: list[str],
    plugin_id: str,
) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        raise RegistrationError(f"{kind} must be a list")
    normalized = []
    seen = set()
    for item in entries:
        fields = {"name", "outputs"}
        if schema_version == 2 and kind == "phrases":
            fields.add("object_type")
        if schema_version == 2 and kind == "properties":
            fields.add("target_types")
        if not isinstance(item, dict) or set(item) != fields:
            required = (
                "name and outputs" if schema_version == 1 else ", ".join(sorted(fields))
            )
            raise RegistrationError(f"each {kind} contribution must have {required}")
        name = _name(item["name"], f"{kind} name")
        if name in seen:
            raise RegistrationError(
                f"duplicate {kind} contribution {name!r} in plugin {plugin_id!r}"
            )
        seen.add(name)
        outputs = _outputs(item["outputs"], f"{kind} outputs")
        if not set(outputs).issubset(plugin_outputs):
            raise RegistrationError(
                f"{kind} contribution {name!r} declares unsupported outputs"
            )
        contribution: dict[str, Any] = {"name": name, "outputs": outputs}
        if schema_version == 2 and kind == "phrases":
            contribution["object_type"] = _name(item["object_type"], "object type")
        if schema_version == 2 and kind == "properties":
            target_types = _outputs(item["target_types"], "target types")
            if not target_types:
                raise RegistrationError("target types must not be empty")
            contribution["target_types"] = target_types
        normalized.append(contribution)
    return sorted(normalized, key=lambda item: item["name"])


def check_conflicts(manifests: Iterable[dict[str, Any]]) -> None:
    """Reject ambiguous identities and contributions deterministically."""
    ids: set[str] = set()
    contributions: dict[tuple[str, str], str] = {}
    for manifest in sorted(manifests, key=lambda item: item["id"]):
        plugin_id = manifest["id"]
        if plugin_id in ids:
            raise RegistrationError(f"duplicate plugin id {plugin_id!r}")
        ids.add(plugin_id)
        for kind in KINDS:
            for item in manifest[kind]:
                key = kind, item["name"]
                if key in contributions:
                    raise RegistrationError(
                        f"conflicting {kind} contribution {item['name']!r} from plugins {contributions[key]!r} and {plugin_id!r}"
                    )
                contributions[key] = plugin_id


def filter_manifests(
    manifests: Iterable[dict[str, Any]], output: str | None = None
) -> list[dict[str, Any]]:
    """Return independent, sorted manifests filtered by declared output."""
    result = []
    for source in sorted(manifests, key=lambda item: item["id"]):
        item = validate_manifest(source)
        if output is not None:
            if output not in item["outputs"]:
                continue
            item["outputs"] = [output]
            for kind in KINDS:
                item[kind] = [
                    entry
                    for entry in item[kind]
                    if not entry["outputs"] or output in entry["outputs"]
                ]
                for entry in item[kind]:
                    if entry["outputs"]:
                        entry["outputs"] = [output]
        result.append(item)
    return result


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


class Plugin:
    """A declaration of capabilities and their Python handlers."""

    def __init__(
        self,
        plugin_id: str,
        version: str,
        *,
        outputs: Iterable[str] = (),
        schema_version: int = 1,
    ) -> None:
        self._data: dict[str, Any] = {
            "schema_version": schema_version,
            "id": plugin_id,
            "version": version,
            "outputs": _declared_outputs(outputs),
            **{kind: [] for kind in KINDS},
        }
        self._data = validate_manifest(self._data)
        self._handlers: dict[tuple[str, str], Callable[..., Any]] = {}
        self._frozen = False

    def _contribute(
        self, kind: str, name: str, outputs: Iterable[str], **metadata: Any
    ) -> Callable[[F], F]:
        def decorate(func: F) -> F:
            if self._frozen:
                raise RegistrationError("registered plugin is frozen")
            if not callable(func):
                raise RegistrationError("plugin contribution must be callable")
            candidate = self.manifest()
            candidate[kind].append(
                {"name": name, "outputs": _declared_outputs(outputs), **metadata}
            )
            self._data = validate_manifest(candidate)
            self._handlers[(kind, name)] = func
            return func

        return decorate

    def phrase(
        self, name: str, *, outputs: Iterable[str] = (), object_type: str | None = None
    ) -> Callable[[F], F]:
        metadata = {} if object_type is None else {"object_type": object_type}
        return self._contribute("phrases", name, outputs, **metadata)

    def property(
        self,
        name: str,
        *,
        outputs: Iterable[str] = (),
        target_types: Iterable[str] | None = None,
    ) -> Callable[[F], F]:
        metadata = (
            {}
            if target_types is None
            else {"target_types": _declared_outputs(target_types)}
        )
        return self._contribute("properties", name, outputs, **metadata)

    def representation(
        self, name: str, *, outputs: Iterable[str] = ()
    ) -> Callable[[F], F]:
        return self._contribute("representations", name, outputs)

    def renderer(self, name: str, *, outputs: Iterable[str] = ()) -> Callable[[F], F]:
        return self._contribute("renderers", name, outputs)

    def manifest(self) -> dict[str, Any]:
        return validate_manifest(self._data)


class Registry:
    """An in-memory registry; registering a plugin trusts already executed code."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        if not isinstance(plugin, Plugin):
            raise RegistrationError("expected a Plugin object")
        manifest = plugin.manifest()
        check_conflicts([*(p.manifest() for p in self._plugins.values()), manifest])
        self._plugins[manifest["id"]] = plugin
        plugin._frozen = True

    def manifests(self, *, output: str | None = None) -> list[dict[str, Any]]:
        return filter_manifests((p.manifest() for p in self._plugins.values()), output)

    def handler(
        self, kind: str, name: str, *, output: str | None = None
    ) -> Callable[..., Any]:
        """Find a registered callable, optionally requiring output compatibility."""
        if kind not in KINDS:
            raise RegistrationError(f"unknown capability kind {kind!r}")
        for plugin in self._plugins.values():
            for manifest in filter_manifests([plugin.manifest()], output):
                if any(item["name"] == name for item in manifest[kind]):
                    return plugin._handlers[(kind, name)]
        raise RegistrationError(
            f"no {kind} contribution {name!r} compatible with output {output!r}"
        )

    def load_installed(self, plugin_id: str) -> None:
        """Import one installed entry point after the caller has approved it."""
        from artifactspec.plugins.discovery import installed_plugins

        installed = installed_plugins(only={plugin_id})
        if plugin_id not in installed:
            raise RegistrationError(f"installed plugin {plugin_id!r} not found")
        entry_point, manifest = installed[plugin_id]
        check_conflicts([*self.manifests(), manifest])
        self._load_entry(plugin_id, entry_point, manifest)

    def load_all_installed(self, *, required: Iterable[str] = ()) -> None:
        """Load all installed entry points; installation grants runtime trust."""
        from artifactspec.plugins.discovery import installed_plugins

        installed = installed_plugins()
        for plugin_id in required:
            if plugin_id not in installed:
                raise RegistrationError(f"installed plugin {plugin_id!r} not found")
        check_conflicts(
            [*self.manifests(), *(manifest for _, manifest in installed.values())]
        )
        for plugin_id, (entry_point, manifest) in installed.items():
            self._load_entry(plugin_id, entry_point, manifest)

    def _load_entry(
        self, plugin_id: str, entry_point: Any, manifest: dict[str, Any]
    ) -> None:
        try:
            plugin = entry_point.load()
        except Exception as exc:
            raise RegistrationError(
                f"failed to load plugin {plugin_id!r}: {exc}"
            ) from exc
        if not isinstance(plugin, Plugin) or plugin.manifest() != manifest:
            raise RegistrationError(
                f"loaded plugin {plugin_id!r} does not match its static manifest"
            )
        self.register(plugin)
