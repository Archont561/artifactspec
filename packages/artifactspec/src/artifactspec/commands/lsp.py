"""Start the editor diagnostics server."""

from typing import Annotated

import typer

from artifactspec.plugins import RegistrationError

app = typer.Typer()


@app.command("lsp")
def serve(
    builtin_basic: Annotated[
        bool,
        typer.Option("--builtin-basic", help="Include static built-in capabilities."),
    ] = False,
) -> None:
    """Run the language server over standard input and output."""
    from artifactspec.lsp import start

    try:
        start(builtin_basic=builtin_basic)
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
