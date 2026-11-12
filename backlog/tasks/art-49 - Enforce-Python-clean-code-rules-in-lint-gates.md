---
id: ART-49
title: Enforce Python clean code rules in lint gates
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-12 19:08'
updated_date: '2026-11-12 19:22'
labels: []
dependencies: []
references:
  - 'https://github.com/Archont561/polyglot-clean-code'
priority: high
type: chore
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Rude and its clean code rules to the developer environment and enforce Python clean code in local hooks and CI, informed by the polyglot-clean-code project.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The locked developer environment includes rude and rude-clean-code with a documented, explicit Python clean code policy.
- [x] #2 Python clean code findings are addressed without changing intended behavior and relevant tests pass.
- [x] #3 The same clean code check fails for violations and runs in Git hooks and all CI paths that cover Python changes.
- [x] #4 Applicable rules from polyglot-clean-code are adopted with provenance and the selected scope is documented.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect Rude and upstream policy rules and select applicable Python checks. 2. Add and lock dependencies, configure rules, integrate hooks and scoped CI, and refactor findings without changing behavior. 3. Verify violation enforcement, repository tests and documentation checks; record any environment blockers.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The direct pixi add could not resolve the optional Manim environment because conda-forge is unreachable in this sandbox. Solved the default environment with Pixi, retained the existing Manim lock and added the same PyPI wheels to it, then verified the complete lock with pixi lock --check --offline. Optional Manim installation and remote CI remain unverified here. Enabled the deterministic Basic profile with documented thresholds, addressed its findings, and adapted selected Python, Alint and Vale rules from upstream commit 39497482cb634f63a4c49433c342d5073d7cabba.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added Rude and rude-clean-code to the locked environment and enforced warning-level clean code checks through the shared lint task, pre-commit and both Python CI scopes. Refactored findings and adopted documented upstream policy equivalents. Verified 423 tests at 97.19% coverage, package builds and wheel checks, lint and all forced pre-commit jobs; a synthetic CC308 violation failed the hook. Offline lock consistency passed; optional Manim installation and GitHub CI were not run.
<!-- SECTION:FINAL_SUMMARY:END -->
