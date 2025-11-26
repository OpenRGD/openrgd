import typer
import sys
import threading
import time
from pathlib import Path
from ..core.visuals import log, print_header

# Importiamo gli adapter (i driver per i vari mondi)
# Nota: li importiamo dentro le funzioni per evitare errori se mancano le librerie (es. rclpy)
# Ma per la struttura, assumiamo che esistano in src/openrgd/runtime/adapters/

app = typer.Typer(help="Runtime execution engines.")

@app.command("ros2")
def run_ros2(
    kernel_path: Path = typer.Option(Path("spec/00_core/kernel.jsonc"), "--kernel", "-k", help="Path to RGD Kernel")
):
    """
    Starts the RGD Runtime Engine attached to the ROS 2 ecosystem.
    Dynamically subscribes to topics defined in hal_mapping.jsonc.
    """
    log("Initializing Cognitive Runtime (ROS 2 Adapter)...", "SYSTEM")
    
    # 1. Check Dependencies
    try:
        import rclpy
    except ImportError:
        log("Critical: 'rclpy' not found. Source your ROS 2 environment first.", "ERROR")
        raise typer.Exit(1)

    # 2. Load Core Logic (The Brain)
    from ..runtime.core.engine import RGDEngine
    from ..runtime.adapters.ros2.node import ROS2Adapter

    try:
        # Initialize the Mind (Pure Python)
        # Risolve il path relativo alla root se necessario
        if not kernel_path.exists():
             # Fallback smart search
             from ..core.utils import find_default_kernel
             kernel_path = find_default_kernel()
             
        engine = RGDEngine(kernel_path.parent.parent) # Passa la cartella 'spec'
        
        # Initialize the Body (ROS2 Middleware)
        rclpy.init()
        node = ROS2Adapter(engine)
        
        log("Neuro-Link Established. Listening to HAL mapping...", "SUCCESS")
        
        # 3. Spin (Blocking Loop)
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            log("Shutting down runtime...", "SYSTEM")
        finally:
            node.destroy_node()
            rclpy.shutdown()
            
    except Exception as e:
        log(f"Runtime Crash: {e}", "ERROR")
        raise typer.Exit(1)

@app.command("hybrid")
def run_hybrid():
    """
    [EXPERIMENTAL] Launches Multi-System Runtime (e.g. ROS2 + Viam + MQTT).
    This proves OpenRGD can bridge worlds.
    """
    log("Starting Hybrid Runtime Cluster...", "SYSTEM")
    # Qui in futuro useremo asyncio o threading per lanciare:
    # - thread_ros2.start()
    # - thread_viam.start()
    # - thread_rest_api.start()
    log("Feature coming in v0.6", "WARN")

@app.command("viam")
def run_viam():
    """
    Launches the Viam Runtime Adapter.
    Requires VIAM_ADDRESS and VIAM_SECRET env vars.
    """
    log("Ignition Sequence: RGD-CORE (Viam Adapter)", "SYSTEM")
    
    try:
        import viam
    except ImportError:
        log("Viam SDK not found. Run: pip install viam-sdk", "ERROR")
        raise typer.Exit(1)

    from ..runtime.core.engine import RGDEngine
    from ..runtime.adapters.viam.node import ViamAdapter
    from ..core.utils import find_default_kernel
    
    # Load Brain
    kernel_path = find_default_kernel()
    engine = RGDEngine(kernel_path.parent.parent)
    
    # Start Body
    adapter = ViamAdapter(engine)
    adapter.spin()