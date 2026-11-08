"""Plugin objects are the source of discoverable capabilities."""

from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(
        Path(__file__).resolve().parents[1]
        / "features"
        / "plugin_object_discovery.feature"
    )
)


@pytest.fixture
def state():
    return {}


@given("an installed plugin declared as a Python object")
def installed(state, tmp_path, monkeypatch):
    package = tmp_path / "sample_plugin"
    package.mkdir()
    marker = tmp_path / "imported"
    (package / "__init__.py").write_text(
        f"""from pathlib import Path
Path({str(marker)!r}).write_text("imported")
from artifactspec.plugin import Plugin, Phrase
plugin = Plugin("sample", outputs={{"image": "Picture."}}, phrases=[Phrase("shape", "shape", "Draw {{name}}.")])
@plugin.phrase("shape")
def shape(ctx): ctx.create("shape")
""",
        encoding="utf-8",
    )
    info = tmp_path / "sample_plugin-2.4.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: sample-plugin\nVersion: 2.4\n", encoding="utf-8"
    )
    (info / "entry_points.txt").write_text(
        "[artifactspec.plugins]\nsample = sample_plugin:plugin\n", encoding="utf-8"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    state["marker"] = marker


@when("I discover its capabilities")
def discover(state):
    from artifactspec.plugin import Registry

    registry = Registry()
    registry.load_installed("sample")
    state["plugin"] = registry.plugin("sample")


@then("its Python module is imported and its distribution version is reported")
def imported(state):
    assert state["marker"].exists()
    data = state["plugin"].to_dict()
    assert data["version"] == "2.4"
    assert data["phrases"][0]["syntax"] == "Draw {name}."
