---
id: ART-37
title: Register built-in Typer applications and nested command trees
status: Done
assignee: []
created_date: '2026-11-08 16:09'
updated_date: '2026-11-08 16:12'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace NAME and handler registration with module-level Typer apps registered directly by the CLI. Preserve existing command invocations and support nested Typer command groups.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each public command module exposes a Typer app; the CLI discovers and registers those apps without a separate NAME or handler registry.
- [x] #2 Multiple commands and nested Typer groups are available with their original names, options, and callbacks, and collisions fail explicitly.
- [x] #3 Existing CLI commands, installed entry points, trust boundaries and tests remain functional; documentation explains the convention.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write failing BDD and tests for module apps, multiple commands, and nested groups.
2. Register discovered Typer apps directly and migrate existing commands while preserving their public syntax.
3. Update property tests and documentation, review, and run checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added failing BDD and unit cases first, then migrated built-ins to Typer apps mounted directly with add_typer. Unnamed apps flatten into the root; named groups retain callbacks, options and nested commands. Validated duplicate names per effective scope, cycles, invalid module apps and unnamed callbacks that Typer would drop. Added generated tree checks and documented trusted-code boundary and conventions. Reviewed changes against refactor and clean-code skills. Verified 193 tests passed and 97.71% coverage; one locked Pixi activation test remains deselected due to the pending Hypothesis bot relock in ART-35. Python 3.11 with the minimum Typer 0.24 passed 124 core tests (two upstream Click deprecation warnings). Package builds, installed entry points and quality checks passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built-in modules now expose directly registered Typer apps with nested command groups, preserved CLI syntax and collision checks.
<!-- SECTION:FINAL_SUMMARY:END -->
