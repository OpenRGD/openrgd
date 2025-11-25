import typer
import os
from pathlib import Path
from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats

app = typer.Typer()

@app.command("import")
def import_cmd(
    file_path: Path = typer.Argument(..., help="Source file (e.g. robot.urdf)"),
    output_dir: Path = typer.Option(None, "--out", "-o", help="Output directory")
):
    """
    Ingests external robot definitions and converts them to OpenRGD.
    Automatically detects format based on extension.
    """
    if not file_path.exists():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)

    # 1. Dynamic Resolution
    ext = file_path.suffix.lower()
    ImporterClass = get_importer_class(ext)
    
    if not ImporterClass:
        log(f"Unsupported format: {ext}", "ERROR")
        log(f"Supported formats: {', '.join(list_supported_formats())}", "INFO")
        raise typer.Exit(1)

    # 2. Instantiation
    log(f"Detected Module: {ImporterClass.__name__}", "SYSTEM")
    importer = ImporterClass(str(file_path))

    # 3. Execution (Polymorphic)
    try:
        rgd_data = importer.parse()
    except Exception as e:
        log(f"Critical Import Failure: {e}", "ERROR")
        raise typer.Exit(1)
    
    if not rgd_data:
        log("Import produced empty data structure.", "ERROR")
        raise typer.Exit(1)

    # 4. Write to Disk
    target_name = importer.robot_name
    if output_dir is None:
        output_dir = Path(target_name)
    
    if output_dir.exists():
        log(f"Target directory '{output_dir}' exists. Merging...", "WARN")
    else:
        output_dir.mkdir()

    log(f"Writing OpenRGD structure to: {output_dir}", "SYSTEM")
    
    # Scrittura con barra di caricamento per effetto scenico
    for rel_path, content in smart_track(rgd_data.items(), "[cyan]Transcribing DNA...[/]"):
        full_path = output_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    log("Import Complete. Welcome to the Hive Mind.", "SUCCESS")