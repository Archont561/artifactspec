---
id: ART-34
title: Discover built-in CLI commands from command modules
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 15:59'
updated_date: '2026-11-08 16:12'
labels: []
dependencies: []
priority: medium
type: task
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants the Typer CLI organized as command modules discovered and registered automatically, rather than adding each command to cli.py manually.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Built-in capabilities, validate and lsp commands are separate modules discovered automatically by the Typer app without changing their external behavior.
- [x] #2 Tests prove a new command module is registered without modifying cli.py, handle malformed or duplicate modules, and preserve both installed entry points and plugin trust boundaries.
- [x] #3 The internal command-module convention and trust boundary are documented, with package and quality checks passing.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add failing discovery and CLI behavior tests using a temporary built-in command module.
2. Split existing commands into modules and add deterministic registration with explicit validation.
3. Document the convention, review the refactor, and run package and quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added sorted package-local discovery of top-level public command modules using NAME and command, with explicit errors for invalid and duplicate definitions. Underscore modules and subpackages are excluded; installed plugin metadata remains separate and static. BDD and regression tests cover automatic registration, duplicate/malformed definitions, ignored helpers, existing CLI behavior and plugin no-import. Isolated wheel checks exercise capabilities, validate and lsp help through both entry points. Locked Linux Python 3.13 coverage-all: 163 passed, 97.79%; isolated Python 3.11 core: 104 passed. Package build, Ruff, mypy, Gherkin, alint, actionlint and offline lock checks passed. Refactor and clean-code review completed; no remaining findings. Remote OS CI not run.

The original NAME/command module convention was superseded by ART-37: command modules now expose Typer apps registered directly, with nested trees preserved.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved built-in CLI commands into discoverable modules, documented the convention and verified behavior, errors, packaging and test suites.
<!-- SECTION:FINAL_SUMMARY:END -->
