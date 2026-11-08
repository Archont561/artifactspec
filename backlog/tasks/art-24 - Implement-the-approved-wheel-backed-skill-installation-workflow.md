---
id: ART-24
title: Implement the approved wheel-backed skill installation workflow
status: To Do
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:50'
labels: []
milestone: m-7
dependencies:
  - ART-23
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent needs a discoverable installed skill while avoiding unsafe lockfile or source-directory changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The chosen CLI command installs a skill from the installed distribution and updates or creates the lockfile as specified.
- [ ] #2 Installation detects unsafe overlaps and handles unavailable symlinks with the documented fallback or a clear error.
- [ ] #3 Tests cover fresh install, existing lockfile, repeat install, and safe removal or update; compatibility limits are documented.
<!-- AC:END -->
