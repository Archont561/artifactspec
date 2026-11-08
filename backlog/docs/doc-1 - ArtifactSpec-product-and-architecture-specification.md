---
id: doc-1
title: ArtifactSpec product and architecture specification
type: specification
created_date: '2026-11-08 02:46'
updated_date: '2026-11-08 16:51'
tags:
  - specification
  - architecture
  - product
---
## Status and purpose

**Design specification, not an implementation claim.** This document captures the agreed direction and requirements for ArtifactSpec. Interface shapes, file grammar, release scope, and several semantics remain open. “Must” describes the intended product contract, not functionality that necessarily exists today. Historical decisions are recorded in `backlog/decisions/`; the first plugin milestone supersedes the core-only scaffold boundary in decision-13.

## 1. Product vision

ArtifactSpec is a Python-first, PyPI-installable framework and CLI for describing, producing, and reviewing visual artifacts. It is designed for an AI agent working on a user's behalf, while remaining usable by humans. The core and CLI ship together as one `artifactspec` distribution; heavyweight backends may be separate or optional.

An agent should be able to:

1. Discover installed artifact formats, plugins, phrases, properties, representations, and renderer capabilities through concise, actionable output.
2. Identify missing capabilities and, subject to user approval and trust policy, obtain and install appropriate plugins.
3. Author a compact specification, validate it iteratively, and correct actionable errors.
4. Preview or render the requested artifact using an appropriate backend.
5. Inspect results, including diagnostics, render provenance, fallbacks, and fidelity limitations; report outcomes and unresolved problems to the user.

Discovery and validation should be economical with tokens: offer concise summaries and progressive detail instead of requiring an agent to load all documentation at once. The first capability-discovery CLI and its versioned JSON schema are documented in `docs/plugins.md`.

## 2. Scope and artifact model

The framework targets output-aware formats such as `.report`, `.presentation`, `.animation`, and `.image`. Shared `.content` is a possibility, not a finalized format. The product should permit reuse of semantic content across outputs without pretending their layout and behavior are identical.

The intended conceptual pipeline is:

1. **Semantic content**: domain meaning and relationships, independent of a particular backend where practical.
2. **Representation**: a chosen way to express content for an output, including output-specific semantics and capabilities.
3. **Composition**: arrangement and, where applicable, timing of representations in the artifact.
4. **Rendering**: backend-specific production of an artifact and, where supported, editable source.

For example, timeline content could become a diagram in an image, a linked list or diagram in a report, or animated visuals in an animation. A content timeline describes domain events; an animation playback timeline schedules visual changes. They are distinct concepts.

Representation choice, backend limitations, and fallback behavior should be explicit and inspectable. A Typst backend is desired for editable `.typ` source and PDF; editable presentation output and fidelity reporting require backend-specific investigation, not an assumption that all visual elements remain editable.

## 3. Specification language

The language should be concise, controlled natural language: primarily declarative sentences with predictable, registered patterns. Plugins may contribute nouns, verbs, phrases, and output-specific commands. Avoid making users write verbose programming-like calls, `custom(...)` expressions, or deeply nested object structures as the primary authoring model.

Parsing produces typed intermediate representation rather than arbitrary executable instructions. Validation should reject unknown phrases, unsupported capabilities, invalid references and types, and unresolved ambiguity rather than silently guessing. The first subset resolves `it` as the most recently created object in the same document. Named references and declared object and property types are checked; missing type metadata produces a warning. See `docs/language.md`.

The authoring model may resemble Gherkin in readability, but is not required to be Gherkin syntax or compatible with Gherkin tooling. The initial `Output`, `Create`, and `Set` grammar is implemented as a source-linked parser; other proposed syntax is illustrative.

Semantic validation does **not** prove that content is factually correct or visually effective. Those concerns require separate checks and, where appropriate, human review.

## 4. Animation and audio

For animation, authors should describe desired states at given times and let the system interpolate, rather than writing a sequence of imperative animation steps. The eventual specification must define timing, interpolation, overlapping changes, and diagnostics precisely; these are not defined here.

A target workflow includes narration with ElevenLabs and synchronization between speech timing and animation. Provider integration, authentication, timing sources, audio formats, alignment behavior, failure recovery, and cost/consent handling remain to be designed. The framework should not claim synchronized narration until it is implemented and verified.

## 5. Plugin architecture

Plugins should be Python-first, explicit, and discoverable. The preferred authoring style is a `Plugin(...)` instance with decorators for contributed phrases, properties, representations, renderers, and related behavior. Plugins declare outputs and capabilities; the initial registration, conflict, and output-compatibility rules are documented in `docs/plugins.md`.

The core should expose phase-specific context **protocols** to plugin functions and inject its own concrete implementations. Plugins should not need to import private core objects such as internal property-assignment classes. A context records or requests operations appropriate to its phase rather than exposing renderer internals by default.

Provide an `artifactspec.testing` layer with fake contexts and helpers, and a pytest plugin with fixtures backed by those helpers. Test individual plugin behavior using fakes as well as end-to-end registration, parsing, validation, and rendering where applicable.

Plugins are trusted executable Python, not sandboxed by typing protocols. An agent must not treat an unapproved plugin as safe merely because it conforms to an interface. Installed discovery reads static manifests without importing plugin code; explicit trusted loading checks the runtime declaration against the manifest. Approval and broader dependency policy remain future work. Rust through PyO3 is an option only for measured performance bottlenecks.

## 6. Validation, diagnostics, and fidelity

A shared validation model and LSP are desired across output formats. Diagnostics should identify source locations when available, describe the problem and its cause, and offer actionable corrections or discoverable alternatives. Ambiguous or unavailable capabilities should be visible instead of silently coerced.

Render results should make it possible to inspect the selected representation and renderer, source-to-output provenance where feasible, warnings, approximations, and unsupported or degraded features. Behavior for unsupported requirements—error, explicit fallback, or user-approved degradation—must be designed and documented per capability.

Visual inspection, output decoding or parsing, and factual review complement—not replace—syntax and semantic validation. The validation CLI and LSP share reference and declared-type checks. The first static rendering slice exposes source provenance and limitations but does not verify visual fidelity or factual content.

## 7. Agent skills

The preferred future installer checks or creates `skills-lock.json`, records the skill, and links `.agents/skills/<name>` to the wheel-installed skill. The earlier proposed command name was `anim skill install`; whether that name fits the final ArtifactSpec CLI remains open.

Before committing to this interface, verify compatibility with the Skills CLI, lockfile behavior, directory links and agent discovery across platforms, wheel installation paths, safe updates/removal, and a copy fallback. Existing repository skill copies and their reconstructed source metadata do not prove wheel interoperability or remote restore/update support. No wheel-backed installer exists yet.

## 8. Packaging, repository, and quality

- The intended `artifactspec` product combines framework and CLI; a renderer such as `artifactspec-manim` may eventually be separate. The core now provides plugin registration and static capability discovery; the Manim distribution remains a version-only placeholder (the initial scaffold boundary is described in decision-13).
- Each package initializer explicitly exports only `VERSION`, sourced from installed distribution metadata generated from `pyproject.toml`. Package-local BDD tests check the fresh namespace, pyproject and installed metadata; the Manim package also checks its minimal source layout.
- Product tests and Gherkin features belong to their owning package. Repository scripts live in root `scripts/`, with their tests and script-specific features in `scripts/tests/` (decision-12 supersedes the root-test prohibition in decision-7 for scripts). Keep `examples/` empty until the API is stable.
- Maintain `pixi.toml` and `pixi-sandbox.toml`. The sandbox file is an initial policy, not evidence of operational sandbox automation.
- CI uses one change-detection script: docs/backlog-only changes get lightweight documentation checks, scripts-only changes run the scripts suite, mixed docs/scripts changes run both, and other or indeterminate changes run full checks. Commit messages are always linted. Full checks generate coverage and upload to Codecov where credentials are available; fork PR uploads are skipped. See `docs/ci.md` for operational details.
- Coverage includes the current package code. A passing test or coverage percentage is not a guarantee of visual correctness.

## 9. Current implementation boundary

The core implements a decorator-based plugin registry, static manifest discovery, an output-aware parser, reference and declared-type validation, CLI and LSP diagnostics, public phase contexts and test fakes, immutable semantic content, and explicit selection and atomic rendering through trusted plugins. The opt-in basic plugin renders text and rectangles to SVG; it can compose image and report forms but does not render reports. See `docs/plugins.md`, `docs/language.md`, and `docs/rendering.md` for contracts and limitations. The Manim package remains a version-only scaffold; animation, content-timeline semantics, narration, timing synchronization, and skill installation are not implemented. Version 1 plugin manifests lack type declarations and produce warnings.

## 10. Initial product acceptance goals

These goals describe future capability, not current completion:

1. A user installs the core product without mandatory heavyweight renderer dependencies; an agent can discover available output and plugin capabilities.
2. Given an installed, approved plugin and a valid specification, the agent can validate and render a supported artifact. An unknown phrase, unresolved reference, unsupported property, or ambiguous request yields a source-linked, actionable diagnostic rather than a silent guess.
3. The agent can inspect output and report renderer, warnings, fallback or fidelity limitations, and outstanding validation or review needs.
4. The same semantic content can be expressed through at least two suitable representations or outputs without making a content timeline equivalent to animation playback.
5. Plugin authors can test contributed behavior using public protocols, fake contexts, and testing helpers without importing private core classes.
6. An animation author can state desired visual states at specified times; interpolation and timing behavior follow documented rules. Narration synchronization is verified separately when implemented.

## 11. Open design questions

- Grammar beyond the first subset, richer phrase patterns, source file boundaries and imports.
- Richer semantic content types, content-timeline semantics, cross-output contracts, composition rules, and representation selection beyond the initial static slice.
- Core-version compatibility negotiation, plugin acquisition and approval policy.
- Deeper incremental validation, richer LSP features, and provenance granularity.
- Animation interpolation, time units, concurrency, narration alignment, and audio provider abstraction.
- Further CLI commands, schema evolution, and the workflow for obtaining plugins.
- Skill lockfile interoperability, symlinks versus copies, and lifecycle safety.
- Backend-specific editable output, fallback policies, visual verification, and implementation milestones.
