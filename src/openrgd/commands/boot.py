"""Deterministic, non-actuating OpenRGD grounding command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.profile import (
    ProfileInspectionError,
    build_grounding_context,
    inspect_profile,
    render_grounding_text,
)
from ..core.visuals import log


def boot(
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
    """Build an integrity-verified grounding context from selected modules.

    Boot is a deterministic profile-read operation. It does not initialize an
    embodied runtime, assess physical safety or authorize actuation.
    """

    if output not in {"text", "json"}:
        log("--output must be 'text' or 'json'", "ERROR")
        raise typer.Exit(2)

    try:
        snapshot = inspect_profile(kernel_path)
        context = build_grounding_context(snapshot)
    except ProfileInspectionError as exc:
        log(f"Grounding failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    if output == "json":
        typer.echo(
            json.dumps(
                context,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
            )
        )
        return

    typer.echo(render_grounding_text(context), nl=False)
