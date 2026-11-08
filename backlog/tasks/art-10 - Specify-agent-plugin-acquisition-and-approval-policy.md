---
id: ART-10
title: Specify agent plugin acquisition and approval policy
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-8
dependencies:
  - ART-3
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: spike
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The envisioned agent may obtain missing plugins, but running untrusted Python can execute arbitrary code.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the approval boundary and how an agent reports plugin source, version, and relevant trust risks.
- [ ] #2 Specify how missing capabilities are surfaced without automatic unapproved installation or execution.
- [ ] #3 Identify dependency, provenance, metadata-discovery, and failure-handling requirements and unresolved security tradeoffs.
<!-- AC:END -->
