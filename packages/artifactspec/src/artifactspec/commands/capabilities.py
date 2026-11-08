"""Inspect static plugin capability metadata."""

import json
from typing import Annotated

import typer

from artifactspec.discovery import capabilities
from artifactspec.plugins import RegistrationError

app = typer.Typer()


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
