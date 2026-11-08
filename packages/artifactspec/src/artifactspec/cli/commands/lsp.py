"""Start the editor diagnostics server."""

from typing import Annotated

import typer

from artifactspec.plugins import RegistrationError

app = typer.Typer()


@app.command("lsp")
def serve(
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
    """Run the language server over standard input and output."""
    from artifactspec.editor.lsp import start

    try:
        start(autoload=not no_plugin_autoload, selected=tuple(plugin or ()))
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
