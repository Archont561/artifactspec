---
id: ART-12
title: Implement representation selection and artifact composition
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 17:37'
labels: []
milestone: m-3
dependencies:
  - ART-2
  - ART-4
  - ART-5
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Content should be reused across artifact types without assuming one layout or renderer works everywhere.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A documented content model can select compatible representations and compose them for at least two supported outputs or forms.
- [x] #2 Incompatible or unavailable representations fail explicitly or use a documented, visible fallback.
- [x] #3 Tests demonstrate semantic reuse and verify that content timeline semantics remain separate from animation playback.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Model built-in events using a strict ISO calendar date and label, preserving declaration order without animation playback semantics. 2. Add BDD and generated tests for same-content image/report composition, source links, invalid and missing fields, and explicit no-playback behavior. 3. Implement the trusted basic plugin extension, document its boundaries, and verify the package and quality gates. 4. Reassess ART-14 and ART-15 against their acceptance criteria.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The approved basic event slice stores a strict ISO calendar date and a nonblank label as semantic node properties. Image and report compositions preserve declared event order, use distinct text forms, preserve source spans, and do not infer playback timing. Grouped and approximate dates, animation, and report rendering remain unsupported. Static validation does not execute plugin value checks.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented and documented dated semantic events with explicit calendar validation and output-specific static composition. BDD, generated date and error tests, CLI SVG and installed-wheel smoke tests pass; the full local suite passed 287 tests with 96.66% coverage.
<!-- SECTION:FINAL_SUMMARY:END -->
