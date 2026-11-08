# ArtifactSpec core

The core package provides decorator-based plugin registration and static
capability discovery. Discovery does not import installed plugin code; plugins
are trusted executable Python and must be approved before loading. The core also
provides an output-aware parser and reference and declared-type validation,
with a validation CLI and language server. Plugin phase contexts and rendering
are not implemented yet.

```sh
artifactspec capabilities
artifactspec capabilities --details --output svg
artifactspec validate scene.art --format json
artifactspec lsp
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
