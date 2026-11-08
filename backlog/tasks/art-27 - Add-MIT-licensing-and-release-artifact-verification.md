---
id: ART-27
title: Add MIT licensing and release artifact verification
status: Done
assignee: []
created_date: '2026-11-08 02:54'
updated_date: '2026-11-08 02:58'
labels: []
dependencies: []
priority: high
type: task
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Packaging needs explicit licensing and reproducible verification before a release rehearsal.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both distributions declare MIT license and include the license in built artifacts.
- [x] #2 Automated checks build and validate wheels and source distributions, including an installation smoke test.
- [x] #3 Release documentation describes a manual TestPyPI rehearsal and a real release without automatically publishing.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Inspect current configuration, add narrowly scoped tooling and CI integration, document limitations, and verify locally before checking acceptance criteria.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added MIT license to both distributions, release metadata and a changelog; verified wheel and sdist licenses, Twine checks and clean virtualenv smoke installation with pixi run check-packages. Documented authorized rehearsal and release steps.
<!-- SECTION:FINAL_SUMMARY:END -->
