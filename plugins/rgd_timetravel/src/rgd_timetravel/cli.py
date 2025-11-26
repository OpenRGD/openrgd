import datetime
from pathlib import Path
import os

import typer

app = typer.Typer(help="Time-travel tools for the OpenRGD Cognitive BIOS.")

SNAPSHOT_DIR_ENV = "RGD_TIMETRAVEL_SNAPSHOT_DIR"


def attach(root: typer.Typer) -> None:
    """
    Entry point for the RGD plugin system.

    After installation, the commands will be available as:
        rgd timetravel snapshot
        rgd timetravel list
    """
    root.add_typer(app, name="timetravel")


def _default_snapshot_dir() -> Path:
    base = os.getenv(SNAPSHOT_DIR_ENV)
    if base:
        return Path(base).expanduser().resolve()
    return Path(".rgd_snapshots").resolve()


@app.command("snapshot")
def snapshot(
    label: str = typer.Option(
        "",
        "--label",
        "-l",
        help="Optional human-readable label for this snapshot.",
    )
):
    """
    Create a new BIOS snapshot (demo version, just a marker file).
    """
    snap_dir = _default_snapshot_dir()
    snap_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_label = label.strip().replace(" ", "_") if label else "snapshot"
    filename = f"{timestamp}__{safe_label}.marker"

    path = snap_dir / filename
    path.write_text(
        f"# Snapshot marker\ncreated_at = {timestamp}\nlabel = {label}\n",
        encoding="utf-8",
    )

    typer.echo(f"[TimeTravel] Snapshot created: {path}")


@app.command("list")
def list_snapshots():
    """
    List known BIOS snapshots.
    """
    snap_dir = _default_snapshot_dir()
    if not snap_dir.exists():
        typer.echo("[TimeTravel] No snapshots found.")
        raise typer.Exit(0)

    files = sorted(snap_dir.glob("*.marker"))
    if not files:
        typer.echo("[TimeTravel] No snapshots found.")
        raise typer.Exit(0)

    typer.echo("[TimeTravel] Available snapshots:")
    for f in files:
        typer.echo(f"  - {f.name}")
