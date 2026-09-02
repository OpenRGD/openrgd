from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.canonical import CanonicalIntegrityError, resolve_spec_dir
from ..core.visuals import log
from ..synapses import (
    SynapseGenerationError,
    get_synapse,
    list_synapse_targets,
    unavailable_reason,
)


def export(
    target: str = typer.Argument(
        ...,
        help="Static interoperability target (currently: ros2).",
    ),
    root_dir: Path = typer.Option(
        Path("."),
        "--root",
        help="OpenRGD project root or direct spec directory.",
    ),
    output_dir: Path = typer.Option(
        Path("export"),
        "--out",
        "-o",
        help="Generated output directory, relative to the project root by default.",
    ),
    output_format: str = typer.Option(
        "text",
        "--output",
        help="Result format: text or json.",
    ),
) -> None:
    """Generate non-actuating static interoperability artifacts."""

    if output_format not in {"text", "json"}:
        log("--output must be 'text' or 'json'", "ERROR")
        raise typer.Exit(2)

    normalized_target = target.lower()
    synapse_class = get_synapse(normalized_target)
    if synapse_class is None:
        reason = unavailable_reason(normalized_target)
        if reason:
            log(f"Target '{target}' is unavailable: {reason}", "ERROR")
        else:
            available = ", ".join(list_synapse_targets()) or "none"
            log(
                f"Unknown target '{target}'. Available static targets: {available}",
                "ERROR",
            )
        raise typer.Exit(2)

    try:
        spec_dir = resolve_spec_dir(root_dir)
        project_root = spec_dir.parent
        destination = (
            output_dir.resolve()
            if output_dir.is_absolute()
            else (project_root / output_dir).resolve()
        )
        if destination == project_root:
            raise SynapseGenerationError(
                "export destination must be a dedicated directory, not the project root"
            )
        if destination == spec_dir or spec_dir in destination.parents:
            raise SynapseGenerationError(
                "export destination cannot be the canonical spec directory or its child"
            )

        synapse = synapse_class(spec_dir=spec_dir)
        result = synapse.generate(destination)
    except (
        CanonicalIntegrityError,
        SynapseGenerationError,
        FileNotFoundError,
        OSError,
        ValueError,
    ) as exc:
        log(f"Static export failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return

    log(
        f"Static {normalized_target.upper()} export: {result['status']}",
        "SUCCESS",
    )
    log(f"Output directory: {result['output_dir']}", "SUCCESS")
    for path in result["generated_files"]:
        log(f"Generated: {path}", "SUCCESS")
