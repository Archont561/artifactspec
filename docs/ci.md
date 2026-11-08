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

Pull requests compare from the merge base. Pushes compare their before and after
commits. A new branch push has no before revision: it runs full CI and commit
lint checks commits since the merge base with the default branch, failing if that
merge base is unavailable. A manual run without a base checks all commits
reachable from HEAD.

Full CI runs coverage across both packages and uploads `coverage.xml` with the
Codecov action. Configure the `CODECOV_TOKEN` repository secret where required by
Codecov. Fork pull requests still run coverage but skip the upload, since secrets
are not generally available to them. There is no coverage threshold yet.
Coverage uses coverage.py subprocess instrumentation and source directories to
include exercised Python package lines. Native code and external programs are
not measured. A successful coverage upload
or render does not establish visual correctness.

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
macOS, and Windows. These matrix jobs install with pip rather than Pixi. The Manim-named package
is a version-only placeholder; no renderer tests currently exist. The
package metadata has no upper Python bound, so later Python versions are not
currently covered by this matrix. The matrix awaits verification on GitHub.

`pixi run audit` checks known Python package vulnerabilities in the default
Pixi environment using pip-audit and skips editable distributions. It is also
run weekly in a separate scheduled workflow. It does not audit OS packages,
conda native libraries, Bun dependencies, or GitHub Actions. Dependabot proposes
updates for GitHub Actions, Python package metadata, and the root npm manifest; it does not update `pixi.lock`. Review
updates and regenerate the Pixi lock where necessary. Hatchling updates to 1.30
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
invocation, it packs, verifies, and publishes `sandbox/gherkin-linux-64`.
It uses a checksum-verified pixi-sandbox 0.9.0 release and the repository token.
The workflow has not yet been run in this repository.

This bundle contains only the isolated `gherkin` environment and the Pixi and
pixi-sandbox tools; it is **not** a developer-environment backup. The `developer`
bundle in `pixi-sandbox.toml` is not published by this workflow: native
pixi-sandbox 0.9.0 rejects the local editable PyPI paths for `artifactspec` and
`artifactspec-manim` in the default lock. Before enabling developer publishing,
provide a supported wheel-only or separate tooling environment, regenerate the
Pixi lock, and verify both the publisher and offline restore. Bun's installed
`node_modules` are not packed by this Gherkin-only bundle.

Once published, use the upstream pixi-sandbox restore instructions with the
`sandbox/gherkin-linux-64` branch. No restore launcher is currently provided
here. GitHub Actions needs permission to write repository contents for the
publisher; publishing is not attempted on pull requests.
