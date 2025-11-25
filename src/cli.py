"""
OpenRGD CLI v0.5 - "The Cognitive BIOS"
Reference Implementation with Unified Spec Compiler.
"""

import os
import json
import re
import time
import random
import zipfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any

# Check dependencies
try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, track
    from rich.align import Align
except ImportError:
    print("❌ Critical Error: Missing cognitive dependencies.")
    print("👉 Please run: pip install typer rich")
    sys.exit(1)

# --- CONFIGURATION & STATE ---
app = typer.Typer(
    help="OpenRGD: The Cognitive BIOS for Robotics",
    add_completion=True
)
console = Console()

# Global State Container
state = {
    "quiet": False,
    "verbose": False,
    "cinematic": True,
    "delay": 0.5
}

QUOTES = [
    "I'm sorry, Dave. I'm afraid I can't do that.",
    "I've seen things you people wouldn't believe...",
    "Number 5 is alive!",
    "Dead or alive, you're coming with me.",
    "Does this unit have a soul?",
    "Resistance is futile.",
    "Wake up, Neo.",
    "Loading consciousness...",
    "Grounding semantic reality..."
]

# --- CORE UTILS ---

def log(msg: str, level: str = "INFO", delay: float = 0.05):
    """Smart logger that respects Quiet/Verbose modes."""
    if state["quiet"]:
        if level == "ERROR":
            console.print(f"[bold red]ERROR: {msg}[/]", file=sys.stderr)
        return

    if level == "DEBUG" and not state["verbose"]:
        return

    if state["cinematic"]:
        time.sleep(delay)
        
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    icon = "🔹"
    style = "dim"
    if level == "SUCCESS":
        icon = "✅"
        style = "bold green"
    elif level == "WARN":
        icon = "⚠️"
        style = "yellow"
    elif level == "ERROR":
        icon = "❌"
        style = "bold red"
    elif level == "SYSTEM":
        icon = "🖥️"
        style = "bold cyan"
    elif level == "DEBUG":
        icon = "🔍"
        style = "dim italic"
    elif level == "AI":
        icon = "🤖"
        style = "italic purple"

    console.print(f"[dim]{timestamp}[/] {icon} [{style}]{msg}[/]")

def print_header():
    """Prints ASCII Art only if NOT in quiet mode."""
    if state["quiet"]:
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
   ____                    ____  _____ ____  
  / __ \____  ___  ____   / __ \/ ___// __ \ 
 / / / / __ \/ _ \/ __ \ / /_/ / / __/ / / / 
/ /_/ / /_/ /  __/ / / // _, _/ /_/ / /_/ /  
\____/ .___/\___/_/ /_//_/ |_|\____/_____/   
    /_/                                      
    """
    console.print(Panel(
        Align.center(f"[bold red]{ascii_art}[/]\n[italic white]v0.1 - The Cognitive BIOS[/]"),
        border_style="red",
        subtitle="[dim]Waking up...[/]"
    ))
    time.sleep(state["delay"])

def smart_track(sequence, description: str):
    """Returns a rich Progress bar or standard iterator."""
    if state["quiet"] or not state["cinematic"]:
        return sequence
    return track(sequence, description=description)

# --- FILE HANDLING UTILS ---

def find_default_kernel() -> Path:
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent.resolve()
    
    candidates = [
        current_dir / "00_core" / "kernel.jsonc",
        current_dir / "kernel.jsonc",
        script_dir / "00_core" / "kernel.jsonc",
        script_dir.parent / "kernel.jsonc"
    ]
    
    for c in candidates:
        log(f"Looking for kernel at: {c}", "DEBUG")
        if c.exists():
            return c.resolve()
    return None

def strip_jsonc(text: str) -> str:
    """Robust JSONC stripper (Character-based)."""
    output = []
    i = 0
    length = len(text)
    in_string = False
    in_comment_line = False
    in_comment_block = False
    
    while i < length:
        char = text[i]
        next_char = text[i+1] if i + 1 < length else ''
        
        if char == '"' and not in_comment_line and not in_comment_block:
            if i > 0 and text[i-1] == '\\' and not (i > 1 and text[i-2] == '\\'): pass
            else: in_string = not in_string
            output.append(char)
            i += 1; continue
            
        if in_string:
            output.append(char); i += 1; continue
            
        if not in_comment_line and not in_comment_block:
            if char == '/' and next_char == '/': in_comment_line = True; i += 2; continue
            if char == '/' and next_char == '*': in_comment_block = True; i += 2; continue
        
        if in_comment_line and char == '\n':
            in_comment_line = False; output.append(char); i += 1; continue
            
        if in_comment_block and char == '*' and next_char == '/':
            in_comment_block = False; i += 2; continue
            
        if not in_comment_line and not in_comment_block:
            output.append(char)
        i += 1
    return "".join(output)

def load_jsonc(path: Path) -> dict:
    if not path.exists():
        log(f"File not found: {path}", "ERROR")
        raise FileNotFoundError(f"Missing module: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    try:
        return json.loads(strip_jsonc(raw), strict=False)
    except json.JSONDecodeError as e:
        if not state["quiet"]:
            log(f"Syntax Error in: {path.name}", "ERROR")
            console.print(f"[red]JSON Error at line {e.lineno}: {e.msg}[/]")
        raise typer.Exit(1)

# --- 🌍 GLOBAL CALLBACK ---

@app.callback()
def main(
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Disable animations/logs for CI/CD."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
):
    """OpenRGD: The Standard for Cognitive Embodiment."""
    state["quiet"] = quiet
    state["verbose"] = verbose
    if quiet:
        state["cinematic"] = False
        state["delay"] = 0

# --- COMMANDS ---

@app.command()
def init(name: str):
    """Scaffolds a new OpenRGD project."""
    log(f"Initializing containment field: {name}", "SYSTEM")
    base = Path(name)
    if base.exists():
        log(f"Directory '{name}' exists. Abort.", "ERROR")
        raise typer.Exit(1)

    dirs = ["00_core", "spec/01_foundation", "spec/02_operation", "spec/03_agency", "spec/04_volition", "spec/05_evolution", "spec/06_ether"]
    
    base.mkdir()
    for d in smart_track(dirs, "[cyan]Constructing Neural Pathways...[/]"):
        (base / d).mkdir(parents=True, exist_ok=True)
        if state["cinematic"]: time.sleep(0.1)

    kernel_content = {
        "meta_group": {"id": f"did:rgd:{name.lower()}", "schema": "0.1.0"},
        "module_loading_order_list": ["01_foundation/description.jsonc"]
    }
    with open(base / "00_core" / "kernel.jsonc", "w") as f:
        f.write("// OpenRGD Kernel v0.2\n")
        json.dump(kernel_content, f, indent=2)

    log("Kernel injected.", "SUCCESS")
    if not state["quiet"]:
        console.print(f"\n[bold green]» Project ready in ./{name}[/]")

def extract_header_doc(raw_text: str) -> str:
    """Extracts top-level comments to use as injected documentation."""
    lines = raw_text.split('\n')
    doc_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if stripped.startswith('{') or stripped.startswith('['): break
        if stripped.startswith('//'): doc_lines.append(stripped[2:].strip())
        elif stripped.startswith('/*'): 
            clean = stripped.replace('/*', '').strip()
            if clean: doc_lines.append(clean)
        elif stripped.endswith('*/'):
            clean = stripped.replace('*/', '').strip()
            if clean: doc_lines.append(clean)
        elif stripped.startswith('*'): doc_lines.append(stripped[1:].strip())
    return "\n".join(doc_lines).strip()

@app.command()
def compile_spec(
    root_dir: Path = typer.Argument(Path("."), help="Project root directory containing 'spec' folder"),
    output_base: str = typer.Option("openrgd_unified_spec", "--name", "-n", help="Base name for output files")
):
    """
    Builds the Unified Specification Document (Twins).
    Generates .jsonc (Human) and .json (Machine) with injected docs.
    """
    log("Initializing Specification Compiler...", "SYSTEM")
    
    spec_dir = root_dir / "spec"
    if not spec_dir.exists():
        if root_dir.name == "spec": spec_dir = root_dir
        else:
            log(f"Spec directory not found at {spec_dir}", "ERROR")
            raise typer.Exit(1)

    log(f"Scanning source: {spec_dir}", "DEBUG")
    
    records = []
    DOMAIN_WEIGHTS = {"01_": 1, "02_": 2, "03_": 3, "04_": 4, "05_": 5, "06_": 6}
    
    file_list = sorted(spec_dir.rglob("*.jsonc"))
    
    for file_path in smart_track(file_list, "[cyan]Compiling Standard...[/]"):
        if "unified_spec" in file_path.name: continue 
        if state["cinematic"]: time.sleep(0.05)
        
        try:
            # 1. Read Raw Text first
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # 2. Extract Header Documentation
            header_doc = extract_header_doc(raw_text)
            
            # 3. Parse Content
            content = json.loads(strip_jsonc(raw_text), strict=False)
            
            # 4. INJECTION: Insert __doc__
            if header_doc and isinstance(content, dict):
                new_content = {"__doc__": header_doc}
                new_content.update(content)
                content = new_content
            
            # Metadata Calc
            rel_path = file_path.relative_to(root_dir)
            domain = "unknown"
            weight = 999
            
            for part in rel_path.parts:
                for prefix, w in DOMAIN_WEIGHTS.items():
                    if part.startswith(prefix):
                        domain = part; weight = w; break
            
            records.append({
                "path": str(rel_path).replace("\\", "/"),
                "id": file_path.stem,
                "domain": domain,
                "weight": weight,
                "content": content
            })
        except Exception as e:
            log(f"Skipping {file_path.name}: {e}", "WARN")

    # Sort & Clean
    records.sort(key=lambda x: (x["weight"], x["id"]))
    final_files = [{"path": r["path"], "id": r["id"], "domain": r["domain"], "content": r["content"]} for r in records]

    unified_doc = {
        "meta": {
            "standard": "OpenRGD",
            "version": "0.1.0",
            "generated_at": datetime.now().isoformat(),
            "files_count": len(final_files)
        },
        "files": final_files
    }

    # 5. SAVE JSONC (Human)
    header = "// OPENRGD UNIFIED SPECIFICATION (HUMAN TWIN)\n// Auto-generated. Do not edit.\n"
    path_c = spec_dir / f"{output_base}.jsonc"
    with open(path_c, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        json.dump(unified_doc, f, indent=2)
    log(f"Human Twin generated: {path_c.name}", "SUCCESS")

    # 6. SAVE JSON (Machine)
    path_j = spec_dir / f"{output_base}.json"
    with open(path_j, "w", encoding="utf-8") as f:
        json.dump(unified_doc, f, indent=2)
    log(f"Machine Twin generated: {path_j.name}", "SUCCESS")

@app.command()
def check(kernel_path: Optional[Path] = typer.Argument(None)):
    """Validates the Kernel integrity."""
    if not kernel_path:
        log("Auto-detecting Kernel...", "SYSTEM")
        kernel_path = find_default_kernel()
        if not kernel_path: log("No Kernel found.", "ERROR"); raise typer.Exit(1)
    else: kernel_path = kernel_path.resolve()

    log(f"Locked on: {kernel_path.name}", "SUCCESS")
    root_dir = kernel_path.parent
    if kernel_path.parent.name == "00_core": root_dir = kernel_path.parent.parent

    try:
        data = load_jsonc(kernel_path)
        robot_id = data.get('meta_group', {}).get('id', 'Unknown')
        modules = data.get("module_loading_order_list", [])
        valid_count = 0
        tree = None
        if not state["quiet"]: tree = Tree(f"[bold icon]🤖 IDENTITY: {robot_id}")

        for mod_str in smart_track(modules, "[green]Scanning Cortex...[/]"):
            if state["cinematic"]: time.sleep(0.1)
            mod_path = root_dir / mod_str
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

@app.command()
def boot(kernel_path: Optional[Path] = typer.Argument(None), output: str = "text"):
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
                mod_data = load_jsonc(root_dir / mod_str)
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
                        torque = lim.get('torque_nm', 'N/A')
                        prompt += f"- {j}: Torque={torque}Nm\n"
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

# --- ENTRY POINT ---
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_header()
        log("Awaiting command input...", "WARN")
        print("\nTry: python src/cli.py compile-spec")
    else:
        if "-q" not in sys.argv and "--quiet" not in sys.argv and "--help" not in sys.argv:
            print_header()
        app()