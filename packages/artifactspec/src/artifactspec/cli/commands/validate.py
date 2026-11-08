"""Validate a specification and present source-linked diagnostics."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from artifactspec.cli.commands._plugins import load_cli_registry
from artifactspec.core.validation import validate
from artifactspec.plugins import RegistrationError

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
    no_plugin_autoload: Annotated[
        bool,
        typer.Option(
            "--no-plugin-autoload", help="Only import explicitly selected plugins."
        ),
    ] = False,
    plugin: Annotated[
        list[str] | None,
        typer.Option("--plugin", help="Select a plugin ID; repeat as needed."),
    ] = None,
) -> None:
    """Validate a specification using imported plugin declarations."""
    try:
        text = path.read_text(encoding="utf-8")
        catalog = load_cli_registry(
            autoload=not no_plugin_autoload, selected=tuple(plugin or ())
        )
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
