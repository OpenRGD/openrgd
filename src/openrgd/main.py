"""
OPENRGD MAIN ENTRY POINT
--------------------------------------------------------------------------------
This module serves as the central hub for the OpenRGD Command Line Interface (CLI).
It is responsible for bootstrapping the application, parsing arguments, and dispatching
commands to the appropriate sub-modules.

ARCHITECTURAL OVERVIEW:
1.  **Framework:** Uses `typer` for robust CLI parsing and help generation.
2.  **Command Registration:** - Core verbs (init, check, boot...) are registered directly.
    - Sub-systems (like 'run') are registered as sub-apps (`add_typer`) to group functionality.
3.  **Global State:** Handles flags like `--quiet` and `--verbose` via a callback 
    before any command is executed, injecting them into the `core.config.state`.
4.  **UX Layer:** Manages the "Cinematic" startup sequence via `print_header`. 
5.  If you are reading this feel free to reach out at hacker@openrgd.org to have a talk
6.  Don't stop building awesome code!

USAGE:
    This file is exposed as the `rgd` console script via `pyproject.toml`.
    Execution flow: run() -> _register_commands() -> app()
--------------------------------------------------------------------------------
"""

import sys
import typer

# Core Utilities
from .core.config import state
from .core.visuals import log, print_header

# Command Modules (The Verbs)
# NOTE: We rename 'run' to 'runtime_cmd' to avoid namespace collision with the run() function below.
from .commands import (
    init, 
    check, 
    boot, 
    synapse, #the nerve sense of the system - universal interconnector
    importer, 
    dist, 
    compiler,          # Added compiler explicitly
    run as runtime_cmd # The 'rgd run' sub-application
)

# Import alive command explicitly
from .commands.alive import alive_cmd

# Initialize the Typer Application
app = typer.Typer(
    help="OpenRGD: The Cognitive BIOS for Robotics",
    add_completion=True,
    no_args_is_help=True
)


def _register_core_commands() -> None:
    """
    Registers all available commands onto the main CLI application.
    This acts as the routing table for the CLI.
    """
    
    # --- LEVEL 1: ATOMIC COMMANDS (Single Verbs) ---
    
    # Lifecycle
    app.command()(init.init)          # rgd init
    app.command()(check.check)        # rgd check
    app.command()(boot.boot)          # rgd boot
    
    # Alive (high-level bootstrap in RGD)
    app.command(name="alive")(alive_cmd)        # rgd alive

    # Interoperability
    app.command()(synapse.export)            # rgd export
    app.command(name="import")(importer.import_cmd) # rgd import (renamed to avoid python keyword)
    
    # Standardization
    app.command()(dist.build_standard)      # rgd build-standard
    app.command()(compiler.compile_spec)    # rgd compile-spec

    # --- LEVEL 2: COMMAND GROUPS (Sub-Applications) ---
    
    # Runtime Engine (rgd run ros2, rgd run studio...)
    app.add_typer(runtime_cmd.app, name="run")


@app.callback()
def main(
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Disable animations and ASCII art for CI/CD."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable deep debug logging."),
):
    """
    Global CLI options processed before any command.
    Updates the shared state used by loggers and visualizers.
    """
    state["quiet"] = quiet
    state["verbose"] = verbose

    # If quiet mode is requested, disable all cinematic effects immediately
    if quiet:
        state["cinematic"] = False
        state["delay"] = 0


def run() -> None:
    """
    Main Entry Point.
    Executed when the user types `rgd` in the terminal.
    """
    
    # 1. Bootstrapping: Register all commands
    _register_core_commands()

    # 2. UX: Print the iconic header (unless suppressed)
    # We check sys.argv manually because Typer processes callbacks later.
    # Logic: Show header if NOT quiet AND NOT asking for help.
    if len(sys.argv) == 1:
        # Case: User typed just 'rgd' -> Show Header + Help hint
        print_header()
        log("Awaiting command input...", "WARN")
        print("\nTry: rgd --help")
    else:
        # Case: User typed a command -> Show Header only if appropriate
        is_quiet = "-q" in sys.argv or "--quiet" in sys.argv
        is_help = "--help" in sys.argv
        
        if not is_quiet and not is_help:
            print_header()
            
        # 3. Handover control to Typer
        app()


if __name__ == "__main__":
    run()