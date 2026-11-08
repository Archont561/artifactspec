# Plugin registration and capability discovery

## Trust boundary

Plugins are executable Python and are **not sandboxed**. Only load or explicitly
register code after the user has approved the plugin and its distribution and
dependencies. Discovery reads installed distribution metadata and JSON manifests;
it does not import plugin modules or invoke entry points. Metadata is untrusted
self-reported information, not proof of safety, correctness, or compatibility.
Normal Python startup, environment setup, and package installation may themselves
execute code; custom Python distribution finders may also execute while metadata
is enumerated. Discovery cannot sandbox those operations.

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
Discovery of explicitly registered
plugins uses `registry.manifests()`. To load an installed plugin, explicitly
call `registry.load_installed("example")` only after approval. This imports its
entry point, and rejects it unless the resulting `Plugin` metadata exactly
matches the static manifest. Import-time side effects cannot be undone even if
validation fails. Imports use Python's normal module search path, so shadowed
modules can execute before the metadata comparison; approval must cover the
actual import environment as well as the distribution. Discovery does not load
or register plugins automatically.

Phase-specific context protocols, their operations, fake contexts, and test
helpers are planned in ART-5, not implemented here. Illustratively, a phrase
handler will receive a parsing/semantic context rather than a private core AST
class, and a renderer will receive a renderer-phase context rather than the
parser's context. For example, the eventual interfaces might resemble the
following **pseudocode**, not an importable API or committed method names:

```python
class PhraseContext(Protocol):
    def record_operation(self, name: str) -> None: ...

class RendererContext(Protocol):
    def emit_output(self, data: bytes) -> None: ...
```

Only phase-appropriate operations should be exposed. Exact methods, signatures,
and injection are undecided; the registration examples are not working renderers.

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
produce a nonzero exit and a diagnostic on stderr, not partial JSON. The CLI
never imports installed plugins. Plugin code may report inaccurate metadata;
loading and manifest comparison are a separate, explicitly trusted operation.
