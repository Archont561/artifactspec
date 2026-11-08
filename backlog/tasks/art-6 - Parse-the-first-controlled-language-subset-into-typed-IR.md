---
id: ART-6
title: Parse the first controlled-language subset into typed IR
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 14:50'
labels: []
milestone: m-1
dependencies:
  - ART-1
  - ART-2
  - ART-4
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An agent needs predictable language processing before it can reliably validate or render an authored artifact.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A documented minimal output-aware subset parses into the agreed typed representation with source locations.
- [x] #2 Unknown or malformed phrases fail with source-linked diagnostics rather than being interpreted as arbitrary instructions.
- [x] #3 Package-local BDD tests cover valid, malformed, and ambiguous inputs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add failing package-local Gherkin scenarios for output-aware parsing, source spans, unknown and malformed phrases, ambiguity, and unresolved references.
2. Implement immutable syntax nodes and a strict line-oriented parser against the registered capability metadata without executing plugin code.
3. Exercise edge cases and cross-version behavior; run the complete quality and packaging checks and update documentation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The user approved the proposed Output/Create/Set grammar. ART-1 and ART-2 contracts are being developed and verified alongside this dependent implementation within the same milestone.

Implemented immutable source-linked nodes and registry/output-aware parsing without plugin handler execution. BDD covers valid, malformed, unknown, unavailable and ambiguous output cases; tests cover escaped strings, positions, references and statement-boundary attacks. Locked coverage-all: 119 passed, 99.11% package coverage on Linux Python 3.13; core suite: 63 passed on Linux Python 3.11. Isolated wheel parse smoke and lint, type, Gherkin and lock checks passed. Remote OS matrix not run.

Applied clean-code and behavior-preserving refactor review: extracted parser responsibilities and used spans to avoid redundant parameters. Afterward, locked coverage-all passed 122 tests with 99.14% package coverage; core Python 3.11 suite passed 63 tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the documented output-aware typed parser and source-linked diagnostics, with BDD and unit coverage and an isolated wheel smoke test. Reference resolution, validation and rendering remain future work.
<!-- SECTION:FINAL_SUMMARY:END -->
