---
id: ART-48
title: Migrate independent plugins and tooling to composable contributions
status: To Do
assignee: []
created_date: '2026-11-08 22:20'
labels: []
milestone: m-12
dependencies:
  - ART-47
priority: high
type: feature
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The class-based contract is a breaking migration. The SVG and events plugins, third-party plugin guidance, testing helpers and isolated distributions must move together without introducing a built-in basic plugin or losing mixed-document support.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 SVG and events use the reviewed decorator-free contribution API, remain separately installable, and render mixed image documents with source provenance and plugin-owned elements.
- [ ] #2 Package-local BDD, integration and property tests plus isolated wheel checks cover standalone plugins, mixed output, metadata, CLI and LSP behavior, and subclass overrides with context isolation.
- [ ] #3 Documentation and migration guidance explain statement and property composition, discovery trust, handler execution, compatibility and distribution-derived versions; quality gates and supported Python versions pass.
<!-- AC:END -->
