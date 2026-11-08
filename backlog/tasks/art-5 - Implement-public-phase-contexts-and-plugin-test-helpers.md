---
id: ART-5
title: Implement public phase contexts and plugin test helpers
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-3
dependencies:
  - ART-3
  - ART-2
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Plugin authors need to test behavior without importing internal property-assignment types or running a renderer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Public phase-specific protocols support the approved plugin contribution contracts without exposing private implementation classes.
- [ ] #2 artifactspec.testing supplies fake contexts that record observable operations, and a pytest plugin supplies fixtures backed by them.
- [ ] #3 Tests exercise a plugin with fakes and core-provided contexts, including invalid operations.
<!-- AC:END -->
