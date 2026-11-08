"""Start the editor diagnostics server."""

import typer

from artifactspec.plugins import RegistrationError

app = typer.Typer()


@app.command("lsp")
def serve() -> None:
    """Run the language server over standard input and output."""
    from artifactspec.editor.lsp import start

    try:
        start()
    except RegistrationError as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
