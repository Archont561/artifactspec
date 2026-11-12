"""Select a conservative revision range for conventional-commit validation."""

import argparse
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def commit(repo: Path, revision: str) -> str:
    return git(
        repo, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"
    )


def _default_comparison(repo: Path, head: str, ref: str, default: str) -> str | None:
    if not default or not ref.startswith("refs/heads/") or ref == "refs/heads/":
        raise ValueError("branch or default branch is unavailable")
    # On the default branch, origin/<default> already points to the new
    # head. Comparing against it would silently select no commits.
    if ref == f"refs/heads/{default}":
        return None
    default_head = commit(repo, f"refs/remotes/origin/{default}")
    return git(repo, "merge-base", default_head, head)


def select_range(
    repo: Path, base: str, head: str, event: str, forced: bool, ref: str, default: str
) -> str:
    head = commit(repo, head)
    missing_base = not base or all(char == "0" for char in base)

    if (event == "push" and (forced or missing_base)) or (
        event == "workflow_dispatch" and missing_base
    ):
        comparison_base = _default_comparison(repo, head, ref, default)
        if comparison_base is None:
            return head
        base = comparison_base
    elif missing_base:
        raise ValueError("comparison base is unavailable")
    else:
        base = commit(repo, base)
        if event == "pull_request":
            base = git(repo, "merge-base", base, head)

    return f"{base}..{head}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", default="")
    parser.add_argument("--head", required=True)
    parser.add_argument(
        "--event", required=True, choices=["push", "pull_request", "workflow_dispatch"]
    )
    parser.add_argument("--forced", choices=["true", "false"], default="false")
    parser.add_argument("--ref", default="")
    parser.add_argument("--default-branch", default="")
    args = parser.parse_args()
    try:
        result = select_range(
            args.repo,
            args.base,
            args.head,
            args.event,
            args.forced == "true",
            args.ref,
            args.default_branch,
        )
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        print(f"Cannot select commit range: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
