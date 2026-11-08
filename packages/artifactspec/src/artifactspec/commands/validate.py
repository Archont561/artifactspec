"""Validate a specification and present source-linked diagnostics."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from artifactspec.discovery import installed_plugins
from artifactspec.plugins import ManifestCatalog, RegistrationError
from artifactspec.validation import validate

app = typer.Typer()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


@app.command("validate")
def validate_file(
    path: Annotated[Path, typer.Argument(help="UTF-8 ArtifactSpec file to validate.")],
    format: Annotated[
        OutputFormat, typer.Option("--format", help="Diagnostic output format.")
    ] = OutputFormat.text,
    builtin_basic: Annotated[
        bool,
        typer.Option("--builtin-basic", help="Include static built-in capabilities."),
    ] = False,
) -> None:
    """Validate a specification using installed static plugin metadata."""
    try:
        text = path.read_text(encoding="utf-8")
        manifests = [item[1] for item in installed_plugins().values()]
        if builtin_basic:
            from artifactspec._basic_metadata import basic_manifest

            manifests.append(basic_manifest())
        catalog = ManifestCatalog(manifests)
        result = validate(text, catalog, source=str(path))
    except (OSError, UnicodeError, RegistrationError) as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    if format == OutputFormat.json:
        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "valid": result.valid,
                    "diagnostics": [asdict(item) for item in result.diagnostics],
                },
                sort_keys=True,
                ensure_ascii=False,
            )
        )
    else:
        for item in result.diagnostics:
            position = item.span.start
            typer.echo(
                f"{item.span.source}:{position.line}:{position.column}: {item.severity} [{item.code}]: {item.message}"
            )
        if result.valid and not result.diagnostics:
            typer.echo(f"{path}: valid")
    if not result.valid:
        raise typer.Exit(code=1)
