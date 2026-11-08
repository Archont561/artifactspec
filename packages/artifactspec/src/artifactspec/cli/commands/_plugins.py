"""Load CLI plugins without letting import-time prints corrupt stdout output."""

import sys
from contextlib import redirect_stdout

from artifactspec.plugins import Registry
from artifactspec.plugins.discovery import load_registry


def load_cli_registry(*, autoload: bool, selected: tuple[str, ...]) -> Registry:
    with redirect_stdout(sys.stderr):
        return load_registry(autoload=autoload, selected=selected)
