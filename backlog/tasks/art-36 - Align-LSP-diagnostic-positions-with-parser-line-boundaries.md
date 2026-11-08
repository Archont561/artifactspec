---
id: ART-36
title: Align LSP diagnostic positions with parser line boundaries
status: To Do
assignee: []
created_date: '2026-11-08 16:08'
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
- [ ] #1 Add a regression scenario for a valid string containing U+0085 followed by a diagnostic on a subsequent line, covering UTF-16 positions.
- [ ] #2 Keep LSP document position conversion and changes consistent with the controlled-language line boundaries and negotiated position encoding.
<!-- AC:END -->
