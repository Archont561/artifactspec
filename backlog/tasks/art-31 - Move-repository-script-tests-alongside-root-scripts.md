---
id: ART-31
title: Move repository script tests alongside root scripts
status: Done
assignee: []
created_date: '2026-11-08 02:58'
updated_date: '2026-11-08 03:00'
labels: []
dependencies: []
priority: high
type: task
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Repository-maintenance scripts are root-level tools, so their tests and behavioral specifications should be owned by scripts rather than a product package. Preserve the dedicated scripts-only CI path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Repository script tests and their behavioral features live under scripts/tests; product package tests remain package-local.
- [x] #2 Scripts-only CI runs the relocated tests and treats package paths conservatively; full CI also runs script tests.
- [x] #3 Local scripts suite, full combined suite and Gherkin, formatting and workflow checks pass with documented paths.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Move repository-script tests and feature beside root scripts; update CI classification and all test/lint paths; reconcile guidance and verify targeted and combined suites.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved repository script tests and their feature to scripts/tests; updated scope detection, Pixi tasks, Gherkin lint, agent guidance and specification. Scripts suite passed 16 tests, full suite passed 23 tests, and lint/format/actionlint/alint passed; remote CI remains unverified.
<!-- SECTION:FINAL_SUMMARY:END -->
