---
id: ART-11
title: Support approved plugin acquisition in the agent workflow
status: To Do
assignee: []
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-8
dependencies:
  - ART-9
  - ART-10
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent that identifies missing capabilities needs a safe, explicit handoff to obtain them on the user’s behalf.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A missing capability is reported with actionable information without silently installing a plugin.
- [ ] #2 Any acquisition or installation requires explicit user approval and reports the selected source and result.
- [ ] #3 Tests cover denied approval, failed installation, and successful rediscovery; trust limitations are documented.
<!-- AC:END -->
