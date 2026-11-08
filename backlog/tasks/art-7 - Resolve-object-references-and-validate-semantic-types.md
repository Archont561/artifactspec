---
id: ART-7
title: Resolve object references and validate semantic types
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 15:34'
labels: []
milestone: m-2
dependencies:
  - ART-6
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Syntax alone cannot establish whether objects exist or properties and phrases are meaningful in the chosen output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Named references and “it” resolve according to the documented scope rules.
- [x] #2 Missing, ambiguous, wrong-type, and unsupported-output references produce actionable source-linked diagnostics.
- [x] #3 Package-local tests cover reference scope boundaries and both valid and invalid inputs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Introduce opt-in v2 static plugin metadata: a phrase declares its created object type, and a property declares its accepted target types; retain v1 manifests and report an explicit warning when type checking is impossible.
2. Add BDD and unit tests before implementing document-scoped named and it reference resolution, duplicate and type diagnostics, and validation without loading plugin handlers.
3. Verify shared validation and metadata compatibility, then document limitations before moving to CLI and LSP tasks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation is awaiting approval of the semantic type metadata and backward-compatibility policy: v1 manifests declare capability names and outputs but not object or property target types.

User approved typed static metadata and explicit warnings for legacy v1 plugins. Type matching will be exact for the initial subset; strings remain the only supported values.

Implemented version 2 metadata with exact object and target types, v1 warnings, static manifest catalogs, two-pass reference resolution and source-linked diagnostics. Package-local BDD and unit tests passed, including installed v2 metadata with no plugin import. Syntax currently stops at its first error; independent semantic errors are accumulated.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented shared reference and exact type validation with legacy metadata warnings, verified by BDD, unit and static-discovery tests.
<!-- SECTION:FINAL_SUMMARY:END -->
