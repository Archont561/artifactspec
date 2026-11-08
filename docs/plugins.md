# Plugin registration and discovery

## Trust boundary

Plugins are executable Python and are **not sandboxed**. Discovery imports the
objects named by installed entry points. Therefore `capabilities`, `validate`,
`lsp`, and `render` all execute installed plugin code by default. Install only
plugins and dependencies you trust. Parsing and validation use the loaded
objects' declarative syntax; they do not invoke contribution handlers.

To import only selected plugins, use `--no-plugin-autoload` and repeat
`--plugin ID`. With autoload enabled, `--plugin ID` requires that plugin but
still loads all installed plugins. This works for all four commands. CLI and LSP
redirect ordinary import-time stdout to stderr to protect their output protocols;
plugin code can still have arbitrary side effects or write directly to streams.
An import error or a conflict can occur after earlier imports have executed;
there is no rollback or pre-import conflict check for contributions.

## Declaring a plugin

The `Plugin` object is the only source of its capability metadata. Declare the
output syntax and typed contributions in its constructor, then attach handlers
using decorators. For example:

```python
from html import escape
from artifactspec.plugin import Phrase, Plugin, Property, Renderer, Representation

plugin = Plugin(
    id="shapes",
    outputs={"image": "Output image."},
    phrases=(Phrase("circle", "circle", "Draw {name}."),),
    properties=(Property("color", ("circle",), "Color {reference} with {value}."),),
    representations=(Representation("diagram", ("circle",)),),
    renderers=(Renderer("svg"),),
)

@plugin.phrase("circle")
def circle(context):
    context.create("circle")

@plugin.property("color")
def color(context):
    context.set("color", context.value)

@plugin.representation("diagram")
def diagram(context):
    context.text(context.node.name, "circle", x=20, y=40 + 70 * context.index)

@plugin.renderer("svg")
def render(context):
    text = "".join(f"<text>{escape(element.text)}</text>" for element in context.composition.elements)
    context.emit(f'<svg xmlns="http://www.w3.org/2000/svg">{text}</svg>'.encode(),
                 media_type="image/svg+xml", editable=True)
```

The example renderer supports text elements only. Real renderers must validate
the element types and content they accept. Decorator names must match a declared
contribution; duplicate handlers and modifications after registration fail.
`Plugin.to_dict()` returns an independent JSON-serializable dictionary, including
all syntax and semantic metadata. It does not invoke handlers. Declaring a
capability without attaching a handler allows metadata inspection, but trying to
execute it reports a missing-handler error.

A plugin distribution advertises the object directly:

```toml
[project.entry-points."artifactspec.plugins"]
shapes = "my_plugin:plugin"
```

The entry point name must equal the plugin ID, which uses lowercase ASCII
letters and digits separated by `-`, `_`, or `.`. Discovery imports the module,
checks that the entry point resolves to a `Plugin`, associates the object with
its owning installed distribution, and registers it. No JSON manifest or wheel
file record is required. The plugin version comes from the entry point's
installed distribution metadata, built from the project's `pyproject.toml`; it is
not an argument to `Plugin`. A plugin constructed or registered directly without
an installed entry point has `version: null` in `to_dict()`. Discovery rejects a
single object associated with different distributions rather than guessing its
version.

## Syntax and composition

`outputs` maps each output name to a literal declaration template. `Phrase`
has a name, object type, syntax, and optional output subset. Its template uses
exactly one `{name}`. `Property` has a name, nonempty target types, syntax, and
optional output subset. Its template uses exactly one each of `{reference}` and
`{value}`. `Representation` declares a name and nonempty target types;
`Renderer` declares a name. Both accept an optional output subset. An empty
subset means all outputs declared by that plugin.

Templates are single trimmed lines of at most 1024 characters. All text outside
the placeholders is literal; literal text must separate adjacent placeholders,
and double braces represent literal braces. Names and references are ASCII
identifiers, and values are JSON strings. `it` is a reserved reference and
cannot be a declared name. Source lines are trimmed before matching. Ambiguous
matches are errors, while identical declarations of the same output are
deduplicated. Type names are exact and case-sensitive; there is no subtype model.

Duplicate plugin IDs and duplicate contribution names are errors. Independent
plugins may share a representation name only for disjoint target types. Core
then dispatches each semantic node to its matching representation handler. Use
`registry.representation_handler(name, object_type, output=...)` when selecting
a handler directly. The output is not a guarantee that a renderer exists.

## Migration from JSON manifests

Remove the installed `artifactspec_plugins/*.json` files. Move each output,
phrase, property, representation, and renderer declaration into the `Plugin`
constructor using the typed classes above. Move handler metadata out of the
decorators, leaving their contribution names. Remove the version argument; the
installed distribution supplies it. Keep the entry point pointing to the actual
object. Update integrations to call `to_dict()` and to expect imports during
discovery, validation, and LSP startup. Older schema-v1/v2 and schema-v3 JSON
manifest files are not used for installed discovery. See
[rendering](rendering.md) for phase contexts and behavior.

## CLI and JSON

`artifactspec capabilities` emits a version 2 JSON envelope with plugins sorted
by ID. Its default summary reports each ID, installed distribution version,
outputs, and contribution counts. `--details` returns each plugin's complete `to_dict()` metadata; `--output image` filters incompatible outputs
and contributions. Discovery errors produce a nonzero exit and a diagnostic on
stderr, not partial JSON. `to_dict()` returns the underlying schema-v3 metadata,
which is separate from the CLI envelope version. The version 2 details shape
replaces the previous version 1 abbreviated contribution arrays.

The Python API exposes `Registry.register(plugin)` for explicit objects,
`Registry.load_installed(id)` for one installed entry point, and
`Registry.load_all_installed()` for all installed entry points. Registration
freezes the object's contribution bindings and checks conflicts. Public phase
protocols live in `artifactspec.core.contexts`; test fakes are in
`artifactspec.testing` and its pytest plugin.
