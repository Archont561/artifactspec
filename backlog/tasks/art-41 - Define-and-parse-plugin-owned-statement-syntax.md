---
id: ART-41
title: Define and parse plugin-owned statement syntax
status: Done
assignee:
  - '@arena-agent'
created_date: '2026-11-08 19:03'
updated_date: '2026-11-08 20:38'
labels: []
milestone: m-10
dependencies: []
priority: high
type: feature
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current core hard-codes Output, Create and Set forms, but the user requires all statement forms, including output selection, to be defined by plugins using declarative templates without executing plugin code for discovery, validation or LSP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Plugins provide full output, phrase and property statement templates in static metadata; core does not hard-code any such statement forms.
- [x] #2 Parsing and validation use only declarative metadata, preserve source-linked diagnostics and type/reference checks, and reject ambiguous or malformed templates and statements deterministically.
- [x] #3 Document the syntax and compatibility contract; BDD, generated and integration tests cover extensible syntax, conflicts, trust boundaries and errors.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write BDD and generated tests for plugin-defined output and content templates, metadata-only parsing, ambiguity, spans and validation. 2. Add a versioned static template contract and runtime declarations; replace hard-coded statement forms with safe template matching. 3. Preserve semantic validation and clear errors, document the migration and verify.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Schema 3 declares literal output templates and typed name, reference and JSON-string placeholders for phrase and property statements. The metadata-only parser rejects legacy v1/v2 manifests with an actionable migration message, reports ambiguity and source spans, and retains reference/type validation. The former core-owned grammar and Lark runtime dependency were removed. BDD, generated and integration tests cover syntax extensibility, malformed input, conflicts and non-execution of plugin modules. Verified in the full suite (365 passed, 96.67% coverage), Python 3.11 targeted suite (44 passed), and isolated wheel builds; lint, formatting, typing, Gherkin, prose and actionlint pass. GitHub CI remains to be verified after an authorized push.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented plugin-owned schema-v3 output and statement templates with metadata-only parsing and validation; documented required v1/v2 migration and verified BDD, generated, integration and package checks.
<!-- SECTION:FINAL_SUMMARY:END -->
