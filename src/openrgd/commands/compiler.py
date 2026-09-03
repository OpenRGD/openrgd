"""Deterministic OpenRGD machine-bundle compilation."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.canonical import (
    CanonicalIntegrityError,
    build_machine_bundle,
    resolve_spec_dir,
)
from ..core.visuals import log


def compile_spec(
    root_dir: Path = typer.Argument(
        Path("."), help="Project root or direct spec directory."
    ),
    output: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help=(
            "Generated machine bundle path. Defaults to "
            "<project>/spec/openrgd_unified_spec.json."
        ),
    ),
    output_format: str = typer.Option(
        "text", "--output", help="Result format: text or json."
    ),
) -> None:
    """Build one deterministic machine bundle from canonical source files."""

    if output_format not in {"text", "json"}:
        log("--output must be 'text' or 'json'", "ERROR")
        raise typer.Exit(2)

    try:
        spec_dir = resolve_spec_dir(root_dir)
        project_root = spec_dir.parent
        output_path = (output or spec_dir / "openrgd_unified_spec.json").resolve()
        result = build_machine_bundle(spec_dir, output_path)
    except (CanonicalIntegrityError, OSError, ValueError) as exc:
        log(f"Compilation failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(json.dumps(result, sort_keys=True))
        return

    rendered_output: str
    try:
        rendered_output = str(Path(result["output_path"]).relative_to(project_root))
    except ValueError:
        rendered_output = result["output_path"]
    log(f"Canonical machine bundle generated: {rendered_output}", "SUCCESS")
    log(f"Source root: {result['bundle_integrity_hash']}", "SUCCESS")
    log(f"Output SHA-256: {result['output_sha256']}", "SUCCESS")
