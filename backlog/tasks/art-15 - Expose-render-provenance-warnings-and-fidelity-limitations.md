---
id: ART-15
title: 'Expose render provenance, warnings, and fidelity limitations'
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 17:58'
labels: []
milestone: m-4
dependencies:
  - ART-14
  - ART-13
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents need to know which rendering choices were made and whether a result was degraded or requires review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Render results identify selected backend and representation and expose warnings and fallback decisions.
- [x] #2 Where source links exist, results expose inspectable provenance; unavailable provenance is reported honestly.
- [x] #3 Tests cover full-fidelity, fallback or unsupported-feature, and error cases with machine-readable results.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define an additive provenance status scoped to composition elements and document that it is not artifact-level mapping. 2. Preserve the existing default CLI behavior; add an opt-in JSON format for structured post-argument-parsing failures, preserving exit codes and diagnostics. 3. Write BDD and generated or parametrized tests first for available, partial, unavailable and empty composition provenance; successful lossless examples, reported limitations, unsupported features and errors. 4. Implement and document the contract without inferring visual fidelity or automatic fallback; verify all acceptance criteria and quality gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The result reports available, partial, unavailable, or no-elements source links for composition elements only, not artifact-byte provenance. Opt-in JSON mode returns structured success and post-argument-parsing failures with phase codes, diagnostics, accumulated warnings and known limitations; no automatic fallback is supported. Default error output remains text. No reported limitations is not a fidelity guarantee. BDD and generated tests cover source-link states, an exact synthetic SVG example, limitations, unsupported capability and phase failures, warning propagation, and preservation of existing output. Full suite: 307 passed, 96.82% coverage; Python 3.11 targeted suite: 33 passed; isolated installed-package JSON success/failure and package checks passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added composition-scoped provenance availability and opt-in machine-readable failure results while preserving default CLI error behavior. Verified with BDD, property and integration tests, an exact synthetic SVG case, full coverage and installed-package smoke tests.
<!-- SECTION:FINAL_SUMMARY:END -->
