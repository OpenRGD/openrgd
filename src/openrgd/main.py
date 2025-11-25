import typer
import sys
from .core.config import state
from .core.visuals import log, print_header
# Import commands (Nota: bridge è incluso qui)
from .commands import compiler, init, check, boot, bridge, importer, dist 

app = typer.Typer(
    help="OpenRGD: The Cognitive BIOS for Robotics",
    add_completion=True
)

# Register Commands
app.command()(init.init)
app.command()(check.check)
app.command()(boot.boot)
app.command()(compiler.compile_spec)
app.command()(bridge.export) # Bridge - ROS2
app.command(name="import")(importer.import_cmd) #Importer URDF, USD; ONSHAPE, etc.
app.command()(dist.build_standard) # standardization spec -> standard

@app.callback()
def main(
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Disable animations."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug."),
):
    state["quiet"] = quiet
    state["verbose"] = verbose
    if quiet:
        state["cinematic"] = False
        state["delay"] = 0

def run():
    """Entry point."""
    if len(sys.argv) == 1:
        print_header()
        log("Awaiting command input...", "WARN")
        print("\nTry: rgd --help")
    else:
        if "-q" not in sys.argv:
            print_header()
        app()

if __name__ == "__main__":
    run()