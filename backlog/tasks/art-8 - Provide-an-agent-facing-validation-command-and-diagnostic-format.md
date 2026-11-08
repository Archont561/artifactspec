---
id: ART-8
title: Provide an agent-facing validation command and diagnostic format
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-2
dependencies:
  - ART-6
  - ART-7
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents need to correct specifications incrementally without inferring validity from rendering failures.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented CLI validation interface returns a nonzero status for invalid input and a successful status for valid input.
- [ ] #2 Human-readable and machine-readable diagnostics expose source location when available, severity, and actionable cause.
- [ ] #3 Package-local tests cover valid input, multiple errors, unknown capabilities, and stable machine-readable output.
<!-- AC:END -->
