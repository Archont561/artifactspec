---
id: ART-44
title: Move CLI commands and keep package initializers minimal
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 21:27'
updated_date: '2026-11-08 21:29'
labels: []
milestone: m-11
dependencies: []
priority: high
type: enhancement
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants command modules under the CLI package and package initializers to re-export APIs rather than define implementations. The existing command discovery, plugin registry, test fakes, and package-version initializers contain implementation code.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Commands live under the CLI package and command discovery, console entry points, errors, and nested Typer behavior remain functional.
- [x] #2 Package initializers only re-export their public APIs or declare export lists; implementation and package version lookup live in dedicated modules.
- [x] #3 BDD, import/layout and isolated-wheel tests cover the new structure; documentation and full quality gates are updated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add regression tests for command-module placement and re-export-only initializers. 2. Move command modules under the CLI package, extract CLI assembly, plugin registry, test contexts, and version lookups into modules while preserving public exports. 3. Update imports, package layout tests and documentation. 4. Run CLI, package, full coverage and quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified command discovery and nested groups in the full BDD suite, initializer-only exports with an AST regression, and the new command imports and absence of the legacy package in isolated built wheels. Full coverage: 375 tests passed, 96.65% coverage. Python 3.11 isolated installations: 68 targeted tests passed. Package builds and independent and mixed plugin smoke tests passed. Ruff, formatting, mypy, Gherkin, prose, alint, actionlint, and diff checks passed. Dependency audit found no known vulnerabilities; four unpublished local distributions were skipped. Remote CI was not run.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved built-in commands under the CLI package and extracted CLI assembly, registry, testing contexts, and version lookups from initializers. Preserved public re-exports and command behavior; verified with 375 tests, isolated package smoke tests, Python 3.11 targeted tests, and local quality checks.
<!-- SECTION:FINAL_SUMMARY:END -->
