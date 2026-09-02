"""Strict-JSON compatibility mirror generation."""

from __future__ import annotations

from pathlib import Path

import typer

from ..core.canonical import (
    CanonicalIntegrityError,
    build_standard_mirror,
    resolve_spec_dir,
)
from ..core.visuals import log


def build_standard(
    src_dir: Path = typer.Option(
        Path("."), "--src", help="Project root or source spec directory."
    ),
    dest_dir: Path | None = typer.Option(
        None,
        "--dest",
        help="Destination directory. Defaults to <project>/standard.",
    ),
) -> None:
    """Build a deterministic strict-JSON mirror of canonical source files."""

    try:
        spec_dir = resolve_spec_dir(src_dir)
        destination = (dest_dir or spec_dir.parent / "standard").resolve()
        processed = build_standard_mirror(spec_dir, destination)
    except (CanonicalIntegrityError, OSError, ValueError) as exc:
        log(f"Standard build failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    log(
        f"Standard mirror complete: {processed} canonical files -> {destination}",
        "SUCCESS",
    )
