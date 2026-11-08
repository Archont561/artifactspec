---
id: decision-4
title: Describe animation as states over time
date: '2026-11-07'
status: accepted
---

## Context

Authors should describe the intended result at points in time without spelling out every imperative animation step.

## Decision

Favor declarative states at specified times, with the system interpolating between them, over imperative step-by-step animation instructions.

## Consequences

The eventual animation model needs explicit timing and interpolation semantics. Narration, including ElevenLabs, and synchronization to speech timing are desired later capabilities. The current text-video renderer does not implement this language, timing model or narration.
