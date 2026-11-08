"""Inspect static plugin capability metadata."""

import json
from typing import Annotated

import typer

from artifactspec.plugins import RegistrationError
from artifactspec.plugins.discovery import capabilities

app = typer.Typer()


@app.command("capabilities")
def show_capabilities(
    details: Annotated[
        bool, typer.Option("--details", help="Include individual contributions.")
    ] = False,
    output: Annotated[
        str | None, typer.Option("--output", help="Filter by output name.")
    ] = None,
    builtin_basic: Annotated[
        bool,
        typer.Option("--builtin-basic", help="Include static built-in capabilities."),
    ] = False,
) -> None:
    """Discover installed plugin capabilities without loading plugin code."""
    try:
        result = capabilities(
            details=details, output=output, builtin_basic=builtin_basic
        )
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(result, sort_keys=True))
