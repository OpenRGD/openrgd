from __future__ import annotations

from pathlib import Path, PurePosixPath

import typer

from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats

app = typer.Typer()


def _normalize_spec_relative_path(raw_path: str) -> Path:
    """Return a safe path relative to one OpenRGD ``spec/`` root.

    Historical importers returned both ``spec/foo`` and ``foo`` keys. The CLI
    accepts either form, strips exactly one optional spec prefix and rejects
    absolute or parent-traversal paths.
    """

    normalized = str(raw_path).replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("spec/"):
        normalized = normalized[len("spec/") :]

    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise ValueError(f"unsafe importer output path: {raw_path!r}")
    if path.parts[0] == "spec":
        raise ValueError(f"nested spec root is not allowed: {raw_path!r}")

    return Path(*path.parts)


@app.command("import")
def import_cmd(
    file_path: Path = typer.Argument(
        ...,
        help=(
            "Path to the robot description file "
            "(auto-detected format: .urdf, .xml, .usd, .usda)."
        ),
    ),
    output_dir: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="RGD root for the generated partial structure (default: RGD-<name>).",
    ),
) -> None:
    """Import source-supported facts into a partial OpenRGD specification.

    This command does not invent missing constitutional, safety or cognitive
    domains. Use ``rgd alive`` when a partial import should be merged with the
    reviewed packaged default seed.
    """

    if not file_path.exists():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)

    extension = file_path.suffix.lower()
    importer_class = get_importer_class(extension)
    if not importer_class:
        supported = ", ".join(list_supported_formats())
        log(f"Unsupported format: {extension}", "ERROR")
        log(f"Supported formats in v0.1.0: {supported}", "INFO")
        raise typer.Exit(1)

    log(f"Detected Module: {importer_class.__name__}", "SYSTEM")
    importer = importer_class(str(file_path))

    try:
        rgd_data = importer.parse()
    except Exception as exc:
        log(f"Critical Import Failure: {exc}", "ERROR")
        raise typer.Exit(1)

    if not rgd_data:
        log("Import produced empty data structure.", "ERROR")
        raise typer.Exit(1)

    robot_name = importer.robot_name
    rgd_root = Path(f"RGD-{robot_name}") if output_dir is None else Path(output_dir)
    spec_dir = rgd_root / "spec"

    if rgd_root.exists():
        log(f"Target RGD root '{rgd_root}' exists. Merging...", "WARN")
    else:
        rgd_root.mkdir(parents=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    log(f"Writing partial OpenRGD structure to: {spec_dir}", "SYSTEM")

    try:
        normalized_items = [
            (_normalize_spec_relative_path(rel_path), content)
            for rel_path, content in rgd_data.items()
        ]
    except (TypeError, ValueError) as exc:
        log(f"Importer emitted an invalid path: {exc}", "ERROR")
        raise typer.Exit(1)

    for rel_path, content in smart_track(
        normalized_items,
        "[cyan]Transcribing imported evidence...[/]",
    ):
        if not isinstance(content, str):
            log(f"Importer output for '{rel_path}' is not text.", "ERROR")
            raise typer.Exit(1)

        full_path = spec_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    log("Partial import complete. Use 'rgd alive' for seed convergence.", "SUCCESS")
