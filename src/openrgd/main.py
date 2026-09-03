"""OpenRGD command-line entry point."""

from __future__ import annotations

import sys

import typer

from .commands import (
    boot,
    check,
    compiler,
    dist,
    hash as hash_cmd,
    importer,
    init,
    run as runtime_boundary_cmd,
    synapse,
)
from .commands.alive import alive_cmd
from .core.config import state
from .core.visuals import log, print_header

app = typer.Typer(
    help="OpenRGD standard validation and interoperability toolchain",
    add_completion=True,
    no_args_is_help=True,
)


def _register_core_commands() -> None:
    """Register specification tooling and fail-closed compatibility commands."""

    app.command()(init.init)
    app.command()(check.check)
    app.command()(boot.boot)
    app.command(name="alive")(alive_cmd)

    app.command()(synapse.export)
    app.command(name="import")(importer.import_cmd)

    app.command(name="hash")(hash_cmd.bundle_hash)
    app.command()(dist.build_standard)
    app.command()(compiler.compile_spec)

    # Historical CLI compatibility only. This group never actuates hardware.
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
