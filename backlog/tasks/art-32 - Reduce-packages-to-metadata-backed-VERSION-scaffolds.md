---
id: ART-32
title: Reduce packages to metadata-backed VERSION scaffolds
status: Done
assignee: []
created_date: '2026-11-08 03:03'
updated_date: '2026-11-08 03:05'
labels: []
dependencies: []
priority: high
type: task
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user requested removal of all existing product functionality, leaving each distribution with only a VERSION initializer and package-local BDD tests. pyproject.toml is the version source of truth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both package source trees contain only __init__.py, with VERSION as the sole explicit public export derived from installed metadata built from pyproject.toml.
- [x] #2 Each package has only a package-local version BDD feature and test that checks the version against pyproject.toml, installed metadata, and the minimal source layout.
- [x] #3 Build, isolated installation, scripts tests, combined tests, lint and CI configuration pass without the removed CLI or renderer.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Write version and layout BDD checks, remove product functionality, switch VERSION to installed metadata, update tooling and documents, verify wheel installation and suites, then prepare a clean source ZIP.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed the CLI and renderer, retained only metadata-backed VERSION package initializers and package-local BDD tests. The pyproject, installed metadata, mocked metadata lookup and minimal layout are checked. Built and installed both wheels in an isolated environment; 18 combined tests and all local lint, type, actionlint and audit checks passed. GitHub CI remains unverified.
<!-- SECTION:FINAL_SUMMARY:END -->
