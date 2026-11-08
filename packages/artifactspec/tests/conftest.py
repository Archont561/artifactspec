import csv
import json
import sys

import pytest


@pytest.fixture
def installed_plugin_factory(tmp_path):
    def make_plugin(
        manifest=None,
        module_source=None,
        *,
        plugin_id="example",
        module="fixture_plugin",
    ):
        sys.modules.pop(module, None)
        path = tmp_path / "site"
        package = path / module
        package.mkdir(parents=True, exist_ok=True)
        marker = tmp_path / "executed"
        source = (
            module_source
            or f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        )
        (package / "__init__.py").write_text(source, encoding="utf-8")
        manifest = manifest or {
            "schema_version": 1,
            "id": plugin_id,
            "version": "1.0",
            "outputs": ["pdf", "svg"],
            "phrases": [{"name": "draw", "outputs": ["svg"]}],
            "properties": [],
            "representations": [],
            "renderers": [],
        }
        manifest_path = package / "artifactspec_plugins" / f"{plugin_id}.json"
        manifest_path.parent.mkdir(exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        info = path / f"{module}-1.0.dist-info"
        info.mkdir(exist_ok=True)
        (info / "METADATA").write_text(
            f"Metadata-Version: 2.1\nName: {module}\nVersion: 1.0\n", encoding="utf-8"
        )
        (info / "entry_points.txt").write_text(
            f"[artifactspec.plugins]\n{plugin_id} = {module}:plugin\n", encoding="utf-8"
        )
        with (info / "RECORD").open("w", newline="", encoding="utf-8") as record:
            csv.writer(record).writerows(
                [
                    [p.relative_to(path).as_posix(), "", ""]
                    for p in [
                        manifest_path,
                        package / "__init__.py",
                        info / "entry_points.txt",
                        info / "METADATA",
                    ]
                ]
            )
        return {
            "path": path,
            "marker": marker,
            "manifest": manifest,
            "manifest_path": manifest_path,
            "info": info,
        }

    return make_plugin
