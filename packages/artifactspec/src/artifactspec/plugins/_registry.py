"""Plugin declarations and explicit, trusted runtime registration."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict
from typing import Any, TypeVar, cast

from artifactspec.plugins._contributions import (
    Phrase,
    Property,
    Renderer,
    Representation,
)

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


def _output_syntax(syntax: Any, outputs: list[str]) -> dict[str, str]:
    from artifactspec.core.templates import TemplateError, compile_template

    if not isinstance(syntax, dict) or set(syntax) != set(outputs):
        raise RegistrationError("output_syntax must map every output to a template")
    for template in syntax.values():
        try:
            compile_template(template, set())
        except TemplateError as exc:
            raise RegistrationError(f"invalid output template: {exc}") from exc
    return dict(sorted(syntax.items()))


def validate_manifest(data: Any, *, expected_id: str | None = None) -> dict[str, Any]:
    """Validate and normalize a static or runtime manifest."""
    if not isinstance(data, dict):
        raise RegistrationError("manifest must be an object using schema version 3")
    version = data.get("schema_version")
    if type(version) is not int or version != 3:
        raise RegistrationError(
            "unsupported plugin metadata schema; migrate to typed Plugin declarations (schema version 3)"
        )
    fields = {"schema_version", "id", "version", "outputs", "output_syntax", *KINDS}
    if set(data) != fields:
        raise RegistrationError(
            "schema version 3 manifest must contain exactly schema_version, id, version, outputs, output_syntax and all capability lists"
        )
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
        "version": None
        if data["version"] is None
        else _name(data["version"], "version"),
        "outputs": _outputs(data["outputs"], "outputs"),
    }
    result["output_syntax"] = _output_syntax(data["output_syntax"], result["outputs"])
    for kind in KINDS:
        result[kind] = _normalize_entries(
            data[kind], kind, result["outputs"], plugin_id
        )
    return result


def _normalize_type_and_syntax(
    contribution: dict[str, Any], item: dict[str, Any], kind: str
) -> None:
    if kind == "phrases":
        contribution["object_type"] = _name(item["object_type"], "object type")
    if kind == "properties":
        target_types = _outputs(item["target_types"], "target types")
        if not target_types:
            raise RegistrationError("target types must not be empty")
        contribution["target_types"] = target_types
    if kind == "representations":
        target_types = _outputs(item["target_types"], "target types")
        if not target_types:
            raise RegistrationError("representation target types must not be empty")
        contribution["target_types"] = target_types
    if kind in ("phrases", "properties"):
        from artifactspec.core.templates import TemplateError, compile_template

        expected = {"name"} if kind == "phrases" else {"reference", "value"}
        try:
            compile_template(item["syntax"], expected)
        except TemplateError as exc:
            raise RegistrationError(f"invalid {kind} template: {exc}") from exc
        contribution["syntax"] = item["syntax"]


def _normalize_entries(
    entries: Any,
    kind: str,
    plugin_outputs: list[str],
    plugin_id: str,
) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        raise RegistrationError(f"{kind} must be a list")
    normalized = []
    seen = set()
    for item in entries:
        fields = {"name", "outputs"}
        if kind == "phrases":
            fields.add("object_type")
        if kind == "properties":
            fields.add("target_types")
        if kind in ("phrases", "properties"):
            fields.add("syntax")
        if kind == "representations":
            fields.add("target_types")
        if not isinstance(item, dict) or set(item) != fields:
            required = ", ".join(sorted(fields))
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
        _normalize_type_and_syntax(contribution, item, kind)
        normalized.append(contribution)
    return sorted(normalized, key=lambda item: item["name"])


def _check_contribution_conflicts(
    previous: list[tuple[str, dict[str, Any]]],
    kind: str,
    item: dict[str, Any],
    plugin_id: str,
) -> None:
    for previous_id, previous_item in previous:
        disjoint_types = kind == "representations" and not set(
            item["target_types"]
        ).intersection(previous_item["target_types"])
        if not disjoint_types:
            raise RegistrationError(
                f"conflicting {kind} contribution {item['name']!r} from plugins {previous_id!r} and {plugin_id!r}"
            )


def check_conflicts(manifests: Iterable[dict[str, Any]]) -> None:
    """Reject ambiguous identities and contributions deterministically."""
    ids: set[str] = set()
    contributions: dict[tuple[str, str], list[tuple[str, dict[str, Any]]]] = {}
    for manifest in sorted(manifests, key=lambda item: item["id"]):
        plugin_id = manifest["id"]
        if plugin_id in ids:
            raise RegistrationError(f"duplicate plugin id {plugin_id!r}")
        ids.add(plugin_id)
        for kind in KINDS:
            for item in manifest[kind]:
                key = kind, item["name"]
                previous = contributions.setdefault(key, [])
                _check_contribution_conflicts(previous, kind, item, plugin_id)
                previous.append((plugin_id, item))


def _filter_contributions(item: dict[str, Any], output: str) -> None:
    for kind in KINDS:
        item[kind] = [
            entry
            for entry in item[kind]
            if not entry["outputs"] or output in entry["outputs"]
        ]
        for entry in item[kind]:
            if entry["outputs"]:
                entry["outputs"] = [output]


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
            item["output_syntax"] = {output: item["output_syntax"][output]}
            _filter_contributions(item, output)
        result.append(item)
    return result


class Plugin:
    """Typed capability declarations and their decorated Python handlers."""

    def __init__(
        self,
        id: str,
        *,
        outputs: Mapping[str, str],
        phrases: Iterable[Phrase] = (),
        properties: Iterable[Property] = (),
        representations: Iterable[Representation] = (),
        renderers: Iterable[Renderer] = (),
    ) -> None:
        if not isinstance(outputs, Mapping):
            raise RegistrationError("outputs must map output names to syntax templates")
        declarations = {
            "phrases": (phrases, Phrase),
            "properties": (properties, Property),
            "representations": (representations, Representation),
            "renderers": (renderers, Renderer),
        }
        data: dict[str, Any] = {
            "schema_version": 3,
            "id": id,
            "version": None,
            "outputs": list(outputs),
            "output_syntax": dict(outputs),
        }
        for kind, (values, expected) in declarations.items():
            entries = list(values)
            if not all(isinstance(item, expected) for item in entries):
                raise RegistrationError(
                    f"{kind} must contain {expected.__name__} declarations"
                )
            data[kind] = [asdict(cast(Any, item)) for item in entries]
        self._data = validate_manifest(data)
        self._handlers: dict[tuple[str, str], Callable[..., Any]] = {}
        self._frozen = False
        self._distribution: str | None = None

    def _bind_distribution(self, name: str, version: str) -> None:
        """Attach the owning entry point's installed distribution identity."""
        version = _name(version, "distribution version")
        identity = (name, version)
        if (
            self._distribution is not None
            and (self._distribution, self._data["version"]) != identity
        ):
            raise RegistrationError("plugin object belongs to multiple distributions")
        self._distribution = name
        self._data["version"] = version

    def _contribute(self, kind: str, name: str) -> Callable[[F], F]:
        def decorate(func: F) -> F:
            if self._frozen:
                raise RegistrationError("registered plugin is frozen")
            if not callable(func):
                raise RegistrationError("plugin contribution must be callable")
            if not any(item["name"] == name for item in self._data[kind]):
                raise RegistrationError(f"undeclared {kind} contribution {name!r}")
            key = kind, name
            if key in self._handlers:
                raise RegistrationError(
                    f"duplicate handler for {kind} contribution {name!r}"
                )
            self._handlers[key] = func
            return func

        return decorate

    def phrase(self, name: str) -> Callable[[F], F]:
        return self._contribute("phrases", name)

    def property(self, name: str) -> Callable[[F], F]:
        return self._contribute("properties", name)

    def representation(self, name: str) -> Callable[[F], F]:
        return self._contribute("representations", name)

    def renderer(self, name: str) -> Callable[[F], F]:
        return self._contribute("renderers", name)

    def to_dict(self) -> dict[str, Any]:
        """Return independent JSON-serializable capability metadata."""
        return validate_manifest(self._data)

    def manifest(self) -> dict[str, Any]:
        """Return capability metadata; use to_dict in new integrations."""
        return self.to_dict()


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
                    handler = plugin._handlers.get((kind, name))
                    if handler is None:
                        raise RegistrationError(
                            f"no handler registered for {kind} contribution {name!r}"
                        )
                    return handler
        raise RegistrationError(
            f"no {kind} contribution {name!r} compatible with output {output!r}"
        )

    def representation_handler(
        self, name: str, object_type: str, *, output: str
    ) -> Callable[..., Any]:
        """Find the representation contribution for one semantic object."""
        for plugin in self._plugins.values():
            for manifest in filter_manifests([plugin.manifest()], output):
                for item in manifest["representations"]:
                    if item["name"] != name or object_type not in item["target_types"]:
                        continue
                    handler = plugin._handlers.get(("representations", name))
                    if handler is None:
                        raise RegistrationError(
                            f"no handler registered for representations contribution {name!r}"
                        )
                    return handler
        raise RegistrationError(
            f"no representation {name!r} for object type {object_type!r} and output {output!r}"
        )

    def plugin(self, plugin_id: str) -> Plugin:
        """Return a registered plugin object by its ID."""
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise RegistrationError(f"plugin {plugin_id!r} is not registered") from exc

    def load_installed(self, plugin_id: str) -> None:
        """Import one explicitly selected installed plugin."""
        from artifactspec.plugins.discovery import installed_plugins

        installed = installed_plugins(only={plugin_id})
        if plugin_id not in installed:
            raise RegistrationError(f"installed plugin {plugin_id!r} not found")
        self.register(installed[plugin_id])

    def load_all_installed(self, *, required: Iterable[str] = ()) -> None:
        """Import installed plugins; installation grants runtime trust."""
        from artifactspec.plugins.discovery import installed_plugins

        installed = installed_plugins()
        for plugin_id in required:
            if plugin_id not in installed:
                raise RegistrationError(f"installed plugin {plugin_id!r} not found")
        check_conflicts(
            [*self.manifests(), *(plugin.to_dict() for plugin in installed.values())]
        )
        for plugin in installed.values():
            self.register(plugin)
