"""Exercise discovery against a real wheel, not just fabricated metadata."""

import json
import os
import subprocess
import sys


def test_installed_wheel_manifest_is_discovered_without_importing(tmp_path):
    project = tmp_path / "project"
    package = project / "wheel_plugin"
    (package / "artifactspec_plugins").mkdir(parents=True)
    marker = tmp_path / "executed"
    (package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 1,
        "id": "wheel-example",
        "version": "2",
        "outputs": ["svg"],
        "phrases": [],
        "properties": [],
        "representations": [],
        "renderers": [{"name": "wheel-svg", "outputs": ["svg"]}],
    }
    (package / "artifactspec_plugins" / "wheel-example.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (project / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '[project]\nname = "wheel-plugin"\nversion = "2"\n'
        '[project.entry-points."artifactspec.plugins"]\nwheel-example = "wheel_plugin:plugin"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["wheel_plugin"]\n',
        encoding="utf-8",
    )
    target = tmp_path / "target"
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-build-isolation",
            "--target",
            str(target),
            str(project),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert install.returncode == 0, install.stderr
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(target), env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-m", "artifactspec", "capabilities", "--details"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    plugin = next(
        item
        for item in json.loads(result.stdout)["plugins"]
        if item["id"] == "wheel-example"
    )
    assert plugin["id"] == "wheel-example"
    assert plugin["capabilities"]["renderers"] == manifest["renderers"]
    assert not marker.exists()
