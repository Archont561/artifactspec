# Rendering and plugin phase contracts

ArtifactSpec has a deliberately small static rendering slice. It validates the
controlled language, executes plugin handlers to construct
semantic content, selects one representation and one renderer, and writes a
single artifact. It does **not** support animation, playback, narration, a
report renderer, arbitrary layout, or semantic values other than strings.

## Plugin trust and a first SVG

Install the separately distributed `artifactspec-svg` plugin alongside
`artifactspec` (for example, `python -m pip install artifactspec artifactspec-svg`
once the distributions are available). Install `artifactspec-events` as well
for the event statements below. SVG owns image text and rectangle syntax, their
`diagram` layout, and the `svg` renderer. Events owns event syntax and its own
`diagram` layout. The renderer consumes the shared composition model and does
not interpret event semantics:

```sh
artifactspec render scene.art \
  --representation diagram --renderer svg --output scene.svg
```

For example, `scene.art` can contain:

```text
Output image.
Create text named title.
Set value of title to "Hello".
Set color of title to "navy".
Create rectangle named box.
Set color of box to "#aabbcc".
Create event named opening.
Set date of opening to "1989-11-09".
Set label of opening to "Berlin Wall opens".
```

Rendering automatically imports every installed ArtifactSpec plugin by default,
like pytest plugin autoload. **Installation therefore authorizes execution** of
all installed plugin code during rendering, including plugins not selected as the
renderer. Plugins are arbitrary Python and are **not sandboxed**. To load only
selected plugins, pass `--no-plugin-autoload` and repeat `--plugin ID`:

```sh
artifactspec render scene.art --no-plugin-autoload \
  --plugin svg --plugin events --representation diagram --renderer svg --output scene.svg
```

With autoload disabled, no installed plugin executes unless explicitly named.
Discovery, validation, and the language server also import installed plugin
modules by default; they do not execute contribution handlers. Use the same
selection options to restrict which plugins they import. Plugin metadata does not
establish that a plugin is safe.

By default, the command prints a version 1 JSON success result, while
diagnostics and operational errors go to stderr. Add `--format json` for
machine-readable successes **and** failures:

```sh
artifactspec render scene.art --representation diagram \
  --renderer svg --output scene.svg --format json
```

In JSON mode, the command writes one JSON object to stdout after argument
parsing. Success adds `status: "success"` to the existing result. Failure has
`status: "error"`, `error` with a stable `code` and descriptive `message`,
`diagnostics`, `warnings`, `limitations`, and `fallback: null`. Diagnostics
and warnings include source spans where available. Limitations include those
reported before a failed phase; their absence does not certify that a failed
phase had none. Validation warnings are also included in `diagnostics` when
validation fails. No artifact field is returned on failure. Trusted plugin code
can itself write to stdout or have side effects; it is not sandboxed.

The codes are `validation_failed`, `capability_selection_failed`,
`phrase_failed`, `property_failed`, `representation_failed`, `renderer_failed`,
`output_write_failed`, `plugin_error`, `io_error`, and the generic
`pipeline_failed`. The Python API still raises `PipelineError`, which exposes
`code`, `diagnostics`, `warnings`, and `limitations` where known. These codes
classify the failing phase; they do not imply a successful fallback. Exit 0
means success, 1 means specification validation failed, and 2 means plugin,
representation, renderer, I/O or usage failure. Errors raised by Typer while
parsing arguments, including missing options or an invalid format, remain
human-readable on stderr even with `--format json`. Output file paths must have
an existing parent directory.

The success result identifies the output, representation, renderer, artifact
path, media type and editable flag, source-linked validation warnings,
limitations, and an explicit `fallback: null` (fallback is not supported).
`provenance` and `provenance_status` describe source links on **composition
elements**, not a verified mapping to artifact bytes:

- `available`: every composition element has at least one source span.
- `partial`: some, but not all, elements have source spans.
- `unavailable`: elements exist but none has a source span.
- `no_elements`: the composition contains no elements; this does not imply the
  renderer emitted an empty artifact.

The provenance list aggregates unique spans from the composition in encounter
order. A renderer may omit, alter, or add output independently, so even
`available` does not establish complete artifact-level provenance. Results
returned by `render` always set one of these statuses. An externally constructed
`RenderResult` may leave its status as `None` (not reported).

Limitations are reported by plugins, not independently verified. An empty list
means none was reported, **not** that the artifact is visually faithful,
factually correct, or complete. A limited synthetic backend can be tested for
exact output, but that does not certify other backends. Inspect the artifact and
perform factual review separately.

## Phase interfaces

`artifactspec.core.contexts` provides public protocols; plugin code should accept
these rather than importing private core implementations:

- `PhraseContext` supplies the object name and optional source span and requires
  exactly one `create(object_type)` call. The created type must equal the
  declared `object_type`.
- `PropertyContext` supplies the target name/type, decoded string value and
  source span. A handler must call `set(key, value)` at least once. Repeated
  assignments take effect in document order. Forward named references are
  resolved before property handlers run; `it` uses the validator's resolution.
- `RepresentationContext` receives immutable `Content`, the current `node`,
  its zero-based declaration-order `index`, and the requested output. Core
  dispatches each node to the selected representation's handler for that
  semantic type. Handlers emit static text or rectangles linked to named nodes
  and can report limitations with `warn(message)`.
- `RendererContext` receives an immutable `Composition`, may report limitations
  with `warn(message)`, and emits exactly one complete byte artifact with a
  media type and editable flag.

`artifactspec.testing` supplies recording fake contexts for each phase. Pytest
fixtures are opt-in: declare `pytest_plugins = ["artifactspec.testing.pytest_plugin"]`
then use `artifactspec_phrase_context`, `artifactspec_property_context`,
`artifactspec_representation_context`, or `artifactspec_renderer_context` as
factories. The fake renderer holds bytes in memory; it does not write files.

## Calendar events and playback

The independent events plugin supports `event` objects with a required `date`
and `label`. A date is a string in exactly `YYYY-MM-DD` format and must be
valid in the proleptic Gregorian calendar, with years from 0001 through 9999.
The label must contain a non-whitespace character. Values are preserved as
semantic properties on the event node, along with source spans. Repeated
assignments take effect in document order. An invalid date or blank event label
is rejected during materialization; missing fields are rejected during
composition. Static `validate` and LSP diagnostics check the registered names,
references and declared types but do **not** execute plugin handlers, so they do
not check calendar validity or required event fields.

Events remain in creation order, even if the dates are not chronological or
are equal. The image form displays `date — label`; the report composition uses
`date: label`. They reuse the same semantic nodes, without sorting or assigning
playback times. There is no separate timeline grouping, date range, approximate
date, calendar conversion, or temporal arithmetic in this slice. Image output
uses the existing fixed static layout, and report composition has no renderer.
Animation and its scheduling and interpolation remain separate, future work;
selecting the diagram representation for animation fails explicitly.

## Selection, output and limitations

`build_content` first validates the whole specification. No contribution
handler runs on validation errors. It materializes immutable `ContentNode`s with
names, types, string properties and source spans. The content is independent of
output; `compose` selects a named, output-compatible representation from an
explicitly trusted `Registry`. The same content can be composed as an image or
as a report. Static composition does not carry playback timing; a content
historical timeline is not an animation timeline.

`render` requires an explicit representation, renderer and destination. It
checks both selections before running content handlers. The registry enforces declared output compatibility; missing or incompatible
contributions and unsupported elements fail, with **no automatic fallback**.
The SVG and events plugins each contribute `diagram` handlers for their own
semantic types, so both can participate in one image composition. A missing
handler for any node and output is an explicit error; for example, SVG shapes
cannot be composed as a report. The SVG renderer supports `image` only. Its fixed 640-by-480 canvas does not wrap or measure
text and reports this limitation; excess rows are rejected. The renderer allows
a limited set of named colors or hexadecimal colors, rejects unsupported colors and
characters forbidden in XML, and escapes text. It preserves editable SVG source,
not a raster or a PDF. Rendering is not factual validation or visual review.

The renderer emits bytes to the core. Only after it completes successfully does
the core write a temporary file in the destination directory and atomically
replace the destination. Validation, handler, encoding or replacement failures
leave a pre-existing destination unchanged and temporary files are cleaned up.
This applies to the core's output operation, not to side effects that trusted
plugin code may perform independently. The result aggregates source spans from
emitted elements; provenance cannot assert that every detail is editable or
visually faithful. Validation warnings remain visible in the result.
