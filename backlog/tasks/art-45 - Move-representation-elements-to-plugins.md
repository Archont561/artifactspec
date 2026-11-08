---
id: ART-45
title: Move representation elements to plugins
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 21:44'
updated_date: '2026-11-08 21:49'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Core currently owns text and rectangle models and constructors even though visual elements and their serialization belong to plugins. The user wants generic core composition and plugin-owned string rendering. SVG and events must remain independently installable and composable. Operators are explicitly out of scope.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Core composition stores plugin-owned elements through a generic API and preserves per-element source provenance without shape-specific models or constructors.
- [x] #2 SVG plugin defines safe string-renderable text and rectangle elements, and its renderer rejects incompatible elements.
- [x] #3 Independent SVG and event plugins compose mixed documents while event image and report representations remain usable without importing the SVG plugin.
- [x] #4 BDD, property and installed-wheel tests cover escaping, provenance, extensibility and compatibility; documentation and quality gates are updated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add failing BDD and unit tests for plugin-owned elements, generic provenance, SVG serialization, unsupported formats and mixed plugins. 2. Replace core shape models and constructors with generic payloads and source links. 3. Implement SVG element classes, migrate SVG and independent event representations, and simplify the SVG renderer. 4. Migrate existing plugin examples and tests, document the breaking API, and verify full quality gates and isolated installations. Operators are out of scope.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Core now carries opaque plugin-owned values and named-node source links via context.add; SVG and events define their own output-specific values and SVG strings. The SVG renderer checks the format marker and custom string method, and trusted plugins remain responsible for safe markup. Operators were explicitly removed from scope. Verified 396 tests with 97.14% coverage, 84 targeted Python 3.11 tests, isolated wheel builds and independent and mixed plugin smoke tests, Ruff, formatting, mypy, Gherkin, Vale, alint, actionlint and diff checks. Dependency audit found no known vulnerabilities; four unpublished local distributions were skipped. Remote CI was not run.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved shape-specific elements and serialization out of core into plugins, preserving provenance and independent mixed composition. SVG uses plugin-owned string-renderable values. Verified full tests, isolated wheels, Python 3.11 tests and local quality gates.
<!-- SECTION:FINAL_SUMMARY:END -->
