import shutil
import os
import re
from pathlib import Path
from typing import Optional
import typer
from importlib import resources
from ..core.visuals import log, smart_track, print_header
from ..core.config import state

def init(
    name: Optional[str] = typer.Argument(None, help="Name of the robot project")
):
    """
    Scaffolds a new OpenRGD project by cloning the internal Gold Standard seed.
    Includes automatic ID injection into the Kernel.
    """
    
    # 1. Interactive Input Handling
    if not name:
        if state["quiet"]:
            log("Missing argument 'NAME' in quiet mode.", "ERROR")
            raise typer.Exit(1)
            
        if not state["quiet"]: print_header()
        name = typer.prompt("🤖 Project Name")

    log(f"Initializing containment field: {name}", "SYSTEM")
    
    target_dir = Path(name)
    if target_dir.exists():
        log(f"Directory '{name}' exists. Abort.", "ERROR")
        raise typer.Exit(1)

    # 2. Locate Internal Seeds (The DNA)
    try:
        # This finds the 'seeds/default' folder inside the installed package
        package_files = resources.files("openrgd") / "seeds" / "default"
    except Exception:
        log("Could not locate internal seeds. Is the package installed correctly?", "ERROR")
        raise typer.Exit(1)

    log(f"Cloning Gold Standard Template...", "DEBUG")

    # 3. Cinematic Simulation (Optional)
    if state["cinematic"]:
        import time
        dirs_to_show = ["00_core", "01_foundation", "02_operation", "03_agency", "04_volition", "05_evolution", "06_ether"]
        for d in smart_track(dirs_to_show, "[cyan]Injecting Neural Pathways...[/]"):
            time.sleep(0.1)

    # 4. Physical Copy (The Cloning)
    src_path = str(package_files)
    try:
        shutil.copytree(src_path, target_dir)
    except Exception as e:
        log(f"Cloning failed: {e}", "ERROR")
        raise typer.Exit(1)

    # 5. Kernel Personalization (The Identity Injection)
    # We open the new kernel.jsonc and replace the default ID with the user's project name
    kernel_path = target_dir / "spec/00_core/kernel.jsonc"
    
    if kernel_path.exists():
        try:
            with open(kernel_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex to find "id": "did:rgd:..." and replace it
            new_id = f"did:rgd:{name.lower().replace(' ', '-')}"
            content = re.sub(r'"id":\s*"did:rgd:[^"]+"', f'"id": "{new_id}"', content)
            
            with open(kernel_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            log(f"Identity assigned: {new_id}", "DEBUG")
        except Exception as e:
            log(f"Failed to personalize kernel ID: {e}", "WARN")

    # 6. Success Handover
    log("Kernel & Semantic Graph injected.", "SUCCESS")
    
    if not state["quiet"]:
        print(f"\n\033[1;32m» Project ready in ./{name}\033[0m")
        print(f"  Try: cd {name} && rgd compile-spec")