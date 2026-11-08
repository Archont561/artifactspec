---
id: ART-40
title: Extract and autodiscover the SVG plugin
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 18:17'
updated_date: '2026-11-08 18:30'
labels: []
milestone: m-9
dependencies:
  - ART-39
priority: high
type: feature
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants SVG-specific syntax and rendering separated into an installable artifactspec-svg plugin, and pytest-style installed plugin loading when rendering. Generic content must remain reusable without SVG.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The optional artifactspec-svg distribution advertises static metadata and provides SVG syntax and rendering independently of core semantic content.
- [x] #2 Rendering automatically loads installed plugins, supports a documented opt-out and reports conflicts and failures; capability discovery, validation and LSP do not execute plugin code.
- [x] #3 BDD and integration tests cover installation, metadata-only discovery, automatic rendering, opt-out, failures and conflicts; package checks verify isolated wheels.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add BDD and integration tests for installed metadata discovery and runtime autoload with opt-out. 2. Extract SVG serialization and backend into a separately packaged plugin, retaining generic semantic content in core. 3. Autoload installed plugins only at render time, preserving static-only discovery and explicit failure behavior. 4. Update packaging, CI and documentation; verify isolated wheel installs and quality gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created artifactspec-svg with a static manifest, separate SVG syntax serialization and renderer adapter. Rendering automatically loads installed plugins after metadata conflict preflight; --no-plugin-autoload permits explicit --plugin selection and ignores unrelated conflicts. Capability discovery, validation and LSP remain metadata-only. Updated package smoke tests, compatibility CI, documentation and trust guidance. Core installs and discovers without SVG.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
All 333 tests passed at 97.30% coverage, including BDD, property and integration coverage. Isolated builds and clean installations checked both CLI entry points, rendering and JSON success/failure; 45 targeted Python 3.11 tests and all local quality checks passed. Dependency audit found no known vulnerabilities; unpublished project packages were skipped.
<!-- SECTION:FINAL_SUMMARY:END -->
