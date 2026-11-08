---
id: ART-22
title: Provide source-linked language server diagnostics
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 15:40'
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
- [x] #1 A documented LSP server publishes diagnostics with source ranges for valid and invalid open documents.
- [x] #2 Edits update diagnostics and clear resolved errors without requiring a full renderer execution.
- [x] #3 Tests cover document open, change, error recovery, and consistency with CLI validation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add BDD and protocol tests for opening, changing and clearing diagnostics, and CLI consistency.
2. Implement an stdio LSP server using the user-approved pygls library and the shared static-metadata validator, correctly converting Unicode positions to LSP ranges.
3. Document editor startup and validate in an isolated environment. Declare the dependency in package and Pixi manifests; defer lock repair to the relock bot when a PR is separately authorized.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
User selected pygls rather than a hand-rolled protocol implementation. Pixi relock will require a separately authorized PR.

Implemented pygls stdio server with static plugin metadata, shared CLI diagnostics, negotiated position encoding and full/incremental document sync. Protocol BDD/unit subprocess tests cover open, fixes, UTF-16 supplementary characters, incremental edits, close, empty document, shutdown and metadata errors; installed wheel smoke includes LSP creation. Python 3.11 core: 97 passed. Linux Python 3.13: 155 passed, 1 lock-dependent test deselected, 97.67% coverage; quality and package checks passed. Full locked verification is blocked until the relock bot updates pixi.lock; retain In Progress until then.
<!-- SECTION:NOTES:END -->
