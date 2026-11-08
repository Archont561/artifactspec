---
id: ART-28
title: Add Python compatibility testing
status: In Progress
assignee: []
created_date: '2026-11-08 02:54'
updated_date: '2026-11-08 02:58'
labels: []
dependencies: []
priority: high
type: task
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Declared Python support is not currently verified across interpreters or platforms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI tests the core package across the documented Python and operating system matrix.
- [ ] #2 Matrix failures participate in the stable CI result gate without running on docs-only or scripts-only changes.
- [x] #3 Document the tested matrix and limitations, including optional Manim.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Inspect current configuration, add narrowly scoped tooling and CI integration, document limitations, and verify locally before checking acceptance criteria.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Configured Python 3.11–3.14 core matrix on Linux, macOS and Windows as a full-CI required result. actionlint passed and the exact core test selection passed locally on Linux Python 3.13. GitHub matrix and other platforms remain unverified; ART-25 tracks remote CI verification.
<!-- SECTION:NOTES:END -->
