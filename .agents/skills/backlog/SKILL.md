---
name: backlog
description: Manage ArtifactSpec work using Backlog.md. Use for project tasks, acceptance criteria, and backlog status.
---

# ArtifactSpec backlog

Backlog.md stores project work in `backlog/`. Prefer the CLI to editing task metadata.
Use `pixi run backlog instructions overview` for the current workflow and
`pixi run backlog <command> --help` for command-specific options. In agent shells,
use `--plain` or `--json` where supported to avoid interactive views.

Do not mark work complete without checking its acceptance criteria. Backlog is
initialized in filesystem-only mode; do not assume Git automation is enabled.
