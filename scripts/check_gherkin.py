"""Fail on any gherlint finding, even if its process returns zero."""

import subprocess
import sys


def main() -> int:
    failed = False
    for path in ("packages", "scripts/tests"):
        result = subprocess.run(
            ["gherlint", "lint", path], capture_output=True, text=True, check=False
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        failed |= bool(result.returncode or result.stdout.strip())
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
