---
id: ART-47
title: Implement plugin-owned statements and context-bound contribution objects
status: To Do
assignee: []
created_date: '2026-11-08 22:20'
updated_date: '2026-11-08 22:20'
labels: []
milestone: m-12
dependencies:
  - ART-46
priority: high
type: feature
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the current split between typed declarations and decorated handlers after the new contract is reviewed. The core currently reduces source statements to creation and property-assignment categories, preventing plugins from defining other semantics as first-class statements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Plugins compose class-based statement, property, representation and renderer contributions with overridable behavior and no separate name-based decorator registration; contexts are available as invocation-bound object properties and isolated across concurrent and nested calls.
- [ ] #2 The core discovers selected trusted plugin objects, registers plugin-owned output and statement syntax, and parses, validates and dispatches them without hard-coded create or set sentence forms or creation and assignment as the only statement kinds.
- [ ] #3 Reusable typed property components compose within statements; the approved binding and execution semantics, source spans, type and reference checks, conflicts and deterministic diagnostics are covered by BDD and generated tests.
- [ ] #4 Capability metadata remains serializable, versions derive from installed distribution metadata, and CLI and LSP validation do not execute handlers; plugin import trust, autoload opt-out and explicit selection remain intact.
<!-- AC:END -->
