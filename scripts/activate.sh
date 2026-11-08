#!/bin/sh
# Pixi sources this file when activating the default feature.
# Absolute paths keep imports correct even when invoked from a subdirectory.
export PYTHONPATH="${PIXI_PROJECT_ROOT}/packages/artifactspec/src:${PIXI_PROJECT_ROOT}/packages/artifactspec-manim/src${PYTHONPATH:+:${PYTHONPATH}}"
