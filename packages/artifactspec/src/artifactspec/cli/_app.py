"""Discover and register built-in Typer applications."""

from importlib import import_module
from pkgutil import iter_modules

import typer
from typer.main import get_command_name, solve_typer_info_defaults

from artifactspec.cli import commands


def _check_command_tree(
    app: typer.Typer, names: set[str], path: tuple[str, ...], ancestors: set[int]
) -> None:
    """Reject collisions that Typer would otherwise silently overwrite."""
    if id(app) in ancestors:
        raise ValueError(f"Cyclic CLI command group at {' '.join(path) or '<root>'}")
    ancestors = ancestors | {id(app)}

    def claim(name: str) -> None:
        if name in names:
            raise ValueError(f"Duplicate CLI command {' '.join((*path, name))!r}")
        names.add(name)

    for command in app.registered_commands:
        if command.callback is None:
            raise ValueError("CLI command must have a callback")
        claim(command.name or get_command_name(command.callback.__name__))
    for group in app.registered_groups:
        child = group.typer_instance
        if child is None:
            raise ValueError("CLI command group must have a Typer app")
        info = solve_typer_info_defaults(group)
        if info.name:
            claim(info.name)
            _check_command_tree(child, set(), (*path, info.name), ancestors)
        else:
            # Typer flattens unnamed apps and does not execute their callbacks.
            if info.callback is not None:
                raise ValueError(
                    "Unnamed CLI command groups cannot have callbacks; give the group a name"
                )
            _check_command_tree(child, names, path, ancestors)


def create_app() -> typer.Typer:
    """Build the app from public, first-party command modules."""
    app = typer.Typer(add_completion=False, no_args_is_help=True)

    @app.callback()
    def main() -> None:
        """Discover installed ArtifactSpec plugin capabilities."""

    modules = sorted(iter_modules(commands.__path__), key=lambda item: item.name)
    for info in modules:
        if info.ispkg or info.name.startswith("_"):
            continue
        module = import_module(f"{commands.__name__}.{info.name}")
        module_app = getattr(module, "app", None)
        if not isinstance(module_app, typer.Typer):
            raise TypeError(
                f"Invalid CLI command module {module.__name__!r}: expected a Typer app"
            )
        app.add_typer(module_app)
    _check_command_tree(app, set(), (), set())
    return app


app = create_app()
