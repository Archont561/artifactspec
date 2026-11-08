---
id: ART-23
title: Verify wheel-backed skill installation interoperability
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-7
dependencies: []
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: spike
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The proposed skill installer relies on behavior not yet established for Skills CLI lockfiles and linked wheel content.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test lockfile creation and updates, Skills CLI listing or restore behavior, and agent discovery against a wheel-installed skill.
- [ ] #2 Document symlink behavior on supported platforms, safe removal or updates, and a copy fallback.
- [ ] #3 Record verified compatibility and limitations without claiming unsupported interoperability.
<!-- AC:END -->
