---
id: ART-35
title: Add property-based coverage for standalone functions
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 16:03'
updated_date: '2026-11-08 16:08'
labels: []
dependencies: []
priority: high
type: task
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user requested Hypothesis for non-BDD tests and a lasting AGENTS.md rule requiring meaningful property cases for standalone functions using Hypothesis or pytest parametrization when possible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Hypothesis is available to Pixi and package development/CI test environments, with the lockfile updated by the relock bot.
- [x] #2 Non-BDD tests are audited and meaningful property-based coverage is added for standalone functions without weakening existing integration and regression tests.
- [x] #3 AGENTS.md records the requested testing rule and tests and quality checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add Hypothesis through Pixi and package test dependencies; document and preserve the relock requirement.
2. Audit standalone functions and add meaningful Hypothesis or parametrized property cases where possible, preserving existing BDD and integration tests.
3. Update AGENTS.md, review the changes and run relevant tests; report coverage gaps and pending lock repair.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hypothesis was added with pixi add --pypi --no-install --frozen after the normal command failed on conda-forge TLS. Lock repair must be done by the relock bot on a separately authorized PR. Added Hypothesis to the package dev extra for the Python matrix, plus the AGENTS.md property testing rule. Added generated properties for parsing, validation, metadata, capability and command discovery, LSP positions, CI scope/range selection and activation path handling; fixed integration and regression cases remain intact by user decision. Side-effectful script and CLI entry points remain covered by their existing fixed integration tests; parser internals are covered via public parse/validate properties. Unicode line-separator conversion issue found by generation is tracked separately. Verified 183 passed (one locked activation test deselected pending relock), 97.98% coverage, Python 3.11 core 114 passed, package builds and quality checks passed.
<!-- SECTION:NOTES:END -->
