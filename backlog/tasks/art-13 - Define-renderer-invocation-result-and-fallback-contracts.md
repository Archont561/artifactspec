---
id: ART-13
title: 'Define renderer invocation, result, and fallback contracts'
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 16:51'
labels: []
milestone: m-3
dependencies:
  - ART-2
  - ART-3
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: spike
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A rendered artifact needs a predictable lifecycle and enough information for an agent to inspect what happened.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define renderer inputs, output artifacts, capability negotiation, error handling, and atomic output behavior.
- [x] #2 Define result metadata for renderer identity, representation, warnings, fallback, and source provenance where available.
- [x] #3 Document unsupported-feature and fidelity policies and how editable and non-editable output are distinguished.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Agree on the first end-to-end rendering slice and trust boundary.
2. Specify typed semantic content, selection/composition, renderer request/result, provenance, explicit fallback and output safety contracts.
3. Document unsupported features and verify the contracts against tests and the selected backend.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Documented explicit trusted plugin and representation/backend selection, renderer contexts, single byte artifact, atomic replacement, errors, source provenance, warnings, limitations, editable flag and explicit null fallback (no implicit fallback is permitted). Tested locally including atomic failure and existing-file preservation.
<!-- SECTION:NOTES:END -->
