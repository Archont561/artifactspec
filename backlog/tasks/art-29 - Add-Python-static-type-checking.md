---
id: ART-29
title: Add Python static type checking
status: Done
assignee: []
created_date: '2026-11-08 02:54'
updated_date: '2026-11-08 02:58'
labels: []
dependencies: []
priority: high
type: task
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The future protocol-oriented plugin API needs type checks to catch regressions early.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A reproducible local type-checking task checks both package source trees.
- [x] #2 Full CI and local hooks run the type checker; tests and configuration document its scope.
- [x] #3 Existing source passes the configured type checks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Inspect current configuration, add narrowly scoped tooling and CI integration, document limitations, and verify locally before checking acceptance criteria.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added mypy with an optional-Manim import override and integrated it into full CI and Lefthook. Local mypy and forced pre-commit checks passed; workflow syntax passed actionlint. Remote CI is tracked separately.
<!-- SECTION:FINAL_SUMMARY:END -->
