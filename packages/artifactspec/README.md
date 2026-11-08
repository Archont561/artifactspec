# ArtifactSpec core

The core package provides decorator-based plugin registration and static
capability discovery. Discovery does not import installed plugin code; rendering
automatically loads installed plugins, which are executable Python and are not
sandboxed. Install only trusted plugins, or disable autoload to select them
explicitly. The core also provides an output-aware parser and reference and
declared-type validation, with a validation CLI and language server. Plugins can
materialize semantic content, including dated calendar events. The optional
`artifactspec-svg` distribution renders the small static SVG image slice.

```sh
artifactspec capabilities
artifactspec capabilities --builtin-basic --details --output image
artifactspec validate scene.art --builtin-basic --format json
artifactspec lsp --builtin-basic
artifactspec render scene.art --builtin-basic --representation basic --renderer svg --output scene.svg
```

The package root exports `VERSION`, read from installed distribution metadata.
Plugin interfaces live in `artifactspec.plugins`. See the
[plugin contract](https://github.com/Archont561/artifactspec/blob/main/docs/plugins.md)
for manifest format, trust boundaries, registration and CLI JSON schema. See the
[language contract](https://github.com/Archont561/artifactspec/blob/main/docs/language.md)
for parser syntax, typed nodes and source spans.

The repository's `pixi run --locked test` task installs the local packages and
runs the core package's BDD and unit tests against current source. Reinstall
after changing package metadata.

See the [rendering contract](https://github.com/Archont561/artifactspec/blob/main/docs/rendering.md) for plugin trust, phase contexts, outputs, and limitations.
