#!/usr/bin/env python3
"""Validate the declared canonical source root and active-artifact cleanup."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from openrgd.core.canonical import (
    INTEGRITY_PROFILE,
    CanonicalIntegrityError,
    compute_integrity,
)

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ACTIVE_PATHS = (
    "RGD-ur5",
    "example",
    "export",
    "msix",
    "my-robots",
    "package.json",
    "requirements.txt",
    "src/cli.py",
    "src/openrgd/commands/integrity.py",
    "src/openrgd/core/spec_unifier.py",
    "tools/generate_requirements",
    "tools/spec-builder",
    "spec/01_spec.jsonc",
    "spec/02_spec.jsonc",
    "spec/03_spec.jsonc",
    "spec/04_spec.jsonc",
    "spec/05_spec.jsonc",
    "spec/06_spec.jsonc",
    "spec/openrgd_unified_spec.json",
    "spec/openrgd_unified_spec.jsonc",
    "spec/openrgd_unified_spec_document.jsonc",
    "standard/01_spec.json",
    "standard/02_spec.json",
    "standard/03_spec.json",
    "standard/04_spec.json",
    "standard/05_spec.json",
    "standard/06_spec.json",
    "standard/openrgd_unified_spec.json",
    "standard/benchmarks",
)


def main() -> int:
    try:
        present = [path for path in FORBIDDEN_ACTIVE_PATHS if (ROOT / path).exists()]
        if present:
            raise CanonicalIntegrityError(
                "generated, duplicate or quarantined paths remain active: "
                + ", ".join(present)
            )

        history = ROOT / "docs/history/generated-artifacts/INVENTORY.json"
        if not history.is_file():
            raise CanonicalIntegrityError(
                "generated-artifact history inventory is missing"
            )
        inventory = json.loads(history.read_text(encoding="utf-8"))
        if inventory.get("status") != "HISTORICAL_EVIDENCE":
            raise CanonicalIntegrityError(
                "generated-artifact inventory has the wrong status"
            )

        result = compute_integrity(ROOT / "spec")
        if result.profile != INTEGRITY_PROFILE:
            raise CanonicalIntegrityError(
                f"unexpected integrity profile: {result.profile!r}"
            )
        if not result.matches:
            print(
                "FAIL: canonical source root mismatch\n"
                + json.dumps(result.as_dict(), indent=2, sort_keys=True),
                file=sys.stderr,
            )
            return 1
        print(
            "PASS: canonical source root "
            f"{result.computed}; {result.files_count} source files; "
            "generated artifacts absent from active authority"
        )
        return 0
    except (CanonicalIntegrityError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
