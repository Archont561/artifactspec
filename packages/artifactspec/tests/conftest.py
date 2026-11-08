import csv
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
        manifest = manifest or {
            "schema_version": 3,
            "id": plugin_id,
            "version": "1.0",
            "outputs": ["pdf", "svg"],
            "output_syntax": {"pdf": "Output pdf.", "svg": "Output svg."},
            "phrases": [
                {
                    "name": "draw",
                    "outputs": ["svg"],
                    "object_type": "draw",
                    "syntax": "Draw {name}.",
                }
            ],
            "properties": [],
            "representations": [],
            "renderers": [],
        }
        if module_source is None:
            declarations = {
                "phrases": ("Phrase", ("name", "object_type", "syntax", "outputs")),
                "properties": (
                    "Property",
                    ("name", "target_types", "syntax", "outputs"),
                ),
                "representations": (
                    "Representation",
                    ("name", "target_types", "outputs"),
                ),
                "renderers": ("Renderer", ("name", "outputs")),
            }
            arguments = []
            for kind, (cls, fields) in declarations.items():
                values = [
                    f"{cls}({', '.join(repr(item[field]) for field in fields)})"
                    for item in manifest[kind]
                ]
                arguments.append(f"{kind}=[{', '.join(values)}]")
            source = (
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
                "from artifactspec.plugin import Plugin, Phrase, Property, Representation, Renderer\n"
                f"plugin = Plugin({manifest['id']!r}, outputs={manifest['output_syntax']!r}, {', '.join(arguments)})\n"
            )
        else:
            source = module_source
        (package / "__init__.py").write_text(source, encoding="utf-8")
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
            "info": info,
        }

    return make_plugin
