"""Select conservative CI scopes from the Git diff; unknown changes run full CI."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    ).stdout


def kind(path: str) -> str:
    if path.startswith(("docs/", "backlog/")) or path in {"README.md", "CHANGELOG.md"}:
        return "docs"
    if path.startswith("packages/") and Path(path).name == "README.md":
        return "docs"
    if path.startswith("scripts/"):
        return "scripts"
    return "full"


def detect(repo: Path, base: str, head: str, event: str) -> dict:
    # No reliable comparison must never make CI lighter.
    if not base or set(base) == {"0"}:
        return {"scope": "full", "reason": "no base revision", "paths": []}
    try:
        if event == "pull_request":
            base = git(repo, "merge-base", base, head).decode().strip()
        raw = git(repo, "diff", "--name-only", "-z", "--no-renames", base, head, "--")
    except (subprocess.CalledProcessError, OSError) as exc:
        return {
            "scope": "full",
            "reason": f"unable to compare revisions: {exc}",
            "paths": [],
        }
    paths = [os.fsdecode(path) for path in raw.split(b"\0") if path]
    kinds = {kind(path) for path in paths}
    if not kinds or "full" in kinds:
        scope = "full"
    elif "scripts" in kinds:
        scope = "scripts"
    else:
        scope = "docs"
    return {
        "scope": scope,
        "reason": "changed paths" if paths else "empty diff",
        "paths": paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument(
        "--event", default="push", choices=["push", "pull_request", "workflow_dispatch"]
    )
    args = parser.parse_args()
    result = detect(args.repo, args.base, args.head, args.event)
    scope = result["scope"]
    run_docs = scope == "docs" or (
        scope == "scripts" and any(kind(path) == "docs" for path in result["paths"])
    )
    # Simple scalar fields are safe to pass between GitHub Actions jobs.
    flags = {
        "scope": scope,
        "run_full": str(scope == "full").lower(),
        "run_scripts": str(scope == "scripts").lower(),
        "run_docs": str(run_docs).lower(),
        "skip_full": str(scope != "full").lower(),
        "skip_scripts": str(scope != "scripts").lower(),
        "skip_docs": str(not run_docs).lower(),
        "skip_coverage": str(scope != "full").lower(),
    }
    for variable in ("GITHUB_OUTPUT", "GITHUB_ENV"):
        if destination := os.environ.get(variable):
            with Path(destination).open("a", encoding="utf-8") as file:
                file.writelines(f"{name}={value}\n" for name, value in flags.items())
    print(json.dumps({**result, **flags}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
