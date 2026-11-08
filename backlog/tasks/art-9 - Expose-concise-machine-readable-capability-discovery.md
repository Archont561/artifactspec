---
id: ART-9
title: Expose concise machine-readable capability discovery
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-0
dependencies:
  - ART-4
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent needs to discover installed output types and plugin capabilities without loading all documentation into its context.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The CLI provides concise capability summaries and an explicit way to request details.
- [ ] #2 Machine-readable output identifies installed plugins, supported outputs, phrases, properties, representations, and renderers as available.
- [ ] #3 Tests cover empty installations, installed contributions, output filtering, and documented output schema.
<!-- AC:END -->
