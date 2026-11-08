"""Render with explicitly selected, trusted plugins and capabilities."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from artifactspec.pipeline import PipelineError
from artifactspec.plugins import RegistrationError, Registry
from artifactspec.rendering import render

app = typer.Typer()


@app.command("render")
def render_command(
    path: Annotated[Path, typer.Argument(help="UTF-8 specification file.")],
    destination: Annotated[
        Path, typer.Option("--output", help="Destination artifact path.")
    ],
    representation: Annotated[
        str, typer.Option("--representation", help="Explicit representation name.")
    ],
    renderer: Annotated[
        str, typer.Option("--renderer", help="Explicit renderer name.")
    ],
    builtin_basic: Annotated[
        bool,
        typer.Option(
            "--builtin-basic", help="Trust and load the built-in basic plugin."
        ),
    ] = False,
    plugin: Annotated[
        list[str] | None,
        typer.Option(
            "--plugin",
            help="Trust and load an installed plugin ID; repeat for multiple plugins.",
        ),
    ] = None,
) -> None:
    """Validate and render using only explicitly trusted plugins."""
    registry = Registry()
    try:
        if builtin_basic:
            from artifactspec.basic import basic_plugin

            registry.register(basic_plugin())
        for plugin_id in plugin or []:
            registry.load_installed(plugin_id)
        if not builtin_basic and not plugin:
            raise RegistrationError(
                "select trusted plugins using --builtin-basic or --plugin"
            )
        text = path.read_text(encoding="utf-8")
        result = render(
            text,
            registry,
            representation=representation,
            renderer=renderer,
            destination=destination,
            source=str(path),
        )
    except PipelineError as exc:
        for diagnostic in exc.diagnostics:
            pos = diagnostic.span.start
            typer.echo(
                f"{diagnostic.span.source}:{pos.line}:{pos.column}: {diagnostic.severity} [{diagnostic.code}]: {diagnostic.message}",
                err=True,
            )
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=1 if exc.diagnostics else 2) from exc
    except (OSError, UnicodeError, RegistrationError) as exc:
        typer.echo(f"artifactspec: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    data = asdict(result)
    data["artifact"]["path"] = str(result.artifact.path)
    typer.echo(
        json.dumps({"schema_version": 1, **data}, ensure_ascii=False, sort_keys=True)
    )
