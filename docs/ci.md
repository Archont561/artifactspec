# Continuous integration

The single `scripts/detect_changes.py` command compares Git revisions and emits
JSON plus scalar flags to `GITHUB_OUTPUT` and `GITHUB_ENV` when present. The
workflow consumes job outputs; environment values are local to their job.

- Only `docs/`, `backlog/`, root README/CHANGELOG, or a package README: run the
  docs whitespace check, not Python package suites.
- Only `scripts/` (including its `scripts/tests/` suite), optionally with docs:
  run the scripts suite; also check changed docs whitespace when present.
  Package paths, including any `tests/scripts/` paths, trigger full CI.
- Any other change, an empty diff, a missing base, or a failed comparison: run
  full checks. Git renames are treated as deletion plus addition so moving code
  into docs cannot hide a code change.
- Conventional commit validation and the final CI result gate always run.

Pull requests compare from the merge base. Ordinary pushes compare their before
and after commits, and fail commit lint if either revision is unavailable. A new
branch push has no before revision and runs full CI. For new branch pushes and
force-pushes, commit lint checks all commits since the merge base with the default
branch, regardless of whether the old head is still available. This also checks
commits retained across a force-push. If the merge base or default branch is
unavailable, lint fails closed. For a force-push to the default branch, or its
initial creation, lint checks all commits reachable from HEAD instead: the remote
default branch points to the new head and cannot be a useful comparison base.
A manual run without a base checks commits since the default branch's merge base
when run on another branch, or all reachable commits on the default branch. An
unavailable change-scope comparison still runs full CI.

Full CI runs coverage across both packages and uploads `coverage.xml` with the
Codecov action. Configure the `CODECOV_TOKEN` repository secret where required by
Codecov. Fork pull requests still run coverage but skip the upload, since secrets
are not generally available to them. The coverage.py configuration fails reports
below 91% total line coverage across the two package source trees; the full CI job
uses this same gate before upload. The separate core-only `coverage` task applies
the threshold to the core package alone. Script tests are run, but script code is
not included in this coverage figure. Coverage uses subprocess instrumentation to
include exercised package lines. Native code and external programs are not
measured. A successful coverage upload or render does not establish visual
correctness.

Merge pull requests using **rebase merge only**; do not use merge commits or
squash merges. Configure repository merge settings accordingly where possible.

For branch protection, use the stable **CI result** job as the required check,
not a conditionally skipped docs, scripts, or full job. Validate the exact check
name and status behavior in GitHub before enabling protection.

Local commands:

```sh
pixi run test-scripts
pixi run coverage-all
pixi run actionlint
python scripts/detect_changes.py --base BASE --head HEAD --event pull_request
```

Full CI also runs mypy, builds and checks both distributions, runs a Python
dependency audit, and tests the core package on Python 3.11–3.14 across Linux,
macOS, and Windows. These matrix jobs install with pip rather than Pixi. Full
CI also imports Manim and checks FFmpeg in its optional Pixi environment. The
Manim-named distribution is a version-only placeholder; no renderer tests
currently exist. The
package metadata has no upper Python bound, so later Python versions are not
currently covered by this matrix. The expanded plugin test suite requires verification on GitHub.

`pixi run audit` checks known Python package vulnerabilities in the default
Pixi environment using pip-audit and skips editable distributions. It is also
run weekly in a separate scheduled workflow. It does not audit OS packages,
conda native libraries, Bun dependencies, or GitHub Actions. Dependabot proposes
updates for GitHub Actions, Python package metadata, and the root npm manifest;
it does not update `pixi.lock`. The separate relock workflow checks Pixi lock
consistency on pull requests and, for same-repository non-Dependabot branches,
can commit a refreshed lock and dispatch CI. Fork and Dependabot PRs require a
manual lock update with suitable permissions. The workflow does not publish a
sandbox from a pull request. Review bot changes and require the repaired-head CI
to pass. The bot has refreshed a lock and dispatched CI in this repository;
GitHub may require approval for PR workflows triggered by the bot's commit. Hatchling updates to 1.30
or newer are temporarily ignored because the locked Twine 6.2 rejects the newer
metadata. Upgrade and relock Twine, then verify package builds before removing
that ignore. Existing incompatible Dependabot PRs will remain red until revised
or closed.

Bun 1.4 can use the v1 `bun.lock` format; it is kept at v1 for compatibility
with Dependabot's older Bun updater. If regenerating the lock produces v2, use
Bun 1.3.14 to regenerate it, then verify with `bun install --frozen-lockfile`
using the workspace's Bun 1.4.2. Dependabot's npm update failure on the initial
run could not be inspected in this environment, so this workaround still needs
remote confirmation.

## Sandbox publishing

`.github/workflows/pixi-sandbox.yml` follows the release-pinned publisher used
in other Archont561 repositories: on relevant pushes to `main` or manual
invocation, it packs, verifies, and publishes `sandbox/developer-linux-64`.
It uses a checksum-verified pixi-sandbox 0.9.0 release and the repository token.
It has succeeded on main.

The bundle contains the locked `default` and `gherkin` environments plus Pixi
and pixi-sandbox. The optional `manim` environment is not packed; it uses the
PyPI Manim distribution with conda-forge's prebuilt ManimPango and PyCairo
bindings and FFmpeg. Local project source paths are deliberately not Pixi
requirements, because native pixi-sandbox only transports locked wheels.
`pixi run install-projects` installs both local projects as non-editable packages
using the locked Hatchling backend and without dependency resolution or build
isolation. Package-test and coverage tasks run this first; default-environment
activation discovers tracked or unignored Python projects with `src` directories
and adds those paths to `PYTHONPATH` so coverage measures the checkout. This does not add local
project wheels to the sandbox; the checkout is required after restore. Bun's
`node_modules` are not packed, so Bun tooling requires a separate install.

Once the branch is published and available from `origin` (or transferred into
the local Git repository), run `scripts/restore.sh`. Set
`PIXI_SANDBOX_FETCH=skip` on an airlocked host to forbid a fetch, and
`PIXI_SANDBOX_USER_TOOLS=skip` to avoid registering user tools. After restore,
run `pixi run --frozen install-projects` to install the local projects. GitHub
Actions needs permission to write repository contents for the publisher;
publishing is not attempted on pull requests. Both publishing and offline restore
have succeeded. The optional Manim environment is checked separately in CI and
is not included in the offline developer bundle.
