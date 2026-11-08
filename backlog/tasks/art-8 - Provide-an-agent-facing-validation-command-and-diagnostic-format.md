---
id: ART-8
title: Provide an agent-facing validation command and diagnostic format
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 15:35'
labels: []
milestone: m-2
dependencies:
  - ART-6
  - ART-7
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents need to correct specifications incrementally without inferring validity from rendering failures.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A documented CLI validation interface returns a nonzero status for invalid input and a successful status for valid input.
- [x] #2 Human-readable and machine-readable diagnostics expose source location when available, severity, and actionable cause.
- [x] #3 Package-local tests cover valid input, multiple errors, unknown capabilities, and stable machine-readable output.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add BDD tests for human and versioned JSON diagnostics, valid input, multiple semantic errors and unknown capabilities without executing plugin code.
2. Expose the shared validator through the Typer CLI using installed static manifests only and documented exit codes.
3. Verify and document the CLI interface before implementing editor diagnostics.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Typer validate command backed by installed static manifests and shared validation, with text and versioned JSON, source spans, warning/error severities and distinct validation/operational exit statuses. BDD subprocess tests cover valid and multiple-error inputs without importing installed plugin code; unit tests cover unknown capabilities, text/JSON and IO failure. Syntax remains first-error; semantic checks accumulate diagnostics.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added and documented CLI validation, verified with package-local BDD and unit tests.
<!-- SECTION:FINAL_SUMMARY:END -->
