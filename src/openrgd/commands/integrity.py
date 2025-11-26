"""
OpenRGD Integrity Module

This module provides verification tools to check whether the unified
specification files have been modified, corrupted, or tampered with.

It compares freshly regenerated unified outputs (from /spec and /standard)
against trusted benchmark snapshots stored under /standard/benchmarks.
"""

import json
from pathlib import Path

import typer

from ..core.visuals import log
from ..core.spec_unifier import (
    scan_spec_records,
    generate_human_unified_from_records,
    generate_machine_unified_from_standard,
    normalize_human_jsonc,
)

# Typer app for this command group (plugin)
app = typer.Typer(help="Integrity and tamper-detection tools for OpenRGD.")

PLUGIN_NAME = "integrity"


def _normalize_machine_json(doc: dict) -> dict:
    """
    Normalize a Machine Twin JSON document for integrity comparison.

    - Removes volatile metadata such as "generated_at"
    - Keeps all semantic content intact

    This allows deterministic comparison between regenerated and benchmark
    Machine Twin documents, even if they were created at different times.
    """
    if not isinstance(doc, dict):
        return doc

    meta = dict(doc.get("meta", {}))
    meta.pop("generated_at", None)

    normalized = dict(doc)
    normalized["meta"] = meta
    return normalized


@app.command("check")
def check_integrity(
    root_dir: Path = typer.Argument(
        Path("."),
        help="Project root directory containing 'spec' and 'standard'.",
    ),
    output_base: str = typer.Option(
        "openrgd_unified_spec",
        "--name",
        "-n",
        help="Base name for unified spec benchmark files.",
    ),
):
    """
    Verify the integrity of the unified specification.

    The command:
    1. Rebuilds the Human Twin (JSONC) from /spec and compares it against the
       benchmark JSONC snapshot stored under /standard/benchmarks.
    2. Rebuilds the Machine Twin (JSON) from /standard and compares it against
       the benchmark JSON snapshot, ignoring volatile metadata such as timestamps.

    If any mismatch is detected, the integrity check fails with a non-zero exit code.
    """
    spec_dir = root_dir / "spec"
    standard_dir = root_dir / "standard"
    benchmark_dir = standard_dir / "benchmarks"

    if not spec_dir.exists() or not standard_dir.exists():
        log("Missing 'spec' or 'standard' directories.", "ERROR")
        raise typer.Exit(1)

    bench_jsonc = benchmark_dir / f"{output_base}.jsonc"
    bench_json = benchmark_dir / f"{output_base}.json"

    if not bench_jsonc.exists() or not bench_json.exists():
        log("Benchmark files not found. Run 'rgd spec compile-spec --def' first.", "ERROR")
        raise typer.Exit(1)

    log("Running integrity check for Unified Spec...", "SYSTEM")

    # ============================================================
    # 1) Rebuild Human Twin (JSONC) from /spec and compare
    # ============================================================

    records = scan_spec_records(root_dir, spec_dir)
    generate_human_unified_from_records(records, spec_dir, output_base)

    current_jsonc_path = spec_dir / f"{output_base}.jsonc"
    current_jsonc_text = current_jsonc_path.read_text(encoding="utf-8")
    bench_jsonc_text = bench_jsonc.read_text(encoding="utf-8")

    current_jsonc_norm = normalize_human_jsonc(current_jsonc_text)
    bench_jsonc_norm = normalize_human_jsonc(bench_jsonc_text)

    jsonc_match = (current_jsonc_norm == bench_jsonc_norm)

    if jsonc_match:
        log("JSONC (Human Twin) integrity: OK", "SUCCESS")
    else:
        log("JSONC (Human Twin) integrity: MISMATCH", "ERROR")

    # ============================================================
    # 2) Rebuild Machine Twin (JSON) from /standard and compare
    # ============================================================

    generate_machine_unified_from_standard(root_dir, standard_dir, output_base)
    current_json_path = standard_dir / f"{output_base}.json"

    with current_json_path.open("r", encoding="utf-8") as f:
        current_json = json.load(f)
    with bench_json.open("r", encoding="utf-8") as f:
        bench_json_obj = json.load(f)

    current_json_norm = _normalize_machine_json(current_json)
    bench_json_norm = _normalize_machine_json(bench_json_obj)

    json_match = (current_json_norm == bench_json_norm)

    if json_match:
        log("JSON (Machine Twin) integrity: OK", "SUCCESS")
    else:
        log("JSON (Machine Twin) integrity: MISMATCH", "ERROR")

    # ============================================================
    # 3) Final verdict
    # ============================================================

    if jsonc_match and json_match:
        log("Unified Spec integrity check PASSED.", "SUCCESS")
        raise typer.Exit(0)
    else:
        log("Unified Spec integrity check FAILED.", "ERROR")
        raise typer.Exit(1)


def attach(root: typer.Typer) -> None:
    """
    Attach this command group to the root CLI.

    This will expose the integrity tools under:
        rgd integrity check
    """
    root.add_typer(app, name="integrity")
