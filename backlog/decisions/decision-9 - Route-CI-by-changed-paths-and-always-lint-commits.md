---
id: decision-9
title: Route CI by changed paths and always lint commits
date: '2026-11-07'
status: accepted
---

## Context

Documentation and script-only changes should not pay for the full renderer suite, while commits still need a consistent message policy.

## Decision

Use one change-detection script to set CI scope flags. Docs/backlog-only changes run lightweight documentation checks; scripts-only changes run the scripts suite; mixed docs and scripts run both. Other, empty or indeterminate diffs run full CI. Always lint commit messages.

## Consequences

Full CI generates coverage and uploads to Codecov, except fork PRs skip the upload; configure `CODECOV_TOKEN` where required. The stable CI result job can be used for branch protection after validating its behavior on GitHub. Coverage undercounts subprocess work; the workflow and upload have not yet been verified remotely.
