"""High-level OpenRGD 'bring this robot alive' workflow."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import time

import typer

from ..core.alive import alive_rgd_spec, write_manifest, write_readme
from ..core.canonical import CanonicalIntegrityError, build_machine_bundle, update_manifest_integrity
from ..core.config import state
from ..core.profile import ProfileInspectionError, build_grounding_context, inspect_profile
from ..core.utils import load_jsonc
from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats
from ..synapses import ROS2Synapse, SynapseGenerationError


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


def _alive_step(label: str, message: str) -> None:
    if state.get("quiet", False):
        return
    log(f"{label} {message}", "SYSTEM")
    if state.get("cinematic", True):
        time.sleep(0.08)


def alive_cmd(
    file_path: Path = typer.Argument(..., help="Robot description file (URDF, XML, ASCII USD or USDA)."),
    output_dir: Path | None = typer.Option(None, "--out", "-o", help="Output RGD project directory."),
    seed: str = typer.Option("default", "--seed", help="Packaged seed profile used to enrich imported evidence."),
    static_export: bool = typer.Option(True, "--static-export/--no-static-export", help="Generate the available static interoperability output after compilation."),
) -> None:
    """Bring a robot alive from one source file.

    Extract source evidence, enrich it with a selected seed, compute canonical
    integrity, validate and ground the profile, compile the deterministic
    machine bundle, and optionally generate static ROS 2 interoperability.

    This creates an inspectable embodiment profile. It does not certify the
    body for physical use or start an embodied runtime.
    """
    if not file_path.is_file():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)
    importer_class = get_importer_class(file_path.suffix.lower())
    if importer_class is None:
        supported = ", ".join(list_supported_formats())
        log(f"Unsupported format: {file_path.suffix}; supported: {supported}", "ERROR")
        raise typer.Exit(1)
    importer = importer_class(str(file_path))
    rgd_root = output_dir or Path("my-robots") / f"RGD-{importer.robot_name}"
    spec_dir = rgd_root / "spec"
    artifacts_dir = rgd_root / "artifacts"
    try:
        _alive_step("①", f"Understanding {file_path.name}")
        base_spec = importer.parse()
        if not base_spec:
            raise ValueError("importer returned no evidence")
        source_artifact = importer.source_artifact(file_path.suffix.lower().lstrip(".") or "UNKNOWN")
        _alive_step("②", f"Building the body model for {importer.robot_name}")
        full_spec = alive_rgd_spec(base_spec=base_spec, robot_name=importer.robot_name, seed_name=seed)
        rgd_root.mkdir(parents=True, exist_ok=True)
        spec_dir.mkdir(parents=True, exist_ok=True)
        for raw_path, content in smart_track(full_spec.items(), "[cyan]Materializing OpenRGD profile...[/]"):
            relative = _safe_relative_path(raw_path)
            target = spec_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        _alive_step("③", "Sealing canonical integrity")
        integrity = update_manifest_integrity(spec_dir)
        manifest = load_jsonc(spec_dir / "manifest.jsonc")
        standard_version = manifest["meta_group"]["rgd_standard_version_semver_str"]
        write_manifest(rgd_root, robot_name=importer.robot_name, standard_version=standard_version, seed_name=seed, source_artifact=source_artifact)
        write_readme(rgd_root, robot_name=importer.robot_name, standard_version=standard_version, seed_name=seed)
        _alive_step("④", "Checking the profile")
        snapshot = inspect_profile(spec_dir / "00_core" / "kernel.jsonc")
        _alive_step("⑤", "Building the grounding context")
        grounding = build_grounding_context(snapshot)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        grounding_path = artifacts_dir / "grounding_context.json"
        grounding_path.write_text(json.dumps(grounding, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        _alive_step("⑥", "Compiling the machine bundle")
        bundle_result = build_machine_bundle(spec_dir, spec_dir / "openrgd_unified_spec.json")
        export_result = None
        if static_export:
            _alive_step("⑦", "Preparing the static ROS 2 bridge")
            export_result = ROS2Synapse(spec_dir=spec_dir).generate(rgd_root / "export" / "ros2")
    except (CanonicalIntegrityError, ProfileInspectionError, SynapseGenerationError, FileNotFoundError, KeyError, OSError, ValueError) as exc:
        log(f"Alive workflow failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc
    log("Robot is alive in OpenRGD. ✨", "SUCCESS")
    log(f"Profile: {rgd_root}", "SUCCESS")
    log(f"Canonical root: {integrity.computed}", "SUCCESS")
    log(f"Grounding: {grounding_path}", "SUCCESS")
    log(f"Machine bundle: {bundle_result['output_path']}", "SUCCESS")
    if export_result is not None:
        log(f"ROS 2 static bridge: {export_result['status']} → {export_result['output_dir']}", "SUCCESS")
    log("Physical actuation still requires a compatible embodied runtime and explicit hardware review.", "WARN")
