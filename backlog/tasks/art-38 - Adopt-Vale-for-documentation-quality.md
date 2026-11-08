---
id: ART-38
title: Adopt Vale for documentation quality
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 17:00'
updated_date: '2026-11-08 17:06'
labels: []
dependencies: []
priority: medium
type: task
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repository checks structure with alint but lacks a consistent prose-quality gate for documentation and backlog. Introduce Vale without conflating these responsibilities or weakening scoped CI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A reproducible Vale installation and versioned style configuration checks project documentation and backlog prose, with clear scope and project terminology.
- [ ] #2 Documentation-only and full CI run the Vale gate, and agent and contributor instructions describe Vale and alint responsibilities.
- [x] #3 Tests verify real Vale findings, code-block handling, and CI integration; existing scoped checks and repository lint continue to pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Select reproducible Vale and style installation compatible with locked Pixi and the sandbox. 2. Establish BDD coverage and a practical scoped rule baseline for existing prose. 3. Integrate the check into scoped CI and document local usage; verify behavior and quality gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Vale 3.26.0 is pinned through a Bun-locked Linux x86-64 binary package; selected Microsoft and write-good rules and licenses are vendored at pinned commits. The global gate checks spelling, repetition, terminology, and spacing; write-good warnings apply to docs only. Errors fail; warnings are advisory. BDD and parametrized tests exercise real Vale, including Markdown code blocks, spelling, terminology, spacing, and backlog scope; a static test verifies CI wiring. Local full coverage: 264 passed, 96.56%; package, prose, alint, Ruff, mypy, feature lint, actionlint, and diff checks passed. CI jobs are configured but have not run remotely for this change, so AC 2 remains open pending remote verification.
<!-- SECTION:NOTES:END -->
