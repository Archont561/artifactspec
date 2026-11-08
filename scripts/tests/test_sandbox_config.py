"""Guard the published, wheel-only developer sandbox."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_published_bundle_matches_workflow_and_uses_wheels():
    config = tomllib.loads((ROOT / "pixi-sandbox.toml").read_text())
    bundles = {bundle["name"]: bundle for bundle in config["bundle"]}
    assert config["cargo_vendor"] is False
    assert bundles["developer"]["environments"] == ["default", "gherkin"]
    assert bundles["developer"]["platforms"] == ["linux-64"]

    workflow = (ROOT / ".github/workflows/pixi-sandbox.yml").read_text()
    assert "--envs default,gherkin" in workflow
    assert "--branch sandbox/developer-linux-64" in workflow
    assert "--cargo-vendor false" in workflow

    lock = (ROOT / "pixi.lock").read_text()
    for environment in ("default", "gherkin"):
        # Pixi v7 lists environment selections before top-level package metadata.
        section = re.search(
            rf"(?ms)^  {environment}:\n(.*?)(?=^  [^ ]+:\n|^packages:\n)", lock
        )
        assert section is not None
        assert "      linux-64:" in section.group(1)
        locations = re.findall(r"^      - pypi: (.+)$", section.group(1), re.MULTILINE)
        assert locations
        assert all(location.endswith(".whl") for location in locations)


def test_package_tests_install_local_projects_without_editable_lock_entries():
    manifest = tomllib.loads((ROOT / "pixi.toml").read_text())
    dependencies = manifest["pypi-dependencies"]
    assert "artifactspec" not in dependencies
    assert "artifactspec-manim" not in dependencies
    assert "hatchling" in dependencies
    tasks = manifest["tasks"]
    install = tasks["install-projects"]
    assert "--no-build-isolation" in install
    assert "--no-deps" in install
    for name in ("test", "test-manim", "coverage", "coverage-all"):
        assert "install-projects" in tasks[name]["depends-on"]
        assert "PYTHONPATH=" not in tasks[name]["cmd"]
    assert "scripts/activate.py" in manifest["activation"]["env"]["PYTHONPATH"]
