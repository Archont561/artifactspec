---
id: decision-3
title: Separate semantic content from output-specific representation
date: '2026-11-07'
status: accepted
---

## Context

The same semantic content can support different artifacts and visual forms; animation playback timing is not the same as a content timeline.

## Decision

Separate semantic content, representation, composition and rendering. Support distinct output-aware formats such as `.report`, `.presentation`, `.animation` and `.image`; shared `.content` remains a possibility. Plugins should be able to contribute output-appropriate representations and commands.

## Consequences

A timeline content plugin might yield a diagram for an image, a linked list or diagram for a report, or animated visuals for an animation. Playback timelines belong to animation composition. Typst is a desired backend for editable `.typ` and PDF output. These layers and backends remain design goals, not implemented APIs.
