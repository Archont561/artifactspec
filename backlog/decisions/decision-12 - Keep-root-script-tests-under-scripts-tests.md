---
id: decision-12
title: Keep root script tests under scripts/tests
date: '2026-11-08 02:59'
status: accepted
---

## Context

Repository maintenance scripts are not product-package functionality; their tests should follow the scripts rather than live in a package.

## Decision

Keep repository scripts under root `scripts/` and their tests and script-specific Gherkin features under `scripts/tests/`. Product tests and features remain package-local. This supersedes the root-test prohibition in decision-7 only for repository scripts.

## Consequences

Run script tests via `pixi run test-scripts` and include them in full CI. Changes under `scripts/` take the scripts-only scope; package paths conservatively take full CI. Lint both package and script Gherkin features.
