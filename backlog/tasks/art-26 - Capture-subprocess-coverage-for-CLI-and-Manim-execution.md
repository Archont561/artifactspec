---
id: ART-26
title: Capture subprocess coverage for CLI and Manim execution
status: Done
assignee: []
created_date: '2026-11-08 02:48'
updated_date: '2026-11-08 02:58'
labels: []
dependencies: []
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
priority: medium
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Current coverage excludes much of the subprocess-executed CLI and Manim scene, making the reported percentage misleading.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Coverage configuration collects supported subprocess execution in the combined test environment.
- [x] #2 The combined coverage report includes exercised CLI and renderer subprocess lines without double-counting or leaking test artifacts.
- [x] #3 Tests or documented reproducible checks demonstrate collection and clarify any remaining gaps.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Configure coverage subprocess collection, verify exercised CLI and Manim lines in the combined report, and document any remaining gaps.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Enabled coverage.py subprocess patching and source-path collection. Combined 20-test suite passed; CLI, renderer and Manim scene lines appear in the report (83% overall). Native code and FFmpeg remain outside Python coverage.
<!-- SECTION:FINAL_SUMMARY:END -->
