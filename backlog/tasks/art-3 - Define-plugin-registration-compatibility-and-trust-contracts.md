---
id: ART-3
title: 'Define plugin registration, compatibility, and trust contracts'
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 02:47'
updated_date: '2026-11-08 14:07'
labels: []
milestone: m-0
dependencies: []
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: high
type: spike
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Plugins are executable Python and need predictable extension boundaries without exposing private core types.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Specify plugin identity, version/capability metadata, registration lifecycle, conflict behavior, and output compatibility.
- [x] #2 Document decorator-based contribution points and phase-specific context protocols with illustrative examples.
- [x] #3 Document the trust boundary and approval requirements, including whether metadata discovery executes plugin code.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define the plugin identity, capabilities, conflict and compatibility rules.
2. Decide how installed plugin discovery handles executable Python and user approval.
3. Document the contract and phase-context boundaries before implementation.

4. Use static per-entry-point manifests for installed capability discovery; importing a plugin requires a separate explicit trust decision.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Documented identity, registration lifecycle, output compatibility, static manifest format, phase-context examples and executable-code trust boundary in docs/plugins.md. Static metadata discovery was selected by the user; loading remains explicit and trusted.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Specified the initial plugin contract, including user-approved static discovery and the separate executable-code trust boundary. Verified against the implemented registration and installed-wheel discovery tests.
<!-- SECTION:FINAL_SUMMARY:END -->
