---
id: ART-1
title: Specify the first controlled-language grammar and reference rules
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 14:46'
labels: []
milestone: m-1
dependencies: []
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: spike
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents need a deterministic, compact language rather than inventing commands. The specification leaves syntax and the scope of “it” unresolved.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document a small output-aware grammar with examples and unambiguous phrase and statement boundaries.
- [x] #2 Specify object naming, resolution, and the scope and reset behavior of “it”, including ambiguous and missing references.
- [x] #3 Document how unknown or conflicting phrases are reported and distinguish illustrative syntax from implemented syntax.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Agree a minimal output-aware grammar and reference model before implementation.
2. Document statement boundaries, registered phrase matching, naming, it scope, and diagnostic cases.
3. Verify the specification against package-local BDD parser tests.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
User approved the Output/Create/Set subset. docs/language.md specifies line and phrase boundaries, output compatibility, naming, the future document-scoped it and named reference semantics, and conflict/unknown diagnostics. BDD and edge-case tests verify the implemented parsing boundary; semantic resolution is explicitly deferred to ART-7.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Documented and implemented the first controlled grammar, with source-linked error cases and separately specified reference semantics. Verified by BDD and parser tests on Python 3.11 and 3.13.
<!-- SECTION:FINAL_SUMMARY:END -->
