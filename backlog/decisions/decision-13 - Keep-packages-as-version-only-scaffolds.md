---
id: decision-13
title: Keep packages as version-only scaffolds
date: '2026-11-08 03:05'
status: accepted
---

## Context

The user requested a deliberately minimal starting point and approved removal of the previous CLI and Manim prototype.

## Decision

Each package contains only its VERSION initializer as product source, together with packaging metadata and a package-local BDD version feature and test. Each `pyproject.toml` declares the version; `VERSION` reads installed distribution metadata. This supersedes the implementation-status claims in decisions 1, 6 and 8, without changing the longer-term architectural goals.

## Consequences

No CLI, renderer or Manim dependency is implemented. Version changes require reinstalling or rebuilding the distribution. The BDD tests compare pyproject, installed metadata and exported VERSION, and verify the minimal source layout.
