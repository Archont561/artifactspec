# Controlled language: first parsing subset

This page defines the initial implemented syntax and the intended semantic
contracts. Parsing is not validation or rendering: it does not resolve references,
execute plugin handlers, infer facts, or guarantee that a renderer exists. The
validation CLI and language server share semantic reference and type checks;
plugin phase contexts and rendering are future work.

## Implemented syntax

An input is a sequence of lines. Blank lines are ignored; every nonblank line
contains exactly one statement ending in a period. There are no comments,
multiline statements, imports, nested scopes, or multiple statements on a line.
Leading and trailing whitespace is ignored. Keywords and capability names are
case-sensitive; spaces between syntactic components are required. Only the
first nonblank statement may be an output header, and exactly one is required:

```text
Output image.
Create circle named sun.
Set color of it to "yellow".
Set label of sun to "Bright sun".
```

`image` must be an output declared by an explicitly registered plugin. Output
names use the same ASCII identifier syntax as object names. `circle`
is an exact registered phrase name, `color` and `label` are exact registered
property names, and each must be compatible with that output. This uses the
runtime `Registry` supplied by the caller, not undisclosed installed metadata;
the parser neither loads plugins nor executes registered callables. An empty
contribution output list applies to all outputs declared by its plugin. The
registry rejects duplicate `(kind, name)` registrations before parsing with a
`RegistrationError` identifying the conflicting plugins; that registry error has
no document source span. A phrase unavailable for the output is reported like an
unknown phrase, with the statement's source span.

Each object name is an ASCII identifier: a letter followed by letters, digits,
underscores, or hyphens. The lowercase word `it` is reserved. Property values in
this subset are JSON strings, including JSON escapes; numbers, lists, booleans,
and null are not supported. The `Create` and `Set` separators ` named `,
` of ` and ` to ` are literal; the object-name and reference positions must be
single identifiers. The quoted string must immediately follow ` to ` and must
end immediately before the period. Phrase and property names in this subset are
one or more ASCII letter, digit, underscore or hyphen words separated by single
spaces; registry names outside that form cannot be expressed by this subset.
The grammar below describes a stripped, nonblank line (`json-string` is a JSON
string literal, not an arbitrary JSON value):

```text
header    = "Output " identifier "."
create    = "Create " capability " named " identifier "."
set       = "Set " capability " of " identifier " to " json-string "."
statement = create | set
```

The header is first and unique; every remaining nonblank line is one statement.
A period inside a JSON string is part of the value, not a statement boundary.
If syntax can be split into more than one valid interpretation, parsing fails
rather than choosing one. Unknown, unavailable, or malformed statements produce a
`ParseError` with a source span and diagnostic code. More than one output header
is rejected as ambiguous, not silently overwritten.

The parser uses Lark to parse each nonblank line according to this grammar, then
checks capabilities against the supplied registry and decodes JSON strings. Lark
is a runtime dependency, not a plugin loader or semantic validator.

`artifactspec.parser.parse(text, registry, source="...")` returns an immutable
`Document` containing an output and typed `CreateStatement` and `SetStatement`
nodes. Lines and columns are one-based Unicode code-point positions; span ends
are exclusive. Spans carry the caller-provided source identifier. A parse failure
returns no partial document. Diagnostic codes include `missing_output`,
`unknown_output`, `ambiguous_output`, `malformed_statement`, `unknown_statement`,
`unknown_phrase`, `unknown_property`, and `ambiguous_statement`. A diagnostic
span covers the offending statement (or position 1:1 for an empty document).
`Reference` nodes retain the original `it` or name, and `StringValue` retains the
decoded JSON value and its literal source span.
For example, with a previously approved and registered plugin:

```python
from artifactspec.parser import parse
from artifactspec.plugins import Plugin, Registry

plugin = Plugin("shapes", "1", outputs=("image",))
plugin.phrase("circle")(lambda context: None)
plugin.property("color")(lambda context: None)
registry = Registry()
registry.register(plugin)
document = parse(
    'Output image.\nCreate circle named sun.\nSet color of it to "yellow".',
    registry,
    source="sun.image",
)
```

The registered handlers in this example are placeholders and are not run by
`parse`; actual phase contexts and invocation are future work.

## Reference semantics

The document is the only scope. Names are case-sensitive; a semantic validator
must reject duplicate definitions and unresolved or ambiguous names. A named
reference is resolved within its document against a unique definition; no other
document or registry entry can satisfy it. Forward named references are allowed
by this contract; resolution occurs only after the complete document is available.
`it` denotes the most recently created object **before** the referring statement;
`Set` and blank lines do not
change it. It starts unset for each new document, and a use before any creation
must produce a source-linked diagnostic, not guess. A new document resets `it`;
the only output header must start the document, so it is not a nested scope.
The parser preserves references; `artifactspec.validation.validate` checks these
rules and returns a `ValidationResult` containing diagnostics and resolved
references. Duplicate names, unresolved and ambiguous references are errors.
Version 2 plugin metadata permits exact object-type checking for properties;
legacy version 1 metadata produces `unverified_type` warnings rather than a
false claim that the types were checked. A result is valid if it has no errors;
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
representations and renderers through the registry. The phase-specific context
protocols and implementation of those layers are not provided by this parser.
The following conceptual types describe intended relationships, **not current
Python classes or a finalized wire format**:

```text
ContentNode       = semantic_type + typed_properties + provenance
Representation    = content_reference + output_type + representation_kind + provenance
Composition       = output_type + ordered_placements + optional_playback + provenance
RendererRequest   = composition + output_options
RendererResult    = artifacts + warnings + provenance
Provenance        = zero_or_more_source_spans
```

An image composition has static placements and no playback; an animation
composition needs an explicit playback model. These are intended constraints,
not checks performed by the current parser. The exact value types, placement
model, output options and renderer contracts remain to be designed. Typed parse
nodes only carry syntax and string literals; they are not these semantic types.

For example, a domain timeline could be semantic content describing historical
events; an image representation could lay those events out in a static diagram.
An animation representation could depict the same content, while its separate
playback composition schedules visual states over elapsed time. A content event's
date is not automatically an animation timestamp. Image output is static and
has no playback timeline; animation requires explicit playback timing semantics
before rendering. Neither layout, animation timing, interpolation nor output
rendering is implemented here.

Source spans are carried from statements and literals into the parse tree. Future
semantic, composition, and rendering phases must preserve enough source links to
explain diagnostics and output provenance; one semantic item or output element
may derive from multiple spans, and generated elements may have none. How to
represent many-to-many provenance, validate units and property types, negotiate
plugin/core compatibility, select representations, and approve fallbacks remains
open. The example flows above are design illustrations, not supported syntax or
claims of rendering capability.

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
stops at the first error. Installed capabilities are discovered from static
manifests; the command does not load plugins or execute handlers. Legacy
version 1 manifests produce warnings where type information is missing.

## Editor diagnostics

Run `artifactspec lsp` as a language server over standard input and output. It
loads installed static manifests at startup, uses the same validator and
validation codes as the CLI, and does not import plugin modules. Configure an
LSP client to start that command for ArtifactSpec documents; the server does not
register a file extension or install editor configuration. Restart it after
installing or changing plugins so that it can rediscover their metadata.

The server validates on document open and change, and clears diagnostics on
close. Both full and incremental changes are supported; LSP positions use the
encoding negotiated with the client (UTF-16 by default). Warnings and errors
are distinguished. Parsing remains first-error, and independent semantic
errors are collected. No renderer or plugin handler runs as part of validation.
