# Agent instructions

## Start each session with environment and hook setup

Before the backlog survey or project changes, check that Pixi is available with `command -v pixi`. If it is missing, run `sh scripts/restore.sh` from the repository root to restore the developer sandbox, then add the registered user tools to the current shell's PATH with `export PATH="$HOME/.local/bin:$PATH"` and verify `pixi --version`. Restore may need access to the sandbox branch and registers user tools by default; see `docs/ci.md`. If restore fails or Pixi remains unavailable, report the blocker rather than claiming setup succeeded.

Once Pixi is available, run `pixi run install-hooks` at the start of every session. It checks the Lefthook installation and installs or updates missing or stale hooks, then verifies them. Do not bypass a failed installation; report the error. Lefthook backs up existing non-Lefthook hooks as `.old` files but does not automatically execute those backups; inspect and integrate any needed custom hooks before relying on them.

## Start each session with a backlog survey

After environment and hook setup, before planning or changing the project, use `pixi run backlog` to survey the current state. For an initial orientation, run:

```sh
pixi run backlog instructions overview
pixi run backlog milestone list --plain
pixi run backlog task list --status "In Progress" --plain
pixi run backlog task list --status "To Do" --plain
```

For the relevant milestone, inspect its tasks with `backlog task list --milestone <id-or-title> --plain`, then view relevant tasks and their dependency graphs with `backlog task view <id> --plain`. Read the applicable backlog specification and decisions, check the workspace and Git state, and reconcile the survey with the user's request before selecting work. Use filters and pagination when the backlog is large. If no milestones exist, say so rather than inventing one. Do not let the survey override a direct user request or automatically start unrelated work.

Use Backlog.md commands to create and update backlog records. Before creating, executing, or finalizing tasks, read the corresponding Backlog.md instructions (`task-creation`, `task-execution`, or `task-finalization`). Keep task status, acceptance criteria, blockers, and handoff notes accurate; never mark unfinished or unverified work complete.

## Milestones, sprints, and releases

Treat each milestone as a sprint containing multiple related tasks, sized and sequenced to be completed together in one working session and delivered in one pull request. A milestone should produce a significant, coherent, verifiable product capability—not merely a collection of unrelated chores. When creating or revising milestones, define the intended product outcome, group tasks and dependencies around it, and make the scope realistic for that session and PR. When working on an existing milestone, survey and work through its relevant tasks as a coherent increment, subject to the user's request and authorization.

A completed milestone may justify a release rehearsal or a proper release. Assess readiness against the actual capability, tests, documentation, packaging, and release requirements; report gaps and propose the appropriate next step. Completion does not automatically authorize publishing a release. If the sprint cannot be finished safely in the session, report the remaining work and blockers and leave statuses truthful rather than forcing completion.

Do not push, create a pull request, merge, tag, publish, or release without explicit user authorization. A planned one-PR sprint is a delivery target, not permission to perform remote actions.

## Engineering rules

- Keep product features and tests in the package that owns the behavior. Repository scripts live under root `scripts/`, with their tests and script-specific features under `scripts/tests/`; do not put script tests in product packages.
- For user-visible features, write a Gherkin scenario and a failing test in the owning package (or in `scripts/tests/` for repository scripts) before implementation when practical.
- Property-test standalone functions wherever practical using varied cases, with Hypothesis or `pytest.mark.parametrize`. Keep BDD scenarios and example-based integration or regression tests where generated cases are not appropriate; do not replace meaningful assertions with arbitrary inputs.
- When implementing a new feature with TDD and BDD, apply `.agents/skills/clean-code-principles/SKILL.md` throughout. After the behavior is green and before the session handoff, review the changed Python files using `.agents/skills/refactor/SKILL.md`, make safe behavior-preserving improvements as appropriate, run the relevant checks, and report any remaining findings.
- Keep the CLI thin and public plugin interfaces testable without renderers.
- Keep examples empty until the public API is stable.
- Report checks that could not be run. Do not claim unfinished functionality is implemented.
- Do not merge, push, or rewrite shared history without explicit authorization.
- When merging an authorized pull request, use rebase merge only; never use merge commits or squash merges.
- For repository skills, read the relevant `.agents/skills/<name>/SKILL.md` when needed.
- Use `pixi run backlog` for Backlog.md commands and `pixi run skills` for the Skills CLI.

## Documentation quality

Use Vale for spelling, terminology, and selected editorial rules. Use alint for
repository structure and configuration; keep its rules separate in `.alint.yml`.
After documentation changes, run `pixi run --locked lint-prose` and
`pixi run --locked alint`. Vale scans the root guides, package READMEs, `docs/`,
and Markdown under `backlog/`. Errors fail the check; warnings are advisory and
should be reviewed. Backlog prose uses a smaller editorial rule set.

Preserve technical accuracy, code examples, and links when fixing findings.
Add legitimate terms to `.vale/styles/config/vocabularies/Project/accept.txt`;
do not disable rules merely to silence findings. The selected upstream style
rules are vendored and pinned, so routine checks do not run `vale sync`. See
`.vale/styles/README.md` before updating them. The locked Bun installation
provides the Linux x86-64 Vale executable; it is not part of the offline Pixi
sandbox. Ruff remains responsible for Python code quality.
