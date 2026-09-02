from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
import json
from pathlib import Path
from typing import Any

from ..core.canonical import compute_integrity
from ..core.utils import load_jsonc


class SynapseGenerationError(RuntimeError):
    """Raised when a static interoperability artifact cannot be generated safely."""


class BaseSynapse(ABC):
    """Base class for non-actuating, file-generating OpenRGD Synapses."""

    target_name = "unknown"

    def __init__(self, spec_dir: Path):
        self.spec_dir = spec_dir.resolve()
        kernel_path = self.spec_dir / "00_core" / "kernel.jsonc"
        if not kernel_path.is_file():
            raise SynapseGenerationError(
                f"kernel not found under specification root: {kernel_path}"
            )
        self.kernel = load_jsonc(kernel_path)
        self.robot_id = self.kernel.get("meta_group", {}).get("id", "unknown")

    def load_machine_bundle(self) -> tuple[dict[str, Any], str]:
        """Load and verify the deterministic machine bundle before export."""

        integrity = compute_integrity(self.spec_dir)
        if not integrity.matches:
            raise SynapseGenerationError(
                "canonical source root does not match manifest; "
                "run 'rgd hash --write' before exporting"
            )

        bundle_path = self.spec_dir / "openrgd_unified_spec.json"
        if not bundle_path.is_file():
            raise SynapseGenerationError(
                "machine bundle not found; run 'rgd compile-spec' first"
            )

        try:
            payload = bundle_path.read_bytes()
            bundle = json.loads(payload.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SynapseGenerationError(
                f"cannot read machine bundle: {exc}"
            ) from exc

        meta = bundle.get("meta", {}) if isinstance(bundle, dict) else {}
        if meta.get("bundle_integrity_hash") != integrity.computed:
            raise SynapseGenerationError(
                "machine bundle is stale or belongs to another source tree; "
                "run 'rgd compile-spec' again"
            )
        if not isinstance(bundle.get("files"), list):
            raise SynapseGenerationError("machine bundle has no files list")

        return bundle, hashlib.sha256(payload).hexdigest()

    @staticmethod
    def module_content(
        bundle: dict[str, Any],
        module_id: str,
        *,
        required: bool = False,
    ) -> dict[str, Any]:
        matches = [
            item.get("content")
            for item in bundle.get("files", [])
            if item.get("id") == module_id and isinstance(item.get("content"), dict)
        ]
        if len(matches) > 1:
            raise SynapseGenerationError(
                f"machine bundle contains duplicate module id: {module_id}"
            )
        if not matches:
            if required:
                raise SynapseGenerationError(
                    f"machine bundle is missing required module: {module_id}"
                )
            return {}
        return matches[0]

    @abstractmethod
    def generate(self, output_dir: Path) -> dict[str, Any]:
        """Materialize deterministic, non-actuating interoperability files."""

    def log(self, msg: str) -> None:
        print(f"  [SYNAPSE:{self.__class__.__name__}] {msg}")
