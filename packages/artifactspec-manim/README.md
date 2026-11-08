# ArtifactSpec Manim scaffold

`artifactspec-manim` is a placeholder for a possible future Manim integration. It
currently exposes only `VERSION`, read from installed distribution metadata. It
does not depend on Manim and does not implement a renderer.

After installing the local project, inspect the version with:

```python
from artifactspec_manim import VERSION

print(VERSION)
```

The version is declared in this package's `pyproject.toml`. The repository's
`pixi run --locked test-manim` task installs the local packages and runs this
package's BDD tests against the current source. Reinstall after changing package
metadata. See the [repository](https://github.com/Archont561/artifactspec) for
the design, contribution guide, and current status.
