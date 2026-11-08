# Controlled language: first parsing subset

This page defines the initial implemented syntax and the intended semantic
contracts. Parsing is not validation or rendering: it does not resolve references,
execute plugin handlers, infer facts, or guarantee that a renderer exists. The
validation CLI and language server share semantic reference and type checks;
a minimal static SVG rendering pipeline is available with the optional SVG plugin.

## Plugin-defined syntax

The core does not reserve a content phrase, property statement, or output
statement form. Installed plugins declare complete statement templates in
typed `Plugin` declarations. Installed plugin modules are imported during
discovery; the core matches their declarations without invoking handlers.
For example, with both the SVG and event plugins installed:

```text
Output image.
Create text named title.
Set value of title to "Welcome".
Create event named opening.
Set date of opening to "1989-11-09".
Set label of opening to "Berlin Wall opens".
```

These specific statements are plugin declarations, not a universal grammar.
Different plugins may declare different full forms. Templates use typed
placeholders for object names, references and JSON string values; see
[the plugin contract](plugins.md) for the typed declarations and matching rules.
Each nonblank line must match exactly one output declaration or content
statement. The first nonblank line selects the output, and later output
statements are rejected. Line endings are LF, CRLF or CR; other Unicode line
separators can occur inside JSON strings. Blank lines are ignored. Source lines
are trimmed before matching, with no multiline or multiple statements per line.

`artifactspec.core.parser.parse(text, catalog, source="...")` returns an
immutable `Document` with typed creation and property nodes. Lines and columns
are one-based Unicode code-point positions; span ends are exclusive. A failure
returns no partial document. Diagnostics distinguish missing or unknown output,
unknown or ambiguous statements, malformed string values, and repeated output
declarations. Output selection and statements are matched only against declarative
metadata; `parse` does not execute plugin handlers. Discovering an installed
plugin imports its module according to the trust policy.

## Reference semantics

The document is the only scope. Names are case-sensitive; a semantic validator
must reject duplicate definitions and unresolved or ambiguous names. A named
reference is resolved within its document against a unique definition; no other
document or registry entry can satisfy it. Forward named references are allowed
by this contract; resolution occurs only after the complete document is available.
`it` denotes the most recently created object **before** the referring statement;
property statements and blank lines do not
change it. It starts unset for each new document, and a use before any creation
must produce a source-linked diagnostic, not guess. A new document resets `it`;
the only output header must start the document, so it is not a nested scope.
The parser preserves references; `artifactspec.core.validation.validate` checks these
rules and returns a `ValidationResult` containing diagnostics and resolved
references. Duplicate names, unresolved and ambiguous references are errors.
Version 3 plugin metadata permits exact object-type checking for properties;
old JSON-manifest plugins must migrate to typed objects. A result is valid if it has no errors;
warnings must still be reviewed. Validation does not execute plugin handlers or
prove factual correctness, rendering support, or visual quality. Syntax errors
currently stop parsing at the first error; multiple independent semantic errors
can be reported together.

## Typed artifact boundaries (design contract)

The parse `Document` is a source-level representation, not validated semantic
content. The validator resolves references and checks declared target types, but
does not yet produce typed semantic **content** for renderers. Future semantic
content will have meaning independent of any particular renderer. A
**representation** selects how that content is expressed for an output; a
**composition** arranges representations and, for animation, playback states;
a **renderer** consumes an approved composition and produces artifacts plus
warnings/provenance. A plugin can contribute phrases, properties,
representations and renderers through the registry. Phase-specific context
protocols and a small static implementation are available in
`artifactspec.core.contexts`, `artifactspec.core.pipeline`, and `artifactspec.core.rendering`;
the parser itself does not run them. The following conceptual types illustrate
their relationships rather than a finalized wire format:

```text
ContentNode       = semantic_type + typed_properties + provenance
Representation    = content_reference + output_type + representation_kind + provenance
Composition       = output_type + ordered_placements + optional_playback + provenance
RendererRequest   = composition + output_options
RendererResult    = artifacts + warnings + provenance
Provenance        = zero_or_more_source_spans
```

An image composition has static placements and no playback; an animation
composition needs an explicit playback model. These are not checks performed by
the parser. The first implemented composition is static and supports text and
rectangles through plugins; animation playback is not yet implemented. See `docs/rendering.md`
for the current contract and limitations. Typed parse nodes only carry syntax
and string literals; they are not these semantic types.

For example, a domain timeline could be semantic content describing historical
events; an image representation could lay those events out in a static diagram.
An animation representation could depict the same content, while its separate
playback composition schedules visual states over elapsed time. A content event's
date is not automatically an animation timestamp. Image output is static and
has no playback timeline; animation requires explicit playback timing semantics
before rendering. Animation timing and interpolation are not implemented.

Source spans are carried from statements and literals into the parse tree. Future
semantic, composition, and rendering phases must preserve enough source links to
explain diagnostics and output provenance; one semantic item or output element
may derive from multiple spans, and generated elements may have none. The first
rendering slice records source spans for emitted elements and rejects implicit
fallback. General unit validation, compatibility negotiation and richer
many-to-many output provenance remain open. The general example flows above are
design illustrations, not claims that every output or representation has a
renderer.

## Validation CLI

Run `artifactspec validate path/to/scene.art` for human-readable diagnostics, or
use `--format json` for the stable version 1 JSON envelope:

```json
{"schema_version": 1, "valid": false, "diagnostics": [{"code": "unresolved_reference", "severity": "error", "message": "No object named 'sun'; declare it in this document.", "span": {"source": "scene.art", "start": {"line": 2, "column": 14}, "end": {"line": 2, "column": 17}}}]}
```

Positions are one-based Unicode code points and span ends are exclusive. Exit
status 0 means no errors (warnings can still be present), 1 means validation
errors, and 2 means an input, metadata, or command-line error. Input is UTF-8.
Diagnostics go to standard output; operational errors go to standard error.
Multiple semantic errors are reported together, but syntax parsing currently
stops at the first error. Installed capabilities are discovered from
plugin objects; the command imports installed plugins but does not execute their
handlers. Use `--no-plugin-autoload --plugin ID` to select trusted plugins.

## Editor diagnostics

Run `artifactspec lsp` as a language server over standard input and output. It
imports installed plugin objects at startup and uses the same validator and
validation codes as the CLI. Use `--no-plugin-autoload --plugin ID` to select
trusted plugins. Configure an LSP client to start that command for ArtifactSpec documents; the server does not
register a file extension or install editor configuration. Restart it after
installing or changing plugins so that it can rediscover their metadata.

The server validates on document open and change, and clears diagnostics on
close. Both full and incremental changes are supported; LSP positions use the
encoding negotiated with the client (UTF-16 by default). Warnings and errors
are distinguished. Parsing remains first-error, and independent semantic
errors are collected. No renderer or plugin handler runs as part of validation.
