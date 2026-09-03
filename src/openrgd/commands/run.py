"""Fail-closed compatibility boundary for the historical ``rgd run`` CLI.

The canonical OpenRGD repository defines standards, contracts and reference
 tooling. It intentionally does not ship a physical embodied runtime. The old
ROS 2 / Viam prototype is preserved under ``docs/history/runtime-prototype``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

app = typer.Typer(
    help=(
        "Compatibility status for the external embodied-runtime boundary. "
        "This package does not actuate hardware."
    ),
    no_args_is_help=True,
)

_RUNTIME_STATUS: dict[str, Any] = {
    "schema_version": "1.0.0",
    "component": "embodied-runtime",
    "canonical_root": "OpenRGD/openrgd",
    "status": "NOT_PROVIDED_BY_CANONICAL_ROOT",
    "historical_prototype": "QUARANTINED",
    "physical_actuation_available": False,
    "contract_package": "contracts/agent/v0.1.0",
    "implementation_repository": None,
    "repository_name_decision": "OPEN",
    "decision_ref": "docs/reconciliation/RUNTIME_BOUNDARY.md",
}


def _validate_output(output: str) -> str:
    normalized = output.strip().lower()
    if normalized not in {"text", "json"}:
        raise typer.BadParameter("output must be 'text' or 'json'")
    return normalized


def _emit(payload: dict[str, Any], output: str, *, error: bool = False) -> None:
    mode = _validate_output(output)
    if mode == "json":
        typer.echo(json.dumps(payload, sort_keys=True), err=error)
        return

    typer.echo(f"Embodied runtime: {payload['status']}", err=error)
    typer.echo(
        "Physical actuation in canonical toolchain: "
        + ("available" if payload["physical_actuation_available"] else "disabled"),
        err=error,
    )
    typer.echo(
        f"Historical bundled prototype: {payload['historical_prototype']}",
        err=error,
    )
    typer.echo(f"Contract package: {payload['contract_package']}", err=error)
    typer.echo(
        "Use a separately versioned embodied runtime after its repository and "
        "contracts have been reconciled.",
        err=error,
    )


def _fail_closed(adapter: str, output: str, **context: Any) -> None:
    payload = {
        **_RUNTIME_STATUS,
        "requested_adapter": adapter,
        "outcome": "BLOCKED",
        "reason": "HISTORICAL_RUNTIME_QUARANTINED",
        **context,
    }
    _emit(payload, output, error=True)
    raise typer.Exit(code=2)


@app.command("status")
def runtime_status(
    output: str = typer.Option(
        "text", "--output", "-o", help="Output format: text or json"
    ),
) -> None:
    """Report the non-actuating embodied-runtime ownership boundary."""

    _emit(dict(_RUNTIME_STATUS), output)


@app.command("ros2")
def run_ros2(
    kernel_path: Path = typer.Option(
        Path("spec/00_core/kernel.jsonc"),
        "--kernel",
        "-k",
        help="Retained compatibility option; no runtime is started.",
    ),
    output: str = typer.Option(
        "text", "--output", "-o", help="Output format: text or json"
    ),
) -> None:
    """Fail closed; the historical ROS 2 runtime is quarantined."""

    _fail_closed("ros2", output, requested_kernel=str(kernel_path))


@app.command("viam")
def run_viam(
    output: str = typer.Option(
        "text", "--output", "-o", help="Output format: text or json"
    ),
) -> None:
    """Fail closed; the historical Viam runtime is quarantined."""

    _fail_closed("viam", output)


@app.command("hybrid")
def run_hybrid(
    output: str = typer.Option(
        "text", "--output", "-o", help="Output format: text or json"
    ),
) -> None:
    """Fail closed; the historical hybrid runtime was never implemented."""

    _fail_closed("hybrid", output)
