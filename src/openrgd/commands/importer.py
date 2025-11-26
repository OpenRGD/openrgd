import typer
from pathlib import Path

from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats

app = typer.Typer()

@app.command("import")
def import_cmd(
    file_path: Path = typer.Argument(
        ...,
        help="Path to the robot description file (auto-detected format: .urdf, .xml, .usd, .usda)."
    ),
    output_dir: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="RGD root for the generated structure (defaults to RGD-<robot_name>).",
    ),
):
    """
    Import a robot description and convert it into an OpenRGD-compatible structure.

    The importer is selected automatically based on the file extension.

    Supported formats (v0.1.0):
        • URDF (.urdf, .xml)
        • USD  (.usd, .usda)

    The importer produces a directory tree under:

        RGD-<robot_name>/spec/

    ready for further compilation via `rgd compile-spec` or bundling.
    """
    if not file_path.exists():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)

    # 1. Dynamic Resolution (extension -> Importer)
    ext = file_path.suffix.lower()
    ImporterClass = get_importer_class(ext)

    if not ImporterClass:
        supported = ", ".join(list_supported_formats())
        log(f"Unsupported format: {ext}", "ERROR")
        log(f"Supported formats in v0.1.0: {supported}", "INFO")
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

    # 4. RGD root & spec dir
    target_name = importer.robot_name

    if output_dir is None:
        rgd_root = Path(f"RGD-{target_name}")
    else:
        rgd_root = Path(output_dir)

    spec_dir = rgd_root / "spec"

    if rgd_root.exists():
        log(f"Target RGD root '{rgd_root}' exists. Merging...", "WARN")
    else:
        rgd_root.mkdir()

    spec_dir.mkdir(parents=True, exist_ok=True)

    log(f"Writing OpenRGD structure to: {spec_dir}", "SYSTEM")

    # 5. Scrittura sotto spec/ con effetto scenico
    for rel_path, content in smart_track(rgd_data.items(), "[cyan]Transcribing DNA...[/]"):
        full_path = spec_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    log("Import Complete. Welcome to the Hive Mind.", "SUCCESS")
