"""Unit tests for the distribution verification script without network access."""

import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "check_packages.py"
spec = importlib.util.spec_from_file_location("check_packages", SCRIPT)
assert spec and spec.loader
check_packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_packages)


def fake_builds(monkeypatch, *, with_license):
    calls = []

    def run(*args):
        calls.append(args)
        if "build" not in args:
            return
        out = Path(args[args.index("--outdir") + 1])
        out.mkdir(parents=True, exist_ok=True)
        package = Path(args[args.index("build") + 1]).name.replace("-", "_")
        wheel = out / f"{package}-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            if with_license:
                archive.writestr(f"{package}-0.1.0.dist-info/licenses/LICENSE", "MIT")
        (out / f"{package}-0.1.0.tar.gz").touch()

    monkeypatch.setattr(check_packages, "run", run)
    return calls


def test_check_packages_validates_and_smoke_installs_both_wheels(monkeypatch):
    calls = fake_builds(monkeypatch, with_license=True)
    check_packages.main()
    assert sum("build" in call for call in calls) == 2
    assert any("twine" in call and "check" in call for call in calls)
    assert any("--no-deps" in call for call in calls)
    assert any("-I" in call and "-c" in call for call in calls)
    assert any(
        any(
            "from artifactspec.parser import parse" in arg
            and "Set label of sun" in arg
            and "from artifactspec.validation import validate" in arg
            and "from artifactspec.lsp import create_server" in arg
            for arg in call
        )
        for call in calls
    )
    assert any(
        "-I" in call and "artifactspec" in call and "capabilities" in call
        for call in calls
    )
    assert any(
        Path(call[0]).name in {"artifactspec", "artifactspec.exe"}
        and "capabilities" in call
        for call in calls
    )
    for command in ("capabilities", "validate", "lsp"):
        assert any(
            "-I" in call and command in call and "--help" in call for call in calls
        )
        assert any(
            Path(call[0]).name in {"artifactspec", "artifactspec.exe"}
            and command in call
            and "--help" in call
            for call in calls
        )


def test_check_packages_rejects_a_missing_wheel_license(monkeypatch):
    fake_builds(monkeypatch, with_license=False)
    with pytest.raises(RuntimeError, match="License missing"):
        check_packages.main()
