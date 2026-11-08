---
id: ART-36
title: Align LSP diagnostic positions with parser line boundaries
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 16:08'
updated_date: '2026-11-08 16:38'
labels: []
dependencies: []
priority: medium
type: task
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Hypothesis testing exposed a position mismatch: the parser splits only on newline, while pygls TextDocument splits additional Unicode line-separator characters such as U+0085 occurring inside valid JSON string values. A diagnostic on a later physical line can therefore be converted against the wrong text and reported at an incorrect column.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add a regression scenario for a valid string containing U+0085 followed by a diagnostic on a subsequent line, covering UTF-16 positions.
- [x] #2 Keep LSP document position conversion and changes consistent with the controlled-language line boundaries and negotiated position encoding.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write failing end-to-end BDD and generated tests for Unicode separators, incremental edits and negotiated encodings.
2. Align the server document model and diagnostic position conversion with the parser line boundaries while preserving full/incremental synchronization.
3. Verify and document the line behavior, run tests and quality checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Parser and LSP documents now share LF, CRLF and CR boundaries without treating Unicode separators within JSON strings as new lines. The workspace document preserves negotiated codecs for UTF-8/16/32 and applies incremental edits with the same line model. Added a failing BDD regression first, nine end-to-end encoding/newline cases, and generated line and position properties. Full locked coverage: 206 passed, 97.11%; Ruff, mypy, Gherkin, alint, actionlint and diff checks passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed diagnostic positions and incremental edits across Unicode separators, line endings and negotiated encodings; verified with BDD and property tests.
<!-- SECTION:FINAL_SUMMARY:END -->
