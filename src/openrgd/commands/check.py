import time
from typing import Optional
from pathlib import Path
import typer
from rich.tree import Tree
from ..core.config import state, console
from ..core.visuals import log, smart_track
from ..core.utils import find_default_kernel, load_jsonc

def check(kernel_path: Optional[Path] = typer.Argument(None)):
    """Validates the Kernel integrity."""
    if not kernel_path:
        log("Auto-detecting Kernel...", "SYSTEM")
        kernel_path = find_default_kernel()
        if not kernel_path:
            log("No Kernel found.", "ERROR"); raise typer.Exit(1)
    else: kernel_path = kernel_path.resolve()

    log(f"Locked on: {kernel_path.name}", "SUCCESS")
    
    # Logic for root detection
    root_dir = kernel_path.parent
    if kernel_path.parent.name == "00_core": 
        root_dir = kernel_path.parent.parent

    try:
        data = load_jsonc(kernel_path)
        robot_id = data.get('meta_group', {}).get('id', 'Unknown')
        modules = data.get("module_loading_order_list", [])
        valid_count = 0
        
        tree = None
        if not state["quiet"]: tree = Tree(f"[bold icon]🤖 IDENTITY: {robot_id}")

        # Handle spec folder prefix if present in kernel but not in loading list, or vice versa
        # For v0.5 we assume kernel lists paths relative to project root or spec root?
        # Let's stick to standard: paths are relative to project root.
        
        for mod_str in smart_track(modules, "[green]Scanning Cortex...[/]"):
            if state["cinematic"]: time.sleep(0.1)
            
            # Try finding the file directly
            mod_path = root_dir / mod_str
            
            # Fallback: look inside 'spec' if not found
            if not mod_path.exists() and (root_dir / "spec" / mod_str).exists():
                mod_path = root_dir / "spec" / mod_str

            exists = mod_path.exists()
            if exists: valid_count += 1
            else: log(f"Missing: {mod_str}", "ERROR")
            
            if tree: tree.add(f"[{'green' if exists else 'bold red'}] {'✓' if exists else '✗'} {mod_str}[/]")

        if tree: console.print(tree)
        
        if valid_count == len(modules):
            log("Bios integrity: 100%", "SUCCESS")
            log("I am ready.", "AI")
        else:
            log("System corruption detected.", "ERROR"); raise typer.Exit(1)
    except Exception as e:
        log(f"Fatal Panic: {e}", "ERROR"); raise typer.Exit(1)