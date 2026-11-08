---
id: decision-8
title: Expose only VERSION from package initializers
date: '2026-11-07'
status: accepted
---

## Context

The package root should remain minimal and have a predictable version constant.

## Decision

Each package initializer explicitly exports only the `VERSION` constant via `__all__`. Each package has a local BDD test checking the fresh root namespace and that `VERSION` matches its installed distribution version.

## Consequences

Public functions live in submodules; the Manim entry point targets `artifactspec_manim.renderer:render_text`. Python can add submodule attributes to a package namespace after submodules are imported. The version constant and package metadata must be kept in sync.
