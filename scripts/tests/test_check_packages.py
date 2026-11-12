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


def fake_builds(monkeypatch, *, with_license, with_plugin_json=False):
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
            if with_plugin_json:
                archive.writestr(f"{package}/artifactspec_plugins/obsolete.json", "{}")
            if with_license:
                archive.writestr(f"{package}-0.1.0.dist-info/licenses/LICENSE", "MIT")
        (out / f"{package}-0.1.0.tar.gz").touch()

    def check_json(*args, **expectations):
        calls.append(args)
        assert expectations["status"] in {"success", "error"}

    monkeypatch.setattr(check_packages, "run", run)
    monkeypatch.setattr(check_packages, "check_json", check_json)
    return calls


def _assert_api_smoke(calls):
    assert any(
        any(
            all(
                text in arg
                for text in (
                    "from artifactspec.core.parser import parse",
                    "Set label of sun",
                    "from artifactspec.core.validation import validate",
                    "from artifactspec.editor.lsp import create_server",
                    "from artifactspec.cli.commands import capabilities",
                    "find_spec('artifactspec.commands') is None",
                )
            )
            for arg in call
        )
        for call in calls
    )


def _assert_command_help(calls):
    for command in ("capabilities", "validate", "lsp", "render"):
        assert any(
            "-I" in call and command in call and "--help" in call for call in calls
        )
        assert any(
            Path(call[0]).name in {"artifactspec", "artifactspec.exe"}
            and command in call
            and "--help" in call
            for call in calls
        )


def test_check_packages_validates_and_smoke_installs_all_wheels(monkeypatch):
    calls = fake_builds(monkeypatch, with_license=True)
    check_packages.main()
    assert sum("build" in call for call in calls) == 4
    assert any("twine" in call and "check" in call for call in calls)
    assert any("--no-deps" in call for call in calls)
    assert any("-I" in call and "-c" in call for call in calls)
    _assert_api_smoke(calls)
    assert any(
        "-I" in call and "artifactspec" in call and "capabilities" in call
        for call in calls
    )
    assert any(
        Path(call[0]).name in {"artifactspec", "artifactspec.exe"}
        and "capabilities" in call
        for call in calls
    )
    _assert_command_help(calls)
    assert any(
        "find_spec('artifactspec_svg') is None" in arg
        and "event_image.media_type" in arg
        for call in calls
        for arg in call
    )
    assert sum("render" in call and "--help" not in call for call in calls) == 7
    assert not any("--builtin-basic" in call for call in calls)
    assert sum("render" in call and "--format" in call for call in calls) == 4


def test_check_packages_rejects_a_missing_wheel_license(monkeypatch):
    fake_builds(monkeypatch, with_license=False)
    with pytest.raises(RuntimeError, match="License missing"):
        check_packages.main()


def test_check_packages_rejects_obsolete_plugin_json(monkeypatch):
    fake_builds(monkeypatch, with_license=True, with_plugin_json=True)
    with pytest.raises(RuntimeError, match="Obsolete plugin JSON"):
        check_packages.main()
