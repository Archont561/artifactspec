# Contributing to ArtifactSpec

Thanks for helping build ArtifactSpec. The repository is an early scaffold: the
language, CLI, plugin API, and renderer are planned, not implemented. Please
check the [backlog](backlog/README.md) and relevant decisions before proposing
work, and avoid presenting planned capabilities as finished.

## Set up

The locked Pixi workspace targets Linux x86-64 (`linux-64`). Install Pixi, clone
the repository, and run:

```sh
pixi install --locked --all
pixi run --locked bun-install
pixi run --locked install-projects
```

The local projects are not editable Pixi dependencies. Package test and coverage
tasks install them without build isolation and test the current source. Re-run
`install-projects` after changing package metadata. Git hooks are optional:
`pixi run hooks-install` installs the checks defined in `lefthook.yml`.

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
