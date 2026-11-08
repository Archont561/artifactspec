---
id: ART-16
title: Add artifact preview and result inspection workflow
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-4
dependencies:
  - ART-14
  - ART-15
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The agent workflow requires a way to examine artifacts and report problems before declaring success.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented workflow can preview or inspect at least one supported rendered output and identify the resulting file.
- [ ] #2 The workflow reports validation errors, render warnings, and fidelity limitations without claiming visual or factual correctness.
- [ ] #3 Tests cover successful inspection, missing or invalid output, and warning propagation.
<!-- AC:END -->
