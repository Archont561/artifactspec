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
commits. With no base, full CI runs and commit lint checks all commits reachable
from HEAD. A manual workflow run also takes this conservative path.

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
updates and regenerate the Pixi lock where necessary.
