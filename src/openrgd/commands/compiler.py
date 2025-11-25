import json
import time
from pathlib import Path
from datetime import datetime
import typer
from ..core.utils import load_jsonc, strip_jsonc
from ..core.visuals import log, smart_track
from ..core.config import state

app = typer.Typer()

def indent_block(text: str, indent_str: str = "      ") -> str:
    """Indents a block of text to fit inside a JSON structure."""
    lines = text.split('\n')
    return "\n".join([f"{indent_str}{line}" if line.strip() else line for line in lines])

@app.command("compile-spec")
def compile_spec(
    root_dir: Path = typer.Argument(Path("."), help="Project root directory containing 'spec' folder"),
    output_base: str = typer.Option("openrgd_unified_spec", "--name", "-n", help="Base name for output files")
):
    """
    Builds the Unified Specification Document (Twins).
    - .jsonc (Human): Constructed manually to PRESERVE original comments.
    - .json (Machine): Clean parsed data for tools.
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
            # 1. READ RAW (The Soul with Comments)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read().strip()
            
            # 2. PARSE CLEAN (The Body for Validation)
            clean_content = json.loads(strip_jsonc(raw_text), strict=False)
            
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
                "raw_content": raw_text,      # CRITICAL: Contains comments
                "parsed_content": clean_content 
            })
        except Exception as e:
            log(f"Skipping {file_path.name}: {e}", "WARN")

    # Sort
    records.sort(key=lambda x: (x["weight"], x["id"]))
    
    # --- 1. GENERATE MACHINE TWIN (.json) ---
    # Standard JSON dump (comments stripped automatically by parser above)
    machine_files = []
    for r in records:
        machine_files.append({
            "path": r["path"],
            "id": r["id"],
            "domain": r["domain"],
            "content": r["parsed_content"]
        })
    
    machine_doc = {
        "meta": {
            "standard": "OpenRGD",
            "type": "MACHINE_TWIN_CLEAN",
            "version": "0.1.0",
            "generated_at": datetime.now().isoformat(),
            "note": "Strict JSON for tooling."
        },
        "files": machine_files
    }
    
    path_j = spec_dir / f"{output_base}.json"
    with open(path_j, "w", encoding="utf-8") as f:
        json.dump(machine_doc, f, indent=2)
    log(f"Machine Twin generated: {path_j.name}", "SUCCESS")

    # --- 2. GENERATE HUMAN TWIN (.jsonc) ---
    # Manual string construction to preserve comments
    
    log("Weaving Human Twin (Preserving Comments)...", "DEBUG")
    
    # Header
    jsonc_lines = []
    jsonc_lines.append("// ======================================================================")
    jsonc_lines.append("// OPENRGD — UNIFIED SPECIFICATION (HUMAN TWIN)")
    jsonc_lines.append("// ----------------------------------------------------------------------")
    jsonc_lines.append(f"// Generated at: {datetime.now().isoformat()}")
    jsonc_lines.append("// This file contains the raw source code of all modules, comments included.")
    jsonc_lines.append("// ======================================================================")
    jsonc_lines.append("")
    jsonc_lines.append("{")
    
    # Meta Block
    jsonc_lines.append('  "meta": {')
    jsonc_lines.append('    "standard": "OpenRGD",')
    jsonc_lines.append('    "type": "HUMAN_TWIN_WITH_COMMENTS",')
    jsonc_lines.append('    "version": "0.1.0"')
    jsonc_lines.append('  },')
    
    # Files Block
    jsonc_lines.append('  "files": [')
    
    total = len(records)
    for i, r in enumerate(records):
        # Wrapper Object Start
        jsonc_lines.append('    {')
        jsonc_lines.append(f'      "path": "{r["path"]}",')
        jsonc_lines.append(f'      "id": "{r["id"]}",')
        jsonc_lines.append(f'      "domain": "{r["domain"]}",')
        
        # Content Injection
        jsonc_lines.append('      "content": ')
        # Here we inject the raw text directly. 
        # We assume the raw text starts with a valid JSON object/comment.
        # We indent it to fit the structure visually.
        indented_raw = indent_block(r["raw_content"], indent_str="      ")
        jsonc_lines.append(indented_raw)
        
        # Wrapper Object End
        if i < total - 1:
            jsonc_lines.append('    },')
        else:
            jsonc_lines.append('    }') # No comma for last item
            
    jsonc_lines.append('  ]')
    jsonc_lines.append('}')
    
    # Write File
    path_c = spec_dir / f"{output_base}.jsonc"
    with open(path_c, "w", encoding="utf-8") as f:
        f.write("\n".join(jsonc_lines))
        
    log(f"Human Twin generated: {path_c.name}", "SUCCESS")