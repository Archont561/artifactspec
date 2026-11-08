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

Each package's `pyproject.toml` declares its version. `VERSION` reads the
installed distribution metadata generated from that declaration, so reinstall
or rebuild the package after changing it. Each package has a BDD test for this
contract. Script tests live in `scripts/tests/`.

See [CI](docs/ci.md) and [release preparation](docs/releases.md) for
compatibility, security, packaging checks, and sandbox publishing. The current
sandbox publisher covers only Gherkin tooling, not the developer environment.
Examples remain empty until the API is stable.

## License

ArtifactSpec is licensed under the [MIT License](LICENSE).
