import time
from typing import Optional
from pathlib import Path
import typer
from rich.panel import Panel
from ..core.config import state, console
from ..core.visuals import log, smart_track
from ..core.utils import find_default_kernel, load_jsonc

def boot(
    kernel_path: Optional[Path] = typer.Argument(None), 
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json")
):
    """Generates the System Prompt."""
    if not kernel_path:
        kernel_path = find_default_kernel()
        if not kernel_path: log("No Kernel found.", "ERROR"); raise typer.Exit(1)

    log(f"Booting: {kernel_path.name}", "SYSTEM")
    try:
        data = load_jsonc(kernel_path)
        root_dir = kernel_path.parent
        if kernel_path.parent.name == "00_core": root_dir = kernel_path.parent.parent
        
        robot_id = data.get('meta_group', {}).get('id', 'Unknown')
        memory_bank = {}
        modules = data.get("module_loading_order_list", [])
        
        for mod_str in smart_track(modules, "[bold cyan]Loading Cognitive Modules...[/]"):
            if state["cinematic"]: time.sleep(0.15)
            try:
                # Path logic same as check
                mod_path = root_dir / mod_str
                if not mod_path.exists() and (root_dir / "spec" / mod_str).exists():
                    mod_path = root_dir / "spec" / mod_str
                
                mod_data = load_jsonc(mod_path)
                key = Path(mod_str).stem
                memory_bank[key] = mod_data
            except: log(f"Failed to load {mod_str}", "WARN")

        if output == "json":
            console.print_json(data=memory_bank)
        else:
            prompt = f"SYSTEM IDENTITY: {robot_id}\n{'='*40}\n\n"
            if "actuation_dynamics" in memory_bank:
                prompt += "[PHYSICAL CONSTRAINTS]\n"
                joints = memory_bank["actuation_dynamics"]
                for j, props in joints.items():
                     if isinstance(props, dict) and "limits" in props:
                        lim = props["limits"]
                        # Handle various torque keys
                        t_val = lim.get('torque_nm') or lim.get('effort') or 'N/A'
                        prompt += f"- {j}: Torque={t_val}Nm\n"
            if "alignment" in memory_bank:
                prompt += "\n[ETHICAL ALIGNMENT]\n"
                align = memory_bank["alignment"]
                prompt += f"Mission: {align.get('mission_statement', 'N/A')}\n"

            if state["quiet"]: print(prompt)
            else:
                console.print(Panel(prompt, title="🧠 LLM System Prompt", border_style="gold1"))
                log("Cognitive Grounding Complete.", "SUCCESS")
    except Exception as e:
        log(f"Boot failed: {e}", "ERROR"); raise typer.Exit(1)