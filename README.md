# ArtifactSpec

[![CI](https://github.com/Archont561/artifactspec/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Archont561/artifactspec/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/Archont561/artifactspec/graph/badge.svg)](https://codecov.io/gh/Archont561/artifactspec)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

An early scaffold for an agent-friendly framework for producing artifacts.
Both Python distributions currently expose only `VERSION`; the CLI, artifact
language, plugin API, and Manim renderer are not implemented.

## Development

```sh
pixi run test
pixi run test-manim
pixi run test-scripts
pixi run coverage-all
pixi run typecheck
pixi run check-packages
pixi run audit
pixi run -e gherkin lint-features
pixi run hooks-install
```

Each package's `pyproject.toml` declares its version. `VERSION` reads installed
distribution metadata. Package test and coverage tasks first install the local
projects without network access, then test the current source via `PYTHONPATH`.
For other work needing installed packages, run `pixi run install-projects` and
rerun it after changing package metadata or when a clean Pixi environment is
created. Script tests live in `scripts/tests/`.

See [CI](docs/ci.md) and [release preparation](docs/releases.md) for
compatibility, security, packaging checks, and sandbox publishing. Examples
remain empty until the API is stable.

## License

ArtifactSpec is licensed under the [MIT License](LICENSE).
