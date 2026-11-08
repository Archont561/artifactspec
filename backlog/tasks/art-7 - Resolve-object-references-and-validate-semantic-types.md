---
id: ART-7
title: Resolve object references and validate semantic types
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-2
dependencies:
  - ART-6
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Syntax alone cannot establish whether objects exist or properties and phrases are meaningful in the chosen output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Named references and “it” resolve according to the documented scope rules.
- [ ] #2 Missing, ambiguous, wrong-type, and unsupported-output references produce actionable source-linked diagnostics.
- [ ] #3 Package-local tests cover reference scope boundaries and both valid and invalid inputs.
<!-- AC:END -->
