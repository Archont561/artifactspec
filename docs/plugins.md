# Plugin registration and capability discovery

## Trust boundary

Plugins are executable Python and are **not sandboxed**. Rendering automatically
imports all installed ArtifactSpec plugins by default: installation is therefore
authorization to execute that code during rendering. Review the distribution
and its dependencies before installing it. Use `--no-plugin-autoload` and
`--plugin ID` to load only explicitly selected plugins. The Python API continues
to require explicit `Registry` registration or loading.

Capability discovery, validation, and the language server read installed
metadata and JSON manifests; they do not import plugin modules or invoke entry
points. Metadata is untrusted self-reported information, not proof of safety,
correctness, or compatibility. Normal Python startup, environment setup, and
package installation may themselves execute code; custom Python distribution
finders may also execute while metadata is enumerated. Discovery cannot sandbox
those operations.

## Identity and static metadata

An installed distribution advertises each plugin with an entry point in the
`artifactspec.plugins` group. The entry point name is the plugin ID (lowercase
ASCII letters and digits separated by `-`, `_`, or `.`), and its value points to
a `Plugin` object, for example `my_plugin:plugin`. The distribution must ship
`my_plugin/artifactspec_plugins/example.json` for the entry point named `example`.
The first module component determines the directory. The file must be listed in
the distribution's installed files (wheel RECORD); discovery reads it from that
distribution, without importing the module. Ensure the build includes the JSON as
package data. Multiple plugins in one distribution have separate manifests. For
example, a plugin package declares its entry point in `pyproject.toml`:

```toml
[project.entry-points."artifactspec.plugins"]
example = "my_plugin:plugin"
```

Wheel builders must include `my_plugin/artifactspec_plugins/example.json`; a
source checkout or editable installation without this file in its distribution
file records cannot be discovered.

A version 1 manifest looks like:

```json
{
  "schema_version": 1,
  "id": "example",
  "version": "1.0.0",
  "outputs": ["pdf", "svg"],
  "phrases": [{"name": "draw a circle", "outputs": ["svg"]}],
  "properties": [],
  "representations": [],
  "renderers": [{"name": "svg-renderer", "outputs": ["svg"]}]
}
```

`version` is a nonempty plugin-defined version string; it is not automatically
compared to distribution or core versions. Each contribution has a nonempty
name and a list of output names. An empty contribution output list means all
outputs declared by its plugin; otherwise it must be a subset of those outputs.
This is a declaration, not a guarantee that an output can actually be rendered.
There is no automatic core-version compatibility negotiation yet. Duplicate
plugin IDs and duplicate `(kind, name)` contributions are errors, regardless
of version or output; errors name the conflict rather than selecting a winner.
Malformed, missing, or unsupported manifests fail discovery explicitly.

## Semantic type metadata (version 2)

Version 2 adds static type declarations to phrase and property contributions.
A phrase has an `object_type` string naming the type of the object it creates;
a property has a nonempty `target_types` array naming the object types it can
be applied to. The other top-level fields and contribution output rules are
unchanged. For example:

```json
{
  "schema_version": 2,
  "id": "shapes",
  "version": "1.0",
  "outputs": ["image"],
  "phrases": [{"name": "circle", "outputs": [], "object_type": "circle"}],
  "properties": [{"name": "color", "outputs": [], "target_types": ["circle"]}],
  "representations": [],
  "renderers": []
}
```

Type names are exact, case-sensitive nonempty strings; there is no subtype or
inheritance model. They are self-reported metadata, not proof of correctness.
Only JSON string values are supported by the current language. Version 1 remains
supported: validation issues a warning when an object or property type cannot be
checked. Typed runtime declarations opt in explicitly:

```python
plugin = Plugin("shapes", "1.0", outputs=("image",), schema_version=2)
plugin.phrase("circle", object_type="circle")(lambda context: None)
plugin.property("color", target_types=("circle",))(lambda context: None)
```

Metadata must still match exactly when loading a plugin at runtime.
`ManifestCatalog` accepts validated static manifests for parsing or validation
without importing plugin modules or invoking handlers.

## Runtime registration

```python
from artifactspec.plugins import Plugin, Registry

plugin = Plugin("example", "1.0.0", outputs=("pdf", "svg"))

@plugin.phrase("draw a circle", outputs=("svg",))
def draw_circle(context):
    # A future parsing context will record a typed operation here.
    pass

@plugin.renderer("svg-renderer", outputs=("svg",))
def render_svg(context):
    pass

registry = Registry()
registry.register(plugin)
handler = registry.handler("phrases", "draw a circle", output="svg")
```

The decorators also support `property` and `representation`. They return the
original callable. Registration validates the whole plugin before modifying the
registry and freezes its contributions. `registry.handler(kind, name, output=...)`
returns a registered callable only when it is compatible with the requested output.
Discovery of explicitly registered plugins uses `registry.manifests()`.
`registry.load_installed("example")` imports a selected plugin, while
`registry.load_all_installed()` imports every installed plugin. Both compare
the resulting `Plugin` with its static manifest. The latter checks installed
metadata conflicts before importing any entry point. An error importing a later
plugin cannot undo code already executed by earlier plugins. With autoload
disabled, selecting one plugin checks only that plugin's installed metadata,
so an unrelated conflicting plugin need not be loaded. Imports use Python's
normal module search path; shadowed modules may execute before the manifest
comparison.

Public phase protocols live in `artifactspec.core.contexts`; fake contexts and
pytest helpers live in `artifactspec.testing` and
`artifactspec.testing.pytest_plugin`. See `docs/rendering.md` for their
contracts. The SVG backend is an independently installed `artifactspec-svg`
distribution; no SVG backend is embedded in the core package.

## CLI and JSON

The console script and `python -m artifactspec` both invoke the Typer app
`artifactspec.cli:app`. `artifactspec capabilities` (or
`python -m artifactspec capabilities`) emits a JSON object with
`schema_version: 1` and a `plugins` array sorted by ID. The
default summary contains each plugin's `id`, `version`, `outputs`, and counts
under `capabilities`, with keys `phrases`, `properties`, `representations`, and
`renderers`. `--details` replaces those counts with arrays of `{name, outputs}`
objects. `--output svg` retains only plugins declaring `svg` and contributions
compatible with it; the output list on each returned plugin is narrowed to the
requested output. Empty results use an empty `plugins` array. Discovery errors
produce a nonzero exit and a diagnostic on stderr, not partial JSON. The capability command does not import installed plugins. Plugin code may
report inaccurate metadata; runtime rendering loads code separately as described
above.
