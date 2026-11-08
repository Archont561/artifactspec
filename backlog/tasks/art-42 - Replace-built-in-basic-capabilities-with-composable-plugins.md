---
id: ART-42
title: Replace built-in basic capabilities with composable plugins
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 19:03'
updated_date: '2026-11-08 20:38'
labels: []
milestone: m-10
dependencies:
  - ART-41
priority: high
type: feature
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user requires no built-in basic content capabilities: SVG-specific text and shapes belong to the SVG plugin, events to a separate installable plugin, and both must compose in a single output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove built-in basic capabilities and CLI options; SVG and event distributions provide their own decorated syntax and handlers with matching static metadata.
- [x] #2 SVG and event contributions compose in a single document and render through SVG without a core-owned basic plugin; conflict and unsupported cases are explicit.
- [x] #3 Update docs, packaging, CI and isolated installation tests; retain metadata-only discovery, validation and LSP and render-time plugin autoload with opt-out.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write BDD/integration tests for mixed SVG and event content, plugin isolation, decorated registrations and no built-in capabilities. 2. Extract event contributions into an independent distribution and move image contributions to SVG. 3. Implement composable representation dispatch so separate plugins contribute visuals to one composition without SVG knowing event semantics. 4. Remove built-in flags, update docs, build and CI; verify isolated wheels and all quality gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed the built-in basic plugin and flags. The independent SVG distribution owns image shapes, diagram layout and decorated SVG renderer; the independently installable events distribution owns event statements and diagram layout. Representation dispatch composes both by semantic type and fails explicitly for conflicts and unsupported cases. Updated static manifests, packaging, CI, documentation and tests. Full suite: 365 passed with 96.67% coverage; Python 3.11 targeted: 44 passed; four-distribution wheel/sdist build and isolated core-only, events-only, SVG-only and mixed-render smoke checks passed. Discovery/validation/LSP and render autoload/opt-out are covered. Remote CI remains unverified until authorized push.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced built-in content with independent decorated SVG and event plugins and composable per-type representations; verified mixed SVG output, isolation, metadata-only paths and all local gates.
<!-- SECTION:FINAL_SUMMARY:END -->
