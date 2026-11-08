"""Inspect capabilities of installed plugin objects."""

import json
from typing import Annotated

import typer

from artifactspec.cli.commands._plugins import load_cli_registry
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
    """Import installed plugins and report their capabilities."""
    try:
        registry = load_cli_registry(
            autoload=not no_plugin_autoload, selected=tuple(plugin or ())
        )
        result = capabilities(
            details=details, output=output, plugins=registry.manifests()
        )
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(result, sort_keys=True))
