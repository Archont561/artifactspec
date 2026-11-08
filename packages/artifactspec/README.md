# ArtifactSpec core scaffold

`artifactspec` is the planned core distribution for an agent-friendly artifact
framework. It currently exposes only `VERSION`, read from installed distribution
metadata. The artifact language, CLI, plugin interfaces, validation, and rendering
are not implemented.

After installing the local project, inspect the version with:

```python
from artifactspec import VERSION

print(VERSION)
```

The version is declared in this package's `pyproject.toml`. The repository's
`pixi run --locked test` task installs the local packages and runs the core
package's BDD tests against the current source. Reinstall after changing package
metadata. See the [repository](https://github.com/Archont561/artifactspec) for
the design, contribution guide, and current status.
