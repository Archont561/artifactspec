---
id: decision-7
title: Keep features and tests package-local
date: '2026-11-07'
status: accepted
---

## Context

Tests and behavior specifications need clear ownership in a repository that may contain several packages.

## Decision

Keep tests and Gherkin feature files within their owning package; do not add root-level tests. Keep `examples/` empty until the public API is stable. Maintain both `pixi.toml` and `pixi-sandbox.toml`.

## Consequences

CI and local tasks must point at package-local test paths. The sandbox manifest is an initial policy, not proof that sandbox automation is implemented.
