"""Check both feature locations with strict handling of gherlint findings."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "check_gherkin.py"
spec = importlib.util.spec_from_file_location("check_gherkin", SCRIPT)
assert spec and spec.loader
check_gherkin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_gherkin)


def test_lints_package_and_script_features(monkeypatch):
    paths = []

    def run(args, **kwargs):
        paths.append(args[-1])
        return SimpleNamespace(stdout="", stderr="", returncode=0)

    monkeypatch.setattr(check_gherkin.subprocess, "run", run)
    assert check_gherkin.main() == 0
    assert paths == ["packages", "scripts/tests"]


def test_output_from_script_features_is_treated_as_failure(monkeypatch):
    def run(args, **kwargs):
        stdout = "feature error\n" if args[-1] == "scripts/tests" else ""
        return SimpleNamespace(stdout=stdout, stderr="", returncode=0)

    monkeypatch.setattr(check_gherkin.subprocess, "run", run)
    assert check_gherkin.main() == 1
