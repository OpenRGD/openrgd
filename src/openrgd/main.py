"""
OPENRGD MAIN ENTRY POINT
--------------------------------------------------------------------------------
This module serves as the central hub for the OpenRGD Command Line Interface (CLI).
It bootstraps the application, parses arguments, and dispatches commands to the
appropriate modules.

ARCHITECTURAL OVERVIEW:
1. Uses Typer for CLI parsing.
2. Registers core specification/tooling verbs directly.
3. Retains ``rgd run`` only as a fail-closed compatibility/status group; the
   canonical package does not ship a physical embodied runtime.
4. Handles shared ``--quiet`` and ``--verbose`` state.
5. Manages optional cinematic output.

USAGE:
    This file is exposed as the ``rgd`` console script via ``pyproject.toml``.
    Execution flow: run() -> _register_core_commands() -> app()
--------------------------------------------------------------------------------
"""

import sys

import typer

from .core.config import state
from .core.visuals import log, print_header
from .commands import (
    boot,
    check,
    compiler,
    dist,
    importer,
    init,
    run as runtime_boundary_cmd,
    synapse,
)
from .commands.alive import alive_cmd

app = typer.Typer(
    help="OpenRGD: The Cognitive BIOS for Robotics",
    add_completion=True,
    no_args_is_help=True,
)


def _register_core_commands() -> None:
    """Register the canonical toolchain and compatibility command groups."""

    # Lifecycle and specification tooling.
    app.command()(init.init)
    app.command()(check.check)
    app.command()(boot.boot)
    app.command(name="alive")(alive_cmd)

    # Interoperability.
    app.command()(synapse.export)
    app.command(name="import")(importer.import_cmd)

    # Standardization.
    app.command()(dist.build_standard)
    app.command()(compiler.compile_spec)

    # Historical CLI compatibility. This group never actuates hardware.
    app.add_typer(runtime_boundary_cmd.app, name="run")


@app.callback()
def main(
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Disable animations and ASCII art for CI/CD.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable deep debug logging.",
    ),
) -> None:
    """Process global CLI options before command dispatch."""

    state["quiet"] = quiet
    state["verbose"] = verbose

    if quiet:
        state["cinematic"] = False
        state["delay"] = 0


def run() -> None:
    """Execute the ``rgd`` console entry point."""

    _register_core_commands()

    if len(sys.argv) == 1:
        print_header()
        log("Awaiting command input...", "WARN")
        print("\nTry: rgd --help")
        return

    is_quiet = "-q" in sys.argv or "--quiet" in sys.argv
    is_help = "--help" in sys.argv

    if not is_quiet and not is_help:
        print_header()

    app()


if __name__ == "__main__":
    run()
