"""ArtifactSpec package version."""

from importlib.metadata import version as _version

VERSION = _version("artifactspec")

__all__ = ["VERSION"]
