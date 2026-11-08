# ArtifactSpec core

The core package provides decorator-based plugin registration and static
capability discovery. Discovery does not import installed plugin code; plugins
are trusted executable Python and must be approved before loading. The artifact
language, phase contexts, validation and rendering are not implemented yet.

```sh
artifactspec capabilities
artifactspec capabilities --details --output svg
```

The package root exports `VERSION`, read from installed distribution metadata.
Plugin interfaces live in `artifactspec.plugins`. See the
[plugin contract](https://github.com/Archont561/artifactspec/blob/main/docs/plugins.md)
for manifest format, trust boundaries, registration and CLI JSON schema.

The repository's `pixi run --locked test` task installs the local packages and
runs the core package's BDD and unit tests against current source. Reinstall
after changing package metadata.
