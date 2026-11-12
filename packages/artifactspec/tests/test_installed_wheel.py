"""Exercise discovery against a real wheel, not just fabricated metadata."""

import json
import os
import subprocess
import sys


def _wheel_project(tmp_path):
    project = tmp_path / "project"
    package = project / "wheel_plugin"
    package.mkdir(parents=True)
    marker = tmp_path / "executed"
    (package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        "from artifactspec.plugin import Plugin, Renderer\n"
        "plugin = Plugin('wheel-example', outputs={'svg': 'Output svg.'}, renderers=(Renderer('wheel-svg', ('svg',)),))\n",
        encoding="utf-8",
    )
    (project / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '[project]\nname = "wheel-plugin"\nversion = "2"\n'
        '[project.entry-points."artifactspec.plugins"]\nwheel-example = "wheel_plugin:plugin"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["wheel_plugin"]\n',
        encoding="utf-8",
    )
    return project, marker


def test_installed_wheel_object_is_imported_with_distribution_version(tmp_path):
    project, marker = _wheel_project(tmp_path)
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
    assert plugin["renderers"] == [{"name": "wheel-svg", "outputs": ["svg"]}]
    assert plugin["version"] == "2"
    assert marker.exists()
