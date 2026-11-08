---
id: decision-2
title: Build an agent-friendly controlled artifact language
date: '2026-11-07'
status: accepted
---

## Context

Agents need to create and revise artifact specifications efficiently while avoiding invented or ambiguous commands.

## Decision

Design a concise, primarily declarative controlled-natural-language syntax, with predictable registered phrases and typed intermediate representation. Plugins may add phrases, nouns and verbs. Favor natural, Gherkin-like sentences over verbose programming syntax, `custom(...)` calls or nested object structures.

## Consequences

Agent workflows should discover capabilities, author and validate a specification, render, inspect results and report. Strict parsing and capability, reference and type checks should reject unsupported commands; they cannot alone verify factual or visual accuracy. `it` may refer to the latest defined object, but its scoping rules remain open. The language and agent workflow are not yet implemented.
