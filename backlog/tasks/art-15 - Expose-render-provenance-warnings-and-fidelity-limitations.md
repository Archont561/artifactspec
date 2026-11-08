---
id: ART-15
title: 'Expose render provenance, warnings, and fidelity limitations'
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
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
- [ ] #1 Render results identify selected backend and representation and expose warnings and fallback decisions.
- [ ] #2 Where source links exist, results expose inspectable provenance; unavailable provenance is reported honestly.
- [ ] #3 Tests cover full-fidelity, fallback or unsupported-feature, and error cases with machine-readable results.
<!-- AC:END -->
