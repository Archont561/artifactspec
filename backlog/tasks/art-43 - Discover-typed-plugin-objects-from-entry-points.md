---
id: ART-43
title: Discover typed plugin objects from entry points
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 21:11'
updated_date: '2026-11-08 21:24'
labels: []
milestone: m-11
dependencies: []
priority: high
type: feature
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace duplicated static JSON manifests with user-defined typed Plugin declarations and pytest-style entry point imports. Installed distribution metadata supplies plugin versions. Discovery, validation and LSP now import plugin code as explicitly approved.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Typed Plugin declarations own all capability syntax and serialize through `to_dict()`; decorated handlers remain composable and no static plugin JSON is needed.
- [x] #2 Discovery imports and validates entry point objects, derives installed distribution versions, reports conflicts and failures, and supports explicit plugin selection and opt-out across CLI and LSP.
- [x] #3 SVG and events distributions, tests, documentation, packaging and CI migrate to this contract; trust and manual-plugin version behavior are explicit.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add BDD and regression tests for typed Plugin declarations, entry-point loading, versions, filtering and import trust. 2. Implement typed constructor declarations and decorators, distribution version binding, direct discovery and registry integration; retain composable parsing and rendering. 3. Migrate SVG and events, CLI and LSP selection, tests, docs and package checks. 4. Run full and isolated-install verification and quality gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented typed constructor declarations and decorated handlers in artifactspec.plugin, direct entry-point object discovery, installed-distribution version binding, and independent JSON serialization. Manual plugins report a null version. Discovery, validation, LSP and rendering now import selected plugins; all provide autoload opt-out and explicit selection. CLI capability details expose the complete Plugin serialization in a version 2 envelope, and import-time stdout is redirected for CLI/LSP protocol safety. Migrated SVG/events, removed plugin JSON from wheels, updated packaging and docs. Verified 373 tests with 96.62% coverage, 67 targeted tests on Python 3.11, isolated four-distribution builds and wheel smoke tests, Ruff, mypy, Gherkin, Vale, alint, actionlint, and dependency audit. The audit skipped unpublished local distributions. Remote CI has not been run for this branch.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced static plugin JSON discovery with typed Plugin entry-point objects and distribution-derived versions, preserving composition and adding selection controls. Verified full, Python 3.11, isolated-wheel and local quality gates.
<!-- SECTION:FINAL_SUMMARY:END -->
