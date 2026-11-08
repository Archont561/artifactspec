# Contributing to ArtifactSpec

Thanks for helping build ArtifactSpec. The repository is an early scaffold: the
language, CLI, plugin API, and renderer are planned, not implemented. Please
check the [backlog](backlog/README.md) and relevant decisions before proposing
work, and avoid presenting planned capabilities as finished.

## Set up

The locked Pixi workspace targets Linux x86-64 (`linux-64`). Install Pixi, clone
the repository, and run:

```sh
pixi install --locked
pixi install --locked -e gherkin
pixi run --locked bun-install
pixi run --locked install-projects
```

The local projects are not editable Pixi dependencies. Package test and coverage
tasks install them without build isolation and test the current source. Re-run
`install-projects` after changing package metadata. Default-environment activation
adds `src` directories belonging to tracked or unignored `pyproject.toml` files
to `PYTHONPATH`. The optional Manim environment is installed separately with
`pixi install --locked -e manim`; see the [README](README.md). Run
`pixi run install-hooks` to check and install the hooks defined in
`lefthook.yml` (agents must do this at session start). Lefthook backs up existing
non-Lefthook hooks as `.old` files but does not run those backups automatically;
integrate any custom hooks you need separately.

Alternatively, open the project with a Dev Containers-compatible editor. The
container setup requires network access. For the published sandbox and offline
restore procedure, see [CI](docs/ci.md).

## Make a change

1. Review the relevant backlog task, specification, and decisions. Use
   `pixi run backlog` and its task instructions to create or update backlog
   records rather than editing task files directly.
2. Keep product code, tests, and Gherkin features in the owning package. Put
   repository scripts and their tests under `scripts/` and `scripts/tests/`.
   For user-visible behavior, add a scenario and a failing test first when
   practical.
3. Update the relevant documentation and report any behavior or checks that
   remain unimplemented or unverified. Keep `examples/` empty until the public
   API is stable.

## Built-in CLI commands

Each public Python module directly inside
`packages/artifactspec/src/artifactspec/commands/` exposes an `app = typer.Typer()`.
Use `@app.command()` for one or more commands, and `app.add_typer()` for nested
command groups. `cli.py` discovers modules in sorted order and registers each
app directly; adding commands requires no change to the entry point. Unnamed
module apps contribute their commands at the root (so existing commands such
as `artifactspec validate FILE` stay unchanged). A named module app, for example
`typer.Typer(name="tools")`, registers a group instead. Name groups that need
callbacks or group options: Typer cannot run callbacks on unnamed, flattened
apps, so those are rejected. Nested groups retain their own names, callbacks,
options and commands. Duplicate names at the same command-tree level, cyclic
apps, and missing or invalid module apps fail explicitly at startup. Module
names beginning with `_` and subpackages are ignored. Add package-local tests
and documentation for new commands.

This is for trusted, built-in code: discovery **imports and executes** the
command modules. It is separate from installed plugin discovery, which continues
to read static metadata without importing plugins. Adding third-party CLI
commands through this mechanism is not supported or sandboxed.

## Checks

Run the checks relevant to your change; the full CI suite includes:

```sh
pixi run --locked lint
pixi run --locked format-check
pixi run --locked typecheck
pixi run --locked check-packages
pixi run --locked audit
pixi run --locked alint
pixi run --locked actionlint
pixi run --locked -e gherkin lint-features
pixi run --locked coverage-all
```

The coverage gate requires at least 91% total line coverage across the two
package source trees. It does not include repository scripts, native code, or
external programs; see [CI](docs/ci.md) for scope, conditional jobs, and Codecov
behavior. Package builds and dependency auditing need network access. For a
focused run, use `pixi run --locked test`, `test-manim`, or `test-scripts`.

## Pull requests

Use [Conventional Commits](https://www.conventionalcommits.org/) for commit
messages, such as `fix: handle missing input`. Explain the change, tests, and any
limitations in the pull request. CI chooses checks based on changed paths; the
stable **CI result** job reports the aggregate result. Pull requests are merged
using rebase merge only, not merge commits or squash merges.

Do not commit credentials, generated distributions, or local environments. Release
and publishing steps require separate authorization; see
[release preparation](docs/releases.md).

## Documentation quality

Run `pixi run --locked lint-prose` to check spelling, project terminology, and
selected editorial rules in the root guides, package READMEs, `docs/`, and
Markdown under `backlog/`. Errors fail the check; review warnings where useful.
The backlog uses a smaller editorial rule set. Preserve technical meaning and
examples, and add legitimate project vocabulary rather than suppressing errors.

Use `pixi run --locked alint` for repository structure and configuration. The
Vale and alint configurations are independent. Vale 3.26.0 is pinned through
Bun for the Linux x86-64 developer environment. The first Bun install requires
network access; the binary is not included in the offline Pixi sandbox. Selected
upstream style rules are vendored, so routine checks do not run `vale sync`.
See `.vale/styles/README.md` for sources and update instructions.
