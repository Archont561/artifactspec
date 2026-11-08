---
id: ART-18
title: Implement declarative timed animation states
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-5
dependencies:
  - ART-17
  - ART-14
  - ART-7
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A user needs to describe what an animation should look like at specified times and obtain predictable transitions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A supported animated property can be declared at multiple times and interpolated according to the documented rules.
- [ ] #2 Invalid times, conflicting states, and unsupported interpolation produce actionable diagnostics.
- [ ] #3 BDD and renderer-level tests verify endpoints, an intermediate state, and failure cases.
<!-- AC:END -->
