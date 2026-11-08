---
id: ART-9
title: Expose concise machine-readable capability discovery
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 14:12'
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
- [x] #1 The CLI provides concise capability summaries and an explicit way to request details.
- [x] #2 Machine-readable output identifies installed plugins, supported outputs, phrases, properties, representations, and renderers as available.
- [x] #3 Tests cover empty installations, installed contributions, output filtering, and documented output schema.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write failing package-local Gherkin scenarios and tests for static installed metadata discovery, filtering, and JSON CLI output.
2. Implement manifest validation and concise/detail discovery without importing installed plugin modules.
3. Test packaging and CLI behavior, document the schema, and run the complete quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented versioned JSON summary/details and output filtering using distribution-recorded static manifests without importing plugin code. Verified empty, installed-wheel, malformed, conflicting, filtered and exact-schema cases. CI matrix expanded to full core suite; remote matrix remains unverified.

The CLI was migrated to Typer at user request. The Pixi manifest now requires a bot-generated lock refresh; locked activation/CI verification is pending. Frozen checks with temporary Typer passed 87 tests (one lock-dependent activation test deselected), and isolated package smoke tests passed for both module and console entry points.
<!-- SECTION:NOTES:END -->
