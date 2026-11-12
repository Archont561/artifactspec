"""Run the configured Rude rules and fail on warnings or errors."""

import json
import os
import subprocess
import sys
from pathlib import Path

from rude.core import discover_rules, load_config

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "pyproject.toml"
REQUIRED_RULES = {
    "CC001",
    "CC002",
    "CC003",
    "CC004",
    "CC005",
    "CC101",
    "CC102",
    "CC103",
    "CC104",
    "CC107",
    "CC201",
    "CC202",
    "CC207",
    "CC301",
    "CC302",
    "CC303",
    "CC306",
    "CC308",
    "CC309",
    "CC310",
    "CC311",
    "CC903",
    "CC905",
    "CC906",
    "CC907",
    "CC910",
}


def python_files() -> list[str]:
    """Find tracked and unignored Python files, including hidden paths."""
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--deduplicate",
            "-z",
            "--",
            "*.py",
        ],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [
        os.fsdecode(path)
        for path in result.stdout.split(b"\0")
        if path and (ROOT / os.fsdecode(path)).is_file()
    ]


def required_rules_available() -> bool:
    """Fail closed if configuration or plugin discovery omits required rules."""
    if not CONFIG.is_file():
        return False
    config = load_config(CONFIG)
    if not config.select:
        return False
    rules = discover_rules(
        select=config.select, ignore=config.ignore, plugins=config.plugins
    )
    return REQUIRED_RULES <= {rule.code for rule in rules}


def main(paths: list[str]) -> int:
    """Check the requested paths, or all maintained Python by default."""
    if not required_rules_available():
        print(
            "Required Rude clean code rules are unavailable or disabled",
            file=sys.stderr,
        )
        return 1
    targets = paths or python_files()
    if not targets:
        print("No Python files found for the clean code check", file=sys.stderr)
        return 1
    command = [
        sys.executable,
        "-m",
        "rude",
        "check",
        "--config",
        str(CONFIG),
        "--format",
        "json",
        "--",
        *targets,
    ]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    failed = result.returncode != 0
    for line in result.stdout.splitlines():
        diagnostic = json.loads(line)
        print(
            f"{diagnostic['file']}:{diagnostic['line']}:{diagnostic['column']}: "
            f"{diagnostic['code']} {diagnostic['message']}"
        )
        failed |= diagnostic["severity"] in {"warning", "error"}
    return int(failed)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
