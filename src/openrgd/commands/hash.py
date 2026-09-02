"""Canonical OpenRGD source-tree integrity command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.canonical import (
    CanonicalIntegrityError,
    compute_integrity,
    resolve_spec_dir,
    update_manifest_integrity,
)
from ..core.visuals import log


def bundle_hash(
    root_dir: Path = typer.Argument(
        Path("."), help="Project root or direct spec directory."
    ),
    write: bool = typer.Option(
        False, "--write", help="Write the current profile and root to manifest.jsonc."
    ),
    output_format: str = typer.Option(
        "text", "--output", help="Result format: text or json."
    ),
) -> None:
    """Compute or update the versioned canonical source-tree SHA-256 root."""

    if output_format not in {"text", "json"}:
        log("--output must be 'text' or 'json'", "ERROR")
        raise typer.Exit(2)

    try:
        spec_dir = resolve_spec_dir(root_dir)
        result = (
            update_manifest_integrity(spec_dir) if write else compute_integrity(spec_dir)
        )
    except (CanonicalIntegrityError, OSError, ValueError) as exc:
        log(f"Integrity operation failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    payload = result.as_dict()
    if output_format == "json":
        typer.echo(json.dumps(payload, sort_keys=True))
    else:
        typer.echo(f"profile:  {result.profile or 'MISSING'}")
        typer.echo(f"computed: {result.computed}")
        typer.echo(f"declared: {result.declared or 'MISSING'}")
        typer.echo(f"files:    {result.files_count}")
        typer.echo(f"status:   {'MATCH' if result.matches else 'MISMATCH'}")

    if not result.matches:
        raise typer.Exit(1)
