import typer
from pathlib import Path
from ..core.visuals import log
from ..synapses import get_synapse, AVAILABLE_SYNAPSES

def export(
    target: str = typer.Argument(..., help=f"Target system ({', '.join(AVAILABLE_SYNAPSES.keys())})"),
    output_dir: Path = typer.Option(Path("export"), "--out", "-o",
                                    help="Output directory for generated export."),
):
    """
    Transpiles the RGD Specification into target ecosystem configuration files.

    Forms a static Synapse between OpenRGD and the specified external system
    (e.g. ROS2, NVIDIA Isaac Lab, etc.).
    """
    synapse_class = get_synapse(target.lower())
    synapse = synapse_class(output_dir=output_dir)

    log(f"Synapse formed: OPENRGD <--> {target.upper()}", "SUCCESS")
    synapse.generate()
