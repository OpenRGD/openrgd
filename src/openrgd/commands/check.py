"""Integrity-aware, non-actuating OpenRGD profile validation command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.profile import ProfileInspectionError, inspect_profile
from ..core.visuals import log


def check(
    kernel_path: Path | None = typer.Argument(
        None,
        help="Optional canonical kernel path (spec/00_core/kernel.jsonc).",
    ),
    output: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Result format: text or json.",
    ),
) -> None:
    """Validate source integrity and every kernel-selected JSONC module.

    This command validates a static profile. It does not assess hardware,
    runtime readiness or permission to actuate.
    """

    if output not in {"text", "json"}:
        log("--output must be 'text' or 'json'", "ERROR")
        raise typer.Exit(2)

    try:
        snapshot = inspect_profile(kernel_path)
    except ProfileInspectionError as exc:
        log(f"Profile validation failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    payload = snapshot.validation_payload()
    if output == "json":
        typer.echo(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
            )
        )
        return

    typer.echo("OPENRGD PROFILE VALIDATION")
    typer.echo("=" * 26)
    typer.echo(f"Status: {payload['status']}")
    typer.echo(f"Identity: {payload['robot_id']}")
    typer.echo(f"Source root: {payload['integrity']['computed']}")
    typer.echo(f"Kernel-selected modules: {payload['modules_count']}")
    typer.echo("Physical execution assessed: NO")
    typer.echo("Runtime readiness: NOT ASSESSED")
