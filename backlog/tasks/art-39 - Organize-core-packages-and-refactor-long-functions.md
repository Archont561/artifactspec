---
id: ART-39
title: Organize core packages and refactor long functions
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 18:17'
updated_date: '2026-11-08 18:30'
labels: []
milestone: m-9
dependencies: []
priority: high
type: task
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Core source currently has many flat modules and several long functions that combine separate responsibilities. The user requested a clean break to a modular package layout and a refactor skill review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Core modules are organized into focused subpackages and project callers, CLI entry points, documentation and package tests use the new imports.
- [x] #2 Long production functions are reviewed for single-responsibility issues and appropriately decomposed without changing existing behavior beyond approved architectural changes.
- [x] #3 BDD, property and integration tests and package checks verify the new layout and behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Survey long production functions and public import usage. 2. Move core modules to coherent subpackages with clean-break imports and update consumers. 3. Refactor identified multi-responsibility functions in small tested steps, preserving behavior. 4. Verify quality gates and package installation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Moved core, CLI, editor, plugin and testing code into focused packages; updated callers and documented the intentional import break. Reviewed long functions against SRP and extracted phase creation/property application, validation diagnostics, LSP publishing, plugin manifest normalization, renderer invocation, basic representation branches, installed-manifest reading, and package-check phases. Remaining long signatures/orchestration are cohesive and were not split solely by line count. Applied clean-code and refactor skill reviews in tested steps.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
All 333 tests passed at 97.30% coverage; isolated wheel/sdist checks for all three distributions, 45 targeted Python 3.11 tests, Ruff, mypy, Gherkin, Vale, alint, actionlint and whitespace checks passed.
<!-- SECTION:FINAL_SUMMARY:END -->
