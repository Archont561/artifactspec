---
id: decision-6
title: Keep renderers optional and validate a Manim vertical slice
date: '2026-11-07'
status: accepted
---

## Context

Fast video output is an initial goal, but the core should not require heavyweight native renderers.

## Decision

Keep renderers optional and discoverable separately. Use an `artifactspec-manim` package as a small vertical slice, discovered through a Python entry point, to test renderer handling and produce a short text video.

## Consequences

The existing slice renders and decodes a real MP4 in tests. It is not the artifact DSL, general plugin API, narration or synchronization. Native Manim and FFmpeg dependencies are installed in the optional Pixi Manim environment.
