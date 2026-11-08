"""The repository coverage gate must reject insufficient coverage."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / ".coveragerc"


@pytest.mark.parametrize(
    ("source", "expected_code"),
    [
        ("value = 1\ndef unused():\n    return 2\n", 2),
        ("value = 1\n", 0),
    ],
    ids=["below-threshold", "fully-covered"],
)
def test_coverage_report_enforces_threshold(tmp_path, source, expected_code):
    sample = tmp_path / "sample.py"
    sample.write_text(source)
    env = os.environ.copy()
    env["COVERAGE_FILE"] = str(tmp_path / ".coverage")
    env.pop("COVERAGE_PROCESS_START", None)
    subprocess.run(
        [sys.executable, "-m", "coverage", "run", f"--rcfile={CONFIG}", str(sample)],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "report", f"--rcfile={CONFIG}"],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected_code, result.stdout + result.stderr
    if expected_code:
        assert "fail-under=91" in result.stdout
