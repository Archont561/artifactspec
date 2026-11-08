---
id: ART-5
title: Implement public phase contexts and plugin test helpers
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 16:51'
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
- [x] #1 Public phase-specific protocols support the approved plugin contribution contracts without exposing private implementation classes.
- [x] #2 artifactspec.testing supplies fake contexts that record observable operations, and a pytest plugin supplies fixtures backed by them.
- [x] #3 Tests exercise a plugin with fakes and core-provided contexts, including invalid operations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Establish approved phase-context contracts and define testable semantic operations for phrase, property, representation and renderer plugins without exposing internals.
2. Add BDD scenarios and failing property/unit tests, then implement core and fake contexts and pytest fixtures.
3. Verify plugin behavior and invalid operations and document the public API.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented public phase protocols, separate core builders, recording fakes and opt-in pytest fixture factories. BDD and generated tests exercise plugin handlers against fake and core contexts, with invalid operations rejected. Documented in docs/rendering.md. Verified in the full local suite.
<!-- SECTION:NOTES:END -->
