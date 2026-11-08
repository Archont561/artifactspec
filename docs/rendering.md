# Rendering and plugin phase contracts

ArtifactSpec has a deliberately small static rendering slice. It validates the
controlled language, executes explicitly trusted plugin handlers to construct
semantic content, selects one representation and one renderer, and writes a
single artifact. It does **not** support animation, playback, narration, a
report renderer, arbitrary layout, or semantic values other than strings.

## Explicit trust and a first SVG

The built-in `builtin-basic` plugin is **not automatically loaded** and is not
listed by installed-plugin discovery. Choose it explicitly for rendering:

```sh
artifactspec render scene.art --builtin-basic \
  --representation basic --renderer svg --output scene.svg
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
Set value of opening to "Berlin Wall opens".
```

Alternatively, repeat `--plugin ID` for each installed plugin you explicitly
trust. Static discovery, validation, and the language server only inspect installed
manifests by default. Pass `--builtin-basic` to `capabilities`, `validate`, or
`lsp` to include the built-in static manifest without loading plugin handlers. The render
command first loads **only** the selected plugin IDs and checks their runtime
manifest against the static manifest. Plugin handlers are arbitrary trusted
Python and are **not sandboxed**; selecting a plugin authorizes executing its
code. The `--builtin-basic` flag explicitly authorizes the first-party plugin.

The command prints a version 1 JSON result with output, representation and
renderer names and an explicit `fallback: null` (fallback is not supported);
artifact path, media type and editable flag; source-linked
validation warnings; textual `limitations`; and the source spans contributing
to emitted elements. Exit 0 means success, 1 means specification validation
failed, and 2 means plugin, representation, renderer, I/O or usage failure.
Diagnostics and operational errors go to stderr. Output file paths must have
an existing parent directory.

## Phase interfaces

`artifactspec.contexts` provides public protocols; plugin code should accept
these rather than importing private core implementations:

- `PhraseContext` supplies the object name and optional source span and requires
  exactly one `create(object_type)` call. For v2 plugins the created type must
  equal the declared `object_type`.
- `PropertyContext` supplies the target name/type, decoded string value and
  source span. A handler must call `set(key, value)` at least once. Repeated
  assignments take effect in document order. Forward named references are
  resolved before property handlers run; `it` uses the validator's resolution.
- `RepresentationContext` receives immutable `Content` and the requested
  output. It emits static text or rectangles linked to named semantic nodes,
  and can report limitations with `warn(message)`.
- `RendererContext` receives an immutable `Composition`, may report limitations
  with `warn(message)`, and emits exactly one complete byte artifact with a
  media type and editable flag.

`artifactspec.testing` supplies recording fake contexts for each phase. Pytest
fixtures are opt-in: declare `pytest_plugins = ["artifactspec.pytest_plugin"]`
then use `artifactspec_phrase_context`, `artifactspec_property_context`,
`artifactspec_representation_context`, or `artifactspec_renderer_context` as
factories. The fake renderer holds bytes in memory; it does not write files.

## Calendar events and playback

The opt-in basic plugin supports `event` objects with a required `date` and
`value` (label). A date is a string in exactly `YYYY-MM-DD` format and must be
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
selecting the basic representation for animation fails explicitly.

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
The basic representation supports text, rectangles, and dated events; the SVG renderer
supports `image` only. Its fixed 640-by-480 canvas does not wrap or measure
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
visually faithful. Validation warnings (including legacy v1 unverified types)
remain visible in the result.
