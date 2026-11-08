"""Typer application for static capability discovery."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from artifactspec.discovery import capabilities, installed_plugins
from artifactspec.plugins import ManifestCatalog, RegistrationError
from artifactspec.validation import validate


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main() -> None:
    """Discover installed ArtifactSpec plugin capabilities."""


@app.command("capabilities")
def show_capabilities(
    details: Annotated[
        bool, typer.Option("--details", help="Include individual contributions.")
    ] = False,
    output: Annotated[
        str | None, typer.Option("--output", help="Filter by output name.")
    ] = None,
) -> None:
    """Discover installed plugin capabilities without loading plugin code."""
    try:
        result = capabilities(details=details, output=output)
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(result, sort_keys=True))


@app.command("validate")
def validate_file(
    path: Annotated[Path, typer.Argument(help="UTF-8 ArtifactSpec file to validate.")],
    format: Annotated[
        OutputFormat, typer.Option("--format", help="Diagnostic output format.")
    ] = OutputFormat.text,
) -> None:
    """Validate a specification using installed static plugin metadata."""
    try:
        text = path.read_text(encoding="utf-8")
        catalog = ManifestCatalog(item[1] for item in installed_plugins().values())
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


@app.command("lsp")
def language_server() -> None:
    """Run the language server over standard input and output."""
    from artifactspec.lsp import start

    try:
        start()
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
