---
id: ART-33
title: Refactor the controlled-language parser to use Lark
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 15:18'
updated_date: '2026-11-08 15:20'
labels: []
dependencies:
  - ART-6
priority: high
type: task
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The first parser uses handwritten regular expressions despite Lark being a runtime dependency; the user requested that the parser use Lark without expanding the language.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Lark parses the documented Output, Create and Set grammar without executing plugin handlers.
- [x] #2 Existing public AST, source spans, diagnostics, capability restrictions and syntax behavior remain covered by regression tests.
- [x] #3 Package documentation and isolated packaging tests describe and verify the Lark-backed implementation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Capture existing grammar edge cases and diagnostics in regression tests.
2. Replace handwritten statement matching with a Lark grammar and map parse trees to existing immutable nodes.
3. Verify installed distributions, locked tests and quality checks; review the refactor.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Lark Earley grammar parses each stripped line, with explicit ambiguity handling and JSON validation; capability checks and source spans remain separate. Regression tests cover grammar keywords in capability names, escapes, whitespace, injection, Unicode columns and Lark invocation. Differential check against prior parser matched 4,080 generated inputs. Locked coverage-all: 133 passed, 99.71% coverage on Linux Python 3.13; Python 3.11 core: 74 passed in an isolated environment; installed wheel and sdist checks, Lark dependency install, Ruff, mypy, Gherkin, alint, actionlint and offline lock check passed. Refactor and clean-code skills reviewed; no outstanding findings in changed code. Cross-platform CI not run locally.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced handwritten statement matching with a Lark grammar while retaining the public parser API, source-linked syntax nodes, capability checks and diagnostic contract; verified packaging and regression tests.
<!-- SECTION:FINAL_SUMMARY:END -->
