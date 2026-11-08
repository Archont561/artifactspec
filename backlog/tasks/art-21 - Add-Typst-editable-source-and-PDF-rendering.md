---
id: ART-21
title: Add Typst editable-source and PDF rendering
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-4
dependencies:
  - ART-14
  - ART-12
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reports should support a backend that provides both generated PDF and editable Typst source rather than only a flattened output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A supported report specification generates editable Typst source and a PDF through a documented backend.
- [ ] #2 Unsupported representations and missing Typst tooling produce actionable diagnostics and explicit fallback behavior.
- [ ] #3 Tests verify source generation, PDF creation when the backend is available, and error handling.
<!-- AC:END -->
