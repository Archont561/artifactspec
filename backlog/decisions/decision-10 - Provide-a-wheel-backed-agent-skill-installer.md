---
id: decision-10
title: Provide a wheel-backed agent skill installer
date: '2026-11-07'
status: proposed
---

## Context

An installed agent skill should be discoverable without manually copying its contents from a Python wheel.

## Decision

Preferred approach: an `anim skill install` command checks for or creates `skills-lock.json`, adds an entry and links `.agents/skills/<name>` to the wheel-installed skill.

## Consequences

This remains proposed: verify the command name in the ArtifactSpec product, lockfile interoperability with the Skills CLI, cross-platform links and an appropriate copy fallback before finalizing. Existing copied repository skills and reconstructed provenance do not establish wheel or remote restore compatibility. No installer has been implemented.
