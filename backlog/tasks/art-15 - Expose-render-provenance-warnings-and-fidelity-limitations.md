---
id: ART-15
title: 'Expose render provenance, warnings, and fidelity limitations'
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 17:37'
labels: []
milestone: m-4
dependencies:
  - ART-14
  - ART-13
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents need to know which rendering choices were made and whether a result was degraded or requires review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Render results identify selected backend and representation and expose warnings and fallback decisions.
- [ ] #2 Where source links exist, results expose inspectable provenance; unavailable provenance is reported honestly.
- [ ] #3 Tests cover full-fidelity, fallback or unsupported-feature, and error cases with machine-readable results.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reassess existing result fields and tests. 2. Specify how unavailable provenance is distinguished from an empty source set. 3. Define and test machine-readable success, limitation, and error results without claiming visual fidelity.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reassessment: successful JSON render results identify renderer and representation, warnings and explicit null fallback; an installed legacy plugin test verifies warning propagation. Source spans are exposed, but an empty provenance list cannot distinguish unavailable provenance from no source-linked elements. Render failures currently emit text on stderr, not a machine-readable result; full-fidelity and unsupported/error result coverage therefore remain open.
<!-- SECTION:NOTES:END -->
