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

A schema version 3 manifest declares complete syntax as data:

```json
{
  "schema_version": 3,
  "id": "shapes",
  "version": "1.0",
  "outputs": ["image"],
  "output_syntax": {"image": "Output image."},
  "phrases": [{"name": "circle", "outputs": [], "object_type": "circle", "syntax": "Draw {name}."}],
  "properties": [{"name": "color", "outputs": [], "target_types": ["circle"], "syntax": "Color {reference} with {value}."}],
  "representations": [{"name": "diagram", "outputs": [], "target_types": ["circle"]}],
  "renderers": []
}
```

Each output has a literal declaration in `output_syntax`. Phrase templates use
exactly one `{name}` placeholder, and property templates use exactly one each of
`{reference}` and `{value}`. The remaining text is literal; templates must be
single trimmed lines of at most 1024 characters, with literal text separating
adjacent placeholders. Double braces represent literal braces. A name or
reference is an ASCII identifier; a value is a JSON string. `it` is a reserved
reference and cannot be a declared name. There is no arbitrary plugin-supplied
regex or executable grammar. Source lines are trimmed before matching. When a
statement matches multiple templates, parsing reports ambiguity instead of
guessing. Identical output declarations for the same output are deduplicated.

`object_type` and `target_types` are nonempty, exact, case-sensitive type names;
there is no subtype model. Each contribution has a nonempty name and an output
list. An empty list means all outputs declared by its plugin; a nonempty list
must be a subset. Duplicate plugin IDs and duplicate contribution names fail;
representations may share a name only when their target types do not overlap.
These rules are checked before runtime autoload. Metadata is self-reported, not
proof of correctness. Versions 1 and 2 do not have complete templates and are
rejected with a migration diagnostic; there is no legacy grammar fallback.
The plugin-defined `version` is not automatically compared to distribution or
core versions.

## Migrating version 1 or 2 plugins

1. Set `schema_version` to 3 in the static JSON and runtime declaration.
   Supply `output_syntax` with a complete literal statement for every output.
2. Give every phrase an `object_type` and a complete `syntax` containing
   `{name}`. Give every property nonempty `target_types` and a complete
   `syntax` containing `{reference}` and `{value}`. Put the same declarations
   on the corresponding runtime decorators.
3. Give every representation nonempty `target_types` and update its handler
   to handle `context.node` at `context.index` rather than iterating the whole
   document. Representations of the same name may be contributed by independent
   plugins for disjoint object types.
4. Ship the JSON in wheel file records, verify that it matches `plugin.manifest()`
   exactly, and test the installed wheel. Run `artifactspec capabilities`,
   `validate`, and `lsp` against the metadata before trusting runtime imports.

Remove any use of `--builtin-basic` and `--no-builtin-basic`; there is no core
basic plugin. Install the needed plugins instead and select their representation
and renderer explicitly. The packaged examples use `diagram` and `svg`.
Version 1's unverified-type warnings are not a compatibility mechanism: old
manifests are rejected before plugin code is imported.

## Runtime registration

```python
from artifactspec.plugins import Plugin, Registry

plugin = Plugin("shapes", "1.0", outputs=("image",),
                output_syntax={"image": "Output image."})

@plugin.phrase("circle", object_type="circle", syntax="Draw {name}.")
def circle(context):
    context.create("circle")

@plugin.property("color", target_types=("circle",),
                 syntax="Color {reference} with {value}.")
def color(context):
    context.set("color", context.value)

@plugin.representation("diagram", target_types=("circle",))
def diagram(context):
    context.text(context.node.name, "circle", x=20, y=40 + 70 * context.index)

registry = Registry()
registry.register(plugin)
```

The decorators also support `renderer`; each returns the original callable. Registration validates the whole plugin before modifying the
registry and freezes its contributions. `registry.handler(kind, name, output=...)`
returns a registered callable only when it is compatible with the requested output.
For a representation shared by multiple plugins, use
`registry.representation_handler(name, object_type, output=...)` to select the
contribution for a particular semantic type.
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
contracts. SVG syntax, layout and rendering belong to the optional `artifactspec-svg`
distribution. Dated-event syntax and representation belong to the optional
`artifactspec-events` distribution. Core includes no built-in content plugin.

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
