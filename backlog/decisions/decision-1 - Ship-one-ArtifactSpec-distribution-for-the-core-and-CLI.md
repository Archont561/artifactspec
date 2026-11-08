---
id: decision-1
title: Ship one ArtifactSpec distribution for the core and CLI
date: '2026-11-07'
status: accepted
---

## Context

The CLI and framework are one product. Splitting runtime and tools into separate distributions would complicate installation and the agent workflow.

## Decision

Publish the reusable core and its CLI together as the `artifactspec` Python distribution. Keep heavyweight renderers optional or separately distributed. The user installs the product and an agent can discover and use its capabilities.

## Consequences

Do not introduce a separate runtime/tools distribution split. The Manim integration is a separate renderer package. Packaging and discovery must continue to work when that renderer is absent.
