"""Merge imported robot evidence with a reviewed OpenRGD seed profile."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import time

import typer

from ..core.alive import alive_rgd_spec, write_manifest, write_readme
from ..core.canonical import CanonicalIntegrityError, update_manifest_integrity
from ..core.config import state
from ..core.utils import load_jsonc
from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats


def _safe_relative_path(raw: str) -> Path:
    normalized = raw.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe generated path: {raw!r}")
    if path.parts[0] == "spec":
        path = PurePosixPath(*path.parts[1:])
    if not path.parts:
        raise ValueError(f"empty generated path: {raw!r}")
    return Path(*path.parts)


def alive_cmd(
    file_path: Path = typer.Argument(
        ...,
        help="Robot description file (URDF, XML, ASCII USD or USDA).",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Output RGD project directory.",
    ),
    seed: str = typer.Option(
        "default",
        "--seed",
        help="Packaged seed profile used to enrich imported evidence.",
    ),
) -> None:
    """Create a full profile from imported evidence plus a reviewed seed."""

    if not file_path.is_file():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)

    importer_class = get_importer_class(file_path.suffix.lower())
    if importer_class is None:
        supported = ", ".join(list_supported_formats())
        log(f"Unsupported format: {file_path.suffix}; supported: {supported}", "ERROR")
        raise typer.Exit(1)

    importer = importer_class(str(file_path))
    try:
        base_spec = importer.parse()
        if not base_spec:
            raise ValueError("importer returned no evidence")
        full_spec = alive_rgd_spec(
            base_spec=base_spec,
            robot_name=importer.robot_name,
            seed_name=seed,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        log(f"Profile enrichment failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    rgd_root = output_dir or Path("my-robots") / f"RGD-{importer.robot_name}"
    spec_dir = rgd_root / "spec"
    rgd_root.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    if state.get("cinematic", True):
        present = sorted(
            {
                PurePosixPath(path.removeprefix("spec/")).parts[0]
                for path in full_spec
                if PurePosixPath(path.removeprefix("spec/")).parts
            }
        )
        for domain in smart_track(present, "[cyan]Enriching profile...[/]"):
            log(f"[{domain}] profile materialized", "DEBUG")
            time.sleep(0.04)

    try:
        for raw_path, content in full_spec.items():
            relative = _safe_relative_path(raw_path)
            target = spec_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")

        integrity = update_manifest_integrity(spec_dir)
        manifest = load_jsonc(spec_dir / "manifest.jsonc")
        standard_version = manifest["meta_group"][
            "rgd_standard_version_semver_str"
        ]
        write_manifest(
            rgd_root,
            robot_name=importer.robot_name,
            standard_version=standard_version,
        )
        write_readme(
            rgd_root,
            robot_name=importer.robot_name,
            standard_version=standard_version,
        )
    except (
        CanonicalIntegrityError,
        FileNotFoundError,
        KeyError,
        OSError,
        ValueError,
    ) as exc:
        log(f"Profile write failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    log(f"OpenRGD profile written to: {rgd_root}", "SUCCESS")
    log(f"Canonical source root: {integrity.computed}", "SUCCESS")
