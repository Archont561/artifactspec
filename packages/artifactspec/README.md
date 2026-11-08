# ArtifactSpec core

The core package provides decorator-based plugin registration and static
capability discovery. Discovery, validation, LSP, and rendering import installed
plugins, which are executable Python and are not sandboxed. Install only trusted plugins, or disable autoload to select them
explicitly. The core also provides an output-aware parser and reference and
declared-type validation, with a validation CLI and language server. Plugins can
materialize semantic content. The optional `artifactspec-svg` distribution
provides image syntax and SVG rendering; `artifactspec-events` provides dated
event syntax and layouts. Core contains no built-in content plugin. Plugin declarations live in typed Python `Plugin` objects; installed JSON
manifests are no longer used.

```sh
artifactspec capabilities
artifactspec capabilities --details --output image
artifactspec validate scene.art --format json
artifactspec lsp
artifactspec render scene.art --representation diagram --renderer svg --output scene.svg
```

The package root exports `VERSION`, read from installed distribution metadata.
Plugin declarations live in `artifactspec.plugin`. See the
[plugin contract](https://github.com/Archont561/artifactspec/blob/main/docs/plugins.md)
for typed declarations, trust boundaries, registration and CLI JSON schema. See the
[language contract](https://github.com/Archont561/artifactspec/blob/main/docs/language.md)
for parser syntax, typed nodes and source spans.

The repository's `pixi run --locked test` task installs the local packages and
runs the core package's BDD and unit tests against current source. Reinstall
after changing package metadata.

See the [rendering contract](https://github.com/Archont561/artifactspec/blob/main/docs/rendering.md) for plugin trust, phase contexts, outputs, and limitations.
