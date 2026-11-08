# ArtifactSpec

[![CI](https://github.com/Archont561/artifactspec/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Archont561/artifactspec/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/Archont561/artifactspec/graph/badge.svg)](https://codecov.io/gh/Archont561/artifactspec)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

ArtifactSpec is an early-stage Python project for describing and producing visual
artifacts with an agent-friendly language. The intended design separates semantic
content, representations, composition, and rendering.

**Current status:** the core provides plugin registration, static capability
discovery, parsing, validation, editor diagnostics, and a rendering pipeline.
The optional `artifactspec-svg` distribution renders static SVG; the Manim
distribution remains a version-only placeholder. Package roots expose `VERSION`
from distribution metadata.

Run `artifactspec capabilities --details` to inspect installed plugin metadata
without importing plugin code, or `artifactspec validate <file>` to validate a
specification. `artifactspec lsp` starts the editor diagnostics server. Rendering
automatically imports installed plugins, which execute arbitrary Python; install
only trusted plugins or use `--no-plugin-autoload` to select them explicitly.
See [plugin registration and discovery](docs/plugins.md), the
[language contract](docs/language.md), and [rendering](docs/rendering.md).

Python modules now live under `artifactspec.core`, `artifactspec.plugins`,
`artifactspec.editor`, `artifactspec.testing`, and `artifactspec.cli`; old flat
module imports are not retained. Update imports when upgrading.

## Repository guide

- [`packages/artifactspec`](packages/artifactspec/README.md) — core package.
- [`packages/artifactspec-svg`](packages/artifactspec-svg/README.md) — optional
  static SVG renderer plugin.
- [`packages/artifactspec-manim`](packages/artifactspec-manim/README.md) —
  renderer placeholder; it has no Manim dependency.
- [`backlog`](backlog/README.md) — product specification, decisions, milestones,
  and tasks.
- [`docs`](docs/README.md) — CI, release preparation, and development skills.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — setup, checks, and contribution process.

Examples remain empty until the public API is stable.

## Development

The locked Pixi workspace targets Linux x86-64 (`linux-64`). On a connected host
with Pixi installed:

```sh
pixi install --locked
pixi install --locked -e gherkin
pixi run --locked bun-install
pixi run --locked install-projects
pixi run --locked test
pixi run --locked test-manim
pixi run --locked test-svg
pixi run --locked test-scripts
pixi run --locked coverage-all
```

The full coverage task requires at least **91% total line coverage** across all three
package source trees. The number does not measure scripts or prove visual correctness. See
[CI](docs/ci.md) for the full check matrix and coverage scope.

Package test and coverage tasks install the local projects without build
isolation, then test the checkout. Default-environment activation discovers each
tracked or unignored `pyproject.toml` with a `src` directory and prepends those
source directories to `PYTHONPATH`, even from a subdirectory. Git-ignored
projects and projects without `src` are skipped. Run
`pixi run --locked install-projects` when work needs installed package metadata,
and rerun it after changing metadata or recreating the Pixi environment.

Manim is an optional PyPI dependency in the `manim` Pixi environment. Install
it with `pixi install --locked -e manim` and use it with
`pixi run --locked -e manim -x manim --version`. Its native ManimPango and
PyCairo bindings and FFmpeg are supplied by conda-forge. This does not implement
the ArtifactSpec renderer or make Manim a distribution dependency.

### Development container

Open the repository in a Dev Containers-compatible editor and choose **Reopen in
Container**. The container targets Linux x86-64 and requires network access on
first creation. Setup installs Git, GitHub CLI, pixi-sandbox, both locked Pixi
environments, Bun tooling, and the local packages. Global tools are separate
from `pixi.lock`. Container setup does not install Git hooks automatically;
run `pixi run install-hooks` to check and install them. Agents must do this at
session start (see [AGENTS.md](AGENTS.md)). Lefthook backs up pre-existing
non-Lefthook hooks as `.old` files, which it does not run automatically; integrate
any needed custom hooks separately.

OpenCode is optional: set `ARTIFACTSPEC_INSTALL_OPENCODE=1` on the host before
creating the container to install it. Authentication and model refresh remain
manual. For an offline sandbox restore, see [CI](docs/ci.md).

## License

ArtifactSpec is licensed under the [MIT License](LICENSE).
