---
id: ART-22
title: Provide source-linked language server diagnostics
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-2
dependencies:
  - ART-8
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Interactive authors and agents benefit from the same validation rules while editing, without waiting for a render.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented LSP server publishes diagnostics with source ranges for valid and invalid open documents.
- [ ] #2 Edits update diagnostics and clear resolved errors without requiring a full renderer execution.
- [ ] #3 Tests cover document open, change, error recovery, and consistency with CLI validation.
<!-- AC:END -->
