"""Build, validate, and smoke-test the distributions in an isolated environment."""

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


def check_json(*args: str, status: str, exit_code: int, error_code: str = "") -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        args, cwd=ROOT, env=env, capture_output=True, text=True, check=False
    )
    if result.returncode != exit_code:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {result.stderr}")
    data = json.loads(result.stdout)
    if data.get("schema_version") != 1 or data.get("status") != status:
        raise RuntimeError(f"Unexpected JSON response: {data}")
    if error_code and data.get("error", {}).get("code") != error_code:
        raise RuntimeError(f"Unexpected error code: {data}")


def _build_distributions(root: Path) -> list[Path]:
    outputs = root / "distributions"
    for package in (
        "artifactspec",
        "artifactspec-manim",
        "artifactspec-svg",
        "artifactspec-events",
    ):
        run(
            sys.executable,
            "-m",
            "build",
            str(ROOT / "packages" / package),
            "--outdir",
            str(outputs),
        )
    files = sorted(outputs.iterdir())
    if len(files) != 8:
        raise RuntimeError("Expected one wheel and one sdist per distribution")
    run(sys.executable, "-m", "twine", "check", *(str(path) for path in files))
    wheels = sorted(outputs.glob("*.whl"))
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            if any(
                "/artifactspec_plugins/" in name and name.endswith(".json")
                for name in archive.namelist()
            ):
                raise RuntimeError(f"Obsolete plugin JSON found in {wheel.name}")
            if not any(
                name.endswith(".dist-info/licenses/LICENSE")
                for name in archive.namelist()
            ):
                raise RuntimeError(f"License missing from {wheel.name}")
    return wheels


def _install_wheels(root: Path, wheels: list[Path]) -> tuple[Path, Path]:
    core = next(path for path in wheels if path.name.startswith("artifactspec-"))
    manim = next(path for path in wheels if path.name.startswith("artifactspec_manim-"))
    svg = next(path for path in wheels if path.name.startswith("artifactspec_svg-"))
    events = next(
        path for path in wheels if path.name.startswith("artifactspec_events-")
    )
    venv = root / "venv"
    run(sys.executable, "-m", "venv", str(venv))
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run(str(python), "-m", "pip", "install", str(core))
    run(
        str(python),
        "-I",
        "-c",
        "from artifactspec.plugins.discovery import installed_plugins; "
        "assert installed_plugins() == {}",
    )
    # These optional packages remain independent distributions.
    run(str(python), "-m", "pip", "install", "--no-deps", str(manim))
    run(str(python), "-m", "pip", "install", "--no-deps", str(events))
    run(
        str(python),
        "-I",
        "-c",
        "from artifactspec.plugins.discovery import installed_plugins; "
        "assert set(installed_plugins()) == {'events'}; "
        "from importlib.util import find_spec; "
        "assert find_spec('artifactspec_svg') is None; "
        "from artifactspec.plugins import Registry; "
        "from artifactspec.core.pipeline import build_content; "
        "from artifactspec.core.rendering import compose; "
        "registry = Registry(); registry.load_installed('events'); "
        'content = build_content(\'Output report.\\nCreate event named e.\\nSet date of e to "2000-01-01".\\nSet label of e to "milestone".\', registry); '
        "assert compose(content, output='report', representation='diagram', registry=registry).elements[0].value.text == '2000-01-01: milestone'; "
        "event_image = compose(content, output='image', representation='diagram', registry=registry).elements[0].value; "
        "assert event_image.media_type == 'image/svg+xml' and str(event_image).startswith('<text ') ",
    )
    run(str(python), "-m", "pip", "install", "--no-deps", str(svg))
    console = venv / (
        "Scripts/artifactspec.exe" if os.name == "nt" else "bin/artifactspec"
    )
    return python, console


def _check_entry_points(python: Path, console: Path) -> None:
    run(str(python), "-I", "-m", "artifactspec", "capabilities", "--details")
    run(str(console), "capabilities", "--details")
    # Both installed entry points must discover every built-in command module.
    for command in ("capabilities", "validate", "lsp", "render"):
        run(str(python), "-I", "-m", "artifactspec", command, "--help")
        run(str(console), command, "--help")


def _check_render_json(entry: tuple[str, ...], source: Path, destination: Path) -> None:
    check_json(
        *entry,
        "render",
        str(source),
        "--representation",
        "diagram",
        "--renderer",
        "svg",
        "--output",
        str(destination),
        "--format",
        "json",
        status="success",
        exit_code=0,
    )
    bad_source = source.parent / "bad.art"
    bad_source.write_text("Output image.\nCreate nonsense.", encoding="utf-8")
    check_json(
        *entry,
        "render",
        str(bad_source),
        "--representation",
        "diagram",
        "--renderer",
        "svg",
        "--output",
        str(destination),
        "--format",
        "json",
        status="error",
        exit_code=1,
        error_code="validation_failed",
    )


def _check_svg_only(root: Path, console: Path) -> None:
    svg_source = root / "svg-only.art"
    svg_source.write_text(
        'Output image.\nCreate text named title.\nSet value of title to "SVG only".',
        encoding="utf-8",
    )
    run(
        str(console),
        "render",
        str(svg_source),
        "--no-plugin-autoload",
        "--plugin",
        "svg",
        "--representation",
        "diagram",
        "--renderer",
        "svg",
        "--output",
        str(root / "svg-only.svg"),
    )


def _check_render(root: Path, python: Path, console: Path) -> None:
    _check_svg_only(root, console)
    source = root / "scene.art"
    source.write_text(
        'Output image.\nCreate text named title.\nSet value of title to "wheel smoke".\n'
        'Create event named launch.\nSet date of launch to "2000-01-01".\n'
        'Set label of launch to "milestone".',
        encoding="utf-8",
    )
    for index, entry in enumerate(
        ((str(python), "-I", "-m", "artifactspec"), (str(console),))
    ):
        destination = root / f"image-{index}.svg"
        run(
            *entry,
            "render",
            str(source),
            "--representation",
            "diagram",
            "--renderer",
            "svg",
            "--output",
            str(destination),
        )
        _check_render_json(entry, source, destination)
        run(
            str(python),
            "-I",
            "-c",
            "import sys, xml.etree.ElementTree as ET; "
            "texts = [element.text for element in ET.parse(sys.argv[1]).getroot().findall('{http://www.w3.org/2000/svg}text')]; "
            "assert texts == ['wheel smoke', '2000-01-01 — milestone']",
            str(destination),
        )


def _check_api(python: Path) -> None:
    run(
        str(python),
        "-I",
        "-c",
        "from importlib.metadata import version; "
        "from importlib.util import find_spec; "
        "import artifactspec, artifactspec_manim, artifactspec_svg, artifactspec_events; "
        "assert artifactspec.VERSION == version('artifactspec'); "
        "assert artifactspec_manim.VERSION == version('artifactspec-manim'); "
        "assert artifactspec_svg.VERSION == version('artifactspec-svg'); "
        "assert artifactspec_events.VERSION == version('artifactspec-events'); "
        "assert artifactspec.__all__ == ['VERSION']; "
        "assert artifactspec_manim.__all__ == ['VERSION']; "
        "assert artifactspec_svg.__all__ == ['VERSION']; "
        "assert artifactspec_events.__all__ == ['VERSION']; "
        "from artifactspec.cli.commands import capabilities, validate, lsp, render; "
        "assert find_spec('artifactspec.commands') is None; "
        "from artifactspec.cli import app, create_app; "
        "from artifactspec.testing import FakePhraseContext; "
        "from artifactspec.testing.contexts import FakePhraseContext as ContextImplementation; "
        "assert FakePhraseContext is ContextImplementation; "
        "from artifactspec.core.parser import parse; "
        "from artifactspec.plugin import Plugin, Registry, Phrase, Property; "
        "from artifactspec.plugins._registry import Plugin as PluginImplementation; "
        "assert Plugin is PluginImplementation; "
        "plugin = Plugin('example', outputs={'image': 'Output image.'}, phrases=(Phrase('circle', 'circle', 'Create circle named {name}.'),), properties=(Property('label', ('circle',), 'Set label of {reference} to {value}.'),)); "
        "plugin.phrase('circle')(lambda context: None); "
        "plugin.property('label')(lambda context: None); "
        "registry = Registry(); registry.register(plugin); "
        "document = parse('Output image.\\nCreate circle named sun.\\n"
        'Set label of sun to \\"hello\\".\', registry); '
        "assert document.statements[0].name == 'sun'; "
        "assert document.statements[1].value.value == 'hello'; "
        "from artifactspec.core.validation import validate; "
        "assert validate('Output image.', registry).valid; "
        "from artifactspec.editor.lsp import create_server; "
        "assert create_server(registry) is not None",
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="artifactspec-packages-") as directory:
        root = Path(directory)
        wheels = _build_distributions(root)
        python, console = _install_wheels(root, wheels)
        _check_entry_points(python, console)
        _check_render(root, python, console)
        _check_api(python)


if __name__ == "__main__":
    main()
