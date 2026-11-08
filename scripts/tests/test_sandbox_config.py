"""Guard the explicitly limited, wheel-only published sandbox."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_published_bundle_matches_workflow_and_uses_wheels():
    config = tomllib.loads((ROOT / "pixi-sandbox.toml").read_text())
    bundles = {bundle["name"]: bundle for bundle in config["bundle"]}
    assert config["cargo_vendor"] is False
    assert bundles["gherkin"]["environments"] == ["gherkin"]
    assert bundles["gherkin"]["platforms"] == ["linux-64"]

    workflow = (ROOT / ".github/workflows/pixi-sandbox.yml").read_text()
    assert "--envs gherkin" in workflow
    assert "--branch sandbox/gherkin-linux-64" in workflow
    assert "--cargo-vendor false" in workflow

    # Pixi v7 lock lists each environment's platform selections before the
    # top-level package metadata. Refuse to publish a path or sdist as a wheel.
    lock = (ROOT / "pixi.lock").read_text()
    section = re.search(r"(?ms)^  gherkin:\n(.*?)(?=^  [^ ]+:\n|^packages:\n)", lock)
    assert section is not None
    assert "      linux-64:" in section.group(1)
    locations = re.findall(r"^      - pypi: (.+)$", section.group(1), re.MULTILINE)
    assert locations
    assert all(location.endswith(".whl") for location in locations)
