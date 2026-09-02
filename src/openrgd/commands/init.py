"""Create a project from the packaged, reconciled OpenRGD default profile."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
import re
import shutil
from typing import Optional

import typer

from ..core.canonical import CanonicalIntegrityError, update_manifest_integrity
from ..core.config import state
from ..core.visuals import log, print_header, smart_track

_DID_RE = re.compile(r'"id":\s*"did:rgd:[^"]+"')


def _project_did(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "-")
    return f"did:rgd:{normalized}"


def init(
    name: Optional[str] = typer.Argument(None, help="Name of the robot project")
) -> None:
    """Clone the canonical default seed, personalize identity, and rehash it."""

    if not name:
        if state["quiet"]:
            log("Missing argument 'NAME' in quiet mode.", "ERROR")
            raise typer.Exit(1)
        print_header()
        name = typer.prompt("🤖 Project Name")

    target_dir = Path(name)
    if target_dir.exists():
        log(f"Directory '{name}' exists. Abort.", "ERROR")
        raise typer.Exit(1)

    log(f"Initializing containment field: {name}", "SYSTEM")

    if state["cinematic"]:
        import time

        domains = [
            "00_core",
            "01_foundation",
            "02_operation",
            "03_agency",
            "04_volition",
            "05_evolution",
            "06_ether",
        ]
        for _ in smart_track(domains, "[cyan]Injecting Neural Pathways...[/]"):
            time.sleep(0.1)

    try:
        packaged_seed = resources.files("openrgd") / "seeds" / "default"
        shutil.copytree(str(packaged_seed), target_dir)

        kernel_path = target_dir / "spec" / "00_core" / "kernel.jsonc"
        if not kernel_path.is_file():
            raise FileNotFoundError(f"packaged seed missing {kernel_path}")

        text = kernel_path.read_text(encoding="utf-8")
        did = _project_did(name)
        updated, count = _DID_RE.subn(f'"id": "{did}"', text, count=1)
        if count != 1:
            raise ValueError("kernel identity field could not be personalized exactly once")
        kernel_path.write_text(updated, encoding="utf-8", newline="\n")

        integrity = update_manifest_integrity(target_dir / "spec")
    except (CanonicalIntegrityError, FileNotFoundError, OSError, ValueError) as exc:
        shutil.rmtree(target_dir, ignore_errors=True)
        log(f"Project initialization failed: {exc}", "ERROR")
        raise typer.Exit(1) from exc

    log(f"Identity assigned: {did}", "DEBUG")
    log(f"Canonical source root: {integrity.computed}", "DEBUG")
    log("Kernel & Semantic Graph injected.", "SUCCESS")

    if not state["quiet"]:
        print(f"\n\033[1;32m» Project ready in ./{name}\033[0m")
        print(f"  Try: cd {name} && rgd hash && rgd check")
