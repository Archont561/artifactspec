---
id: ART-46
title: Design composable statement and class-based plugin contracts
status: In Progress
assignee:
  - '@arena-agent'
created_date: '2026-11-08 22:20'
updated_date: '2026-11-08 22:46'
labels: []
milestone: m-12
dependencies: []
references:
  - 'https://github.com/rude-dev/rude/blob/main/docs/guide/custom-rules.md'
  - 'https://github.com/rude-dev/rude/blob/main/docs/guide/plugin-development.md'
  - 'https://github.com/ManimCommunity/manim/blob/main/manim/scene/scene.py'
documentation:
  - backlog/docs/doc-1 - ArtifactSpec-product-and-architecture-specification.md
  - backlog/docs/doc-2 - Proposed-composable-plugin-and-statement-contract.md
priority: high
type: spike
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current plugin API separates typed declarations from name-based decorators and core still models only creation and property-assignment statements. The user wants plugins to define complete statements, compose reusable typed properties, override behavior on objects without decorators, and access invocation context as an object property. Manim and the Rude Python linter are suggested design inspirations. Obtain user review before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define a reviewed public contract for plugin-owned statements, output declarations, reusable typed property components, subclass overrides and contribution composition without separate name-based registration.
- [ ] #2 Specify declarative structured syntax, property binding and default behavior, name and reference resolution, diagnostics, ambiguity and semantic effects without requiring executable parsing hooks or core-owned statement wording.
- [ ] #3 Specify per-invocation context binding and concurrent or nested call isolation, plugin discovery and trust, metadata serialization, version ownership and migration from the existing API.
- [ ] #4 Compare relevant Manim authoring and Rude rule and plugin patterns, and document which ideas are adopted or rejected without imposing a Manim or Rude runtime dependency.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing parser, validation, pipeline, plugin registry and plugin examples, and compare relevant Manim and Rude patterns. 2. Draft a concrete class-based authoring and execution contract, including structured syntax, reusable properties, statement effects, contexts, provenance, metadata, selection and migration. 3. Check proposed examples against current behavior and edge cases, run documentation quality checks, and present the design and open decisions for user review before implementation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Drafted doc-2 after inspecting the current parser, validation, pipeline, registry, SVG and events plugins, and pinned Manim and Rude sources. The design is proposed and awaits user review; no implementation or acceptance criteria are complete.

User suggested typed Rectangle elements rather than plain strings. Added a proposed format-neutral Element base, separate provenance entries, and the open renderer interoperability decision to doc-2; implementation remains pending review.

User requested classes rather than strings for semantic type references. Updated the proposed syntax and target declarations to use Rectangle directly, and documented serializable type identities and separation between semantic nodes and visual instances.
<!-- SECTION:NOTES:END -->
