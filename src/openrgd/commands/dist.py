import json
import shutil
from pathlib import Path
import typer
from ..core.utils import strip_jsonc
from ..core.visuals import log, smart_track
from ..core.config import state

app = typer.Typer()

@app.command("build-standard")
def build_standard(
    src_dir: Path = typer.Option(Path("spec"), "--src", help="Source directory (JSONC)"),
    dest_dir: Path = typer.Option(Path("standard"), "--dest", help="Destination directory (JSON)")
):
    """
    Transpiles the 'spec' folder (JSONC) into a clean 'standard' folder (JSON).
    Removes comments and validating syntax for machine consumption.
    """
    log(f"Initializing Standard Build: {src_dir} -> {dest_dir}", "SYSTEM")

    if not src_dir.exists():
        log(f"Source directory '{src_dir}' not found.", "ERROR")
        raise typer.Exit(1)

    # 1. Clean / Create Destination
    if dest_dir.exists():
        log("Cleaning existing standard folder...", "DEBUG")
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    # 2. Walk and Transpile
    files = list(src_dir.rglob("*"))
    processed_count = 0
    
    for src_file in smart_track(files, "[cyan]Building Standard...[/]"):
        if src_file.is_dir():
            continue
            
        # Calcola il percorso relativo per specchiare la struttura
        rel_path = src_file.relative_to(src_dir)
        dest_file = dest_dir / rel_path
        
        # Assicura che la cartella di destinazione esista
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Logica di conversione
        if src_file.suffix == ".jsonc":
            # Caso JSONC: Pulisci e salva come .json
            try:
                with open(src_file, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                # Rimuovi commenti
                clean_json_str = strip_jsonc(raw_content)
                
                # Valida che sia JSON valido
                json_obj = json.loads(clean_json_str)
                
                # Cambia estensione in .json
                dest_file = dest_file.with_suffix(".json")
                
                with open(dest_file, 'w', encoding='utf-8') as f:
                    json.dump(json_obj, f, indent=2)
                    
                processed_count += 1
                
            except json.JSONDecodeError as e:
                log(f"Invalid JSONC in {src_file.name}: {e}", "ERROR")
                # Non interrompiamo il processo, ma segnaliamo l'errore
                
        else:
            # Altri file (md, txt, immagini): Copia semplice
            shutil.copy2(src_file, dest_file)

    log(f"Build Complete. {processed_count} files transpiled to '{dest_dir}/'", "SUCCESS")