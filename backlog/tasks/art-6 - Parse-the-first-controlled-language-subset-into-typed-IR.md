---
id: ART-6
title: Parse the first controlled-language subset into typed IR
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-1
dependencies:
  - ART-1
  - ART-2
  - ART-4
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent needs predictable language processing before it can reliably validate or render an authored artifact.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented minimal output-aware subset parses into the agreed typed representation with source locations.
- [ ] #2 Unknown or malformed phrases fail with source-linked diagnostics rather than being interpreted as arbitrary instructions.
- [ ] #3 Package-local BDD tests cover valid, malformed, and ambiguous inputs.
<!-- AC:END -->
