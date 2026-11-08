"""Render with explicitly selected, trusted plugins and capabilities."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from artifactspec.core.pipeline import PipelineError
from artifactspec.core.rendering import render
from artifactspec.core.validation import Diagnostic
from artifactspec.plugins import RegistrationError, Registry

app = typer.Typer()


class OutputFormat(str, Enum):
    legacy = "legacy"
    json = "json"


def _json(data: dict[str, object]) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, sort_keys=True))


def _failure_json(
    code: str,
    message: str,
    *,
    diagnostics: tuple[Diagnostic, ...] = (),
    warnings: tuple[Diagnostic, ...] = (),
    limitations: tuple[str, ...] = (),
) -> None:
    _json(
        {
            "schema_version": 1,
            "status": "error",
            "error": {"code": code, "message": message},
            "diagnostics": [asdict(item) for item in diagnostics],
            "warnings": [asdict(item) for item in warnings],
            "limitations": list(limitations),
            "fallback": None,
        }
    )


def _pipeline_error(exc: PipelineError, format: OutputFormat) -> None:
    if format == OutputFormat.json:
        _failure_json(
            exc.code,
            str(exc),
            diagnostics=exc.diagnostics,
            warnings=exc.warnings,
            limitations=exc.limitations,
        )
    else:
        for diagnostic in exc.diagnostics:
            pos = diagnostic.span.start
            typer.echo(
                f"{diagnostic.span.source}:{pos.line}:{pos.column}: {diagnostic.severity} [{diagnostic.code}]: {diagnostic.message}",
                err=True,
            )
        typer.echo(f"artifactspec: {exc}", err=True)


def _operational_error(
    exc: OSError | UnicodeError | RegistrationError, format: OutputFormat
) -> None:
    if format == OutputFormat.json:
        code = "plugin_error" if isinstance(exc, RegistrationError) else "io_error"
        _failure_json(code, str(exc))
    else:
        typer.echo(f"artifactspec: {exc}", err=True)


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
    format: Annotated[
        OutputFormat, typer.Option("--format", help="Render result and failure format.")
    ] = OutputFormat.legacy,
    no_plugin_autoload: Annotated[
        bool,
        typer.Option(
            "--no-plugin-autoload",
            help="Do not automatically execute installed plugin code.",
        ),
    ] = False,
    plugin: Annotated[
        list[str] | None,
        typer.Option(
            "--plugin",
            help="Require a plugin ID; with autoload disabled, load only named plugins. Repeat as needed.",
        ),
    ] = None,
) -> None:
    """Validate and render with installed plugins or explicitly selected plugins."""
    registry = Registry()
    try:
        if no_plugin_autoload:
            for plugin_id in plugin or []:
                registry.load_installed(plugin_id)
        else:
            registry.load_all_installed(required=plugin or ())
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
        _pipeline_error(exc, format)
        raise typer.Exit(code=1 if exc.diagnostics else 2) from exc
    except (OSError, UnicodeError, RegistrationError) as exc:
        _operational_error(exc, format)
        raise typer.Exit(code=2) from exc
    data = asdict(result)
    data["artifact"]["path"] = str(result.artifact.path)
    if format == OutputFormat.json:
        data["status"] = "success"
    _json({"schema_version": 1, **data})
