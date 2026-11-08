"""Build, validate, and smoke-test the distributions in an isolated environment."""

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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="artifactspec-packages-") as directory:
        root = Path(directory)
        outputs = root / "distributions"
        for package in ("artifactspec", "artifactspec-manim"):
            run(
                sys.executable,
                "-m",
                "build",
                str(ROOT / "packages" / package),
                "--outdir",
                str(outputs),
            )
        files = sorted(outputs.iterdir())
        if len(files) != 4:
            raise RuntimeError("Expected one wheel and one sdist per distribution")
        run(sys.executable, "-m", "twine", "check", *(str(path) for path in files))
        wheels = sorted(outputs.glob("*.whl"))
        for wheel in wheels:
            with zipfile.ZipFile(wheel) as archive:
                if not any(
                    name.endswith(".dist-info/licenses/LICENSE")
                    for name in archive.namelist()
                ):
                    raise RuntimeError(f"License missing from {wheel.name}")
        core = next(path for path in wheels if path.name.startswith("artifactspec-"))
        manim = next(
            path for path in wheels if path.name.startswith("artifactspec_manim-")
        )
        venv = root / "venv"
        run(sys.executable, "-m", "venv", str(venv))
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run(str(python), "-m", "pip", "install", str(core))
        # The optional Manim placeholder remains an independent distribution.
        run(str(python), "-m", "pip", "install", "--no-deps", str(manim))
        run(str(python), "-I", "-m", "artifactspec", "capabilities", "--details")
        console = venv / (
            "Scripts/artifactspec.exe" if os.name == "nt" else "bin/artifactspec"
        )
        run(str(console), "capabilities", "--details")
        run(
            str(python),
            "-I",
            "-c",
            "from importlib.metadata import version; "
            "import artifactspec, artifactspec_manim; "
            "assert artifactspec.VERSION == version('artifactspec'); "
            "assert artifactspec_manim.VERSION == version('artifactspec-manim'); "
            "assert artifactspec.__all__ == ['VERSION']; "
            "assert artifactspec_manim.__all__ == ['VERSION']; "
            "from artifactspec.parser import parse; "
            "from artifactspec.plugins import Plugin, Registry; "
            "plugin = Plugin('example', '1', outputs=('image',)); "
            "plugin.phrase('circle')(lambda context: None); "
            "plugin.property('label')(lambda context: None); "
            "registry = Registry(); registry.register(plugin); "
            "document = parse('Output image.\\nCreate circle named sun.\\n"
            'Set label of sun to \\"hello\\".\', registry); '
            "assert document.statements[0].name == 'sun'; "
            "assert document.statements[1].value.value == 'hello'",
        )


if __name__ == "__main__":
    main()
