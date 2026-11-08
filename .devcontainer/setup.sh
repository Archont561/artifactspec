#!/usr/bin/env bash
# Online devcontainer bootstrap, following pixi-sandbox's setup pattern.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

case "${ARTIFACTSPEC_INSTALL_OPENCODE:-0}" in
  0|1) ;;
  *) echo 'ARTIFACTSPEC_INSTALL_OPENCODE must be 0 or 1.' >&2; exit 2 ;;
esac

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo 'ArtifactSpec requires a Linux x86-64 container (Pixi linux-64).' >&2
  exit 1
fi
if ! command -v pixi >/dev/null 2>&1; then
  echo 'Pixi is missing; use the configured Pixi devcontainer image.' >&2
  exit 1
fi

export PATH="${HOME}/.pixi/bin:${PATH}"
pixi --version

# The image may not contain these CLIs. Global tools are outside pixi.lock.
pixi global install --channel conda-forge git gh
pixi global install --channel https://prefix.dev/archont561/archont561 \
  --channel conda-forge 'pixi-sandbox=0.9.0'

# Materialize both locked environments and the separately locked Bun tooling.
pixi install --locked --all
pixi run --locked bun-install
pixi run --locked install-projects

# An optional developer tool, deliberately not a project dependency.
if [[ "${ARTIFACTSPEC_INSTALL_OPENCODE:-0}" == 1 ]]; then
  pixi run --locked -x bun add --global --exact opencode-ai@1.19.5
  echo 'OpenCode was installed; authentication and model refresh are manual.'
fi

echo 'ArtifactSpec devcontainer ready. Run: pixi run --locked test'
