import typer
from pathlib import Path
from ..core.visuals import log, smart_track
from ..core.config import state
from ..core.utils import find_default_kernel, load_jsonc
from ..bridges import get_bridge, AVAILABLE_BRIDGES

app = typer.Typer()

@app.command("export")
def export(
    target: str = typer.Argument(..., help=f"Target ecosystem ({', '.join(AVAILABLE_BRIDGES.keys())})"),
    output_dir: Path = typer.Option(Path("export"), "--out", "-o", help="Destination folder")
):
    """
    Bridges the semantic gap: Transpiles RGD into ecosystem-specific configs (ROS2, etc.).
    """
    # 1. Validate Target
    bridge_class = get_bridge(target.lower())
    if not bridge_class:
        log(f"Unknown bridge target: {target}", "ERROR")
        log(f"Available bridges: {', '.join(AVAILABLE_BRIDGES.keys())}", "INFO")
        raise typer.Exit(1)

    # 2. Find & Load Kernel
    kernel_path = find_default_kernel()
    if not kernel_path:
        log("No Kernel found. Cannot build bridge.", "ERROR")
        raise typer.Exit(1)
        
    log(f"Initializing Bridge: OPENRGD -> {target.upper()}", "SYSTEM")
    
    # 3. Prepare Environment
    kernel_data = load_jsonc(kernel_path)
    spec_dir = kernel_path.parent.parent # root/spec
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # 4. Execute Bridge
    try:
        # Instantiate the Adapter
        adapter = bridge_class(kernel_data, spec_dir)
        # Run generation
        adapter.generate(output_dir)
        
        log(f"Bridge construction complete in ./{output_dir}", "SUCCESS")
        
    except Exception as e:
        log(f"Bridge collapse: {e}", "ERROR")
        raise typer.Exit(1)