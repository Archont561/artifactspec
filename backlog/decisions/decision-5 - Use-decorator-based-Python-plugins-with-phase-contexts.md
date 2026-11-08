---
id: decision-5
title: Use decorator-based Python plugins with phase contexts
date: '2026-11-07'
status: accepted
---

## Context

Plugins should be pleasant to author in Python and independently testable without depending on internal implementation classes.

## Decision

Prefer explicit `plugin = Plugin(...)` objects with decorators such as `@plugin.phrase`, `@plugin.property`, `@plugin.representation` and `@plugin.renderer`. Expose phase-specific context protocols and inject core implementations; provide testing helpers and pytest fixtures backed by those helpers.

## Consequences

Plugin authors should be able to use fake contexts to exercise behavior. Plugins are trusted executable Python; protocols do not sandbox them. Exact interfaces, registration semantics and implementation are not finalized. Rust via PyO3 is reserved for measured bottlenecks, not the default implementation.
