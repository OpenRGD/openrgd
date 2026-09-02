#!/usr/bin/env python3
"""Validate repository-level OpenRGD invariants without mutating the tree."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DOMAINS = (
    "01_foundation",
    "02_operation",
    "03_agency",
    "04_volition",
    "05_evolution",
    "06_ether",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_jsonc(path: Path) -> dict[str, Any]:
    # Import the same parser used by the installed OpenRGD toolchain.
    from openrgd.core.utils import strip_jsonc

    return json.loads(strip_jsonc(path.read_text(encoding="utf-8")), strict=False)


def load_pyproject() -> dict[str, Any]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def validate_python_metadata() -> None:
    project = load_pyproject()["project"]
    if project.get("name") != "rgd":
        fail("pyproject project.name must remain 'rgd'")

    requirement = project.get("requires-python", "")
    match = re.search(r">=\s*(\d+)\.(\d+)", requirement)
    if not match or (int(match.group(1)), int(match.group(2))) < (3, 10):
        fail(f"requires-python must declare Python 3.10+; found {requirement!r}")

    scripts = project.get("scripts", {})
    if scripts.get("rgd") != "openrgd.main:run":
        fail("the rgd console entry point must target openrgd.main:run")


def validate_standard_manifest() -> str:
    manifest_path = ROOT / "spec" / "manifest.jsonc"
    manifest = load_jsonc(manifest_path)
    meta = manifest.get("meta_group", {})
    version = meta.get("rgd_standard_version_semver_str", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"invalid standard semantic version: {version!r}")

    domains = manifest.get("domains_map", {})
    if tuple(domains.keys()) != EXPECTED_DOMAINS:
        fail(
            "spec/manifest.jsonc must declare the canonical domain order: "
            + ", ".join(EXPECTED_DOMAINS)
        )

    if not (ROOT / "spec" / "00_core").is_dir():
        fail("missing spec/00_core")
    for domain in EXPECTED_DOMAINS:
        if not (ROOT / "spec" / domain).is_dir():
            fail(f"missing specification domain: spec/{domain}")

    return version


def validate_version_copies(standard_version: str) -> None:
    standard_manifest = json.loads(
        (ROOT / "standard" / "manifest.json").read_text(encoding="utf-8")
    )
    strict_version = standard_manifest["meta_group"][
        "rgd_standard_version_semver_str"
    ]
    if strict_version != standard_version:
        fail(
            "standard/manifest.json version diverges from spec/manifest.jsonc: "
            f"{strict_version} != {standard_version}"
        )

    seed_manifest = load_jsonc(
        ROOT / "src" / "openrgd" / "seeds" / "default" / "spec" / "manifest.jsonc"
    )
    seed_version = seed_manifest["meta_group"]["rgd_standard_version_semver_str"]
    if seed_version != standard_version:
        fail(
            "packaged seed manifest version diverges from source manifest: "
            f"{seed_version} != {standard_version}"
        )


def validate_reconciliation_files() -> None:
    required = (
        "README.md",
        "STRUCTURE.md",
        "LAYOUT.md",
        "GLOSSARIO.md",
        "VERSIONING.md",
        "docs/reconciliation/README.md",
        "docs/reconciliation/DECISIONS.md",
        "docs/reconciliation/REPOSITORY_MAP.md",
        "docs/history/README.md",
        "docs/history/STRUCTURE_2025_LEGACY.md",
        "docs/history/GLOSSARIO_MISFILED_GITIGNORE_2025.md",
        "contracts/README.md",
        "contracts/agent/v0.1.0/README.md",
        "contracts/agent/v0.1.0/PROVENANCE.md",
        "contracts/agent/v0.1.0/validate.py",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        fail("missing reconciliation files: " + ", ".join(missing))

    contract_readme = (
        ROOT / "contracts" / "agent" / "v0.1.0" / "README.md"
    ).read_text(encoding="utf-8")
    provenance = (
        ROOT / "contracts" / "agent" / "v0.1.0" / "PROVENANCE.md"
    ).read_text(encoding="utf-8")
    if "CONVERGENCE CANDIDATE" not in contract_readme:
        fail("agent contract package lost its candidate maturity label")
    if "a295463bfc9fb9ad26bc2bff90800874d9e4f7c5db8219fc9a0b7123d2ceb987" not in provenance:
        fail("agent contract provenance is missing the source archive SHA-256")


def tracked_paths() -> list[str]:
    if not (ROOT / ".git").exists():
        print("NOTICE: .git unavailable; tracked-artifact audit skipped")
        return []
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def validate_no_generated_artifacts() -> None:
    forbidden: list[str] = []
    for path in tracked_paths():
        parts = PurePosixPath(path).parts
        if path.startswith(("build/", "dist/")):
            forbidden.append(path)
        elif "__pycache__" in parts or path.endswith((".pyc", ".pyo")):
            forbidden.append(path)
        elif any(part.endswith(".egg-info") for part in parts):
            forbidden.append(path)
        elif path == "src/openrgd.rar":
            forbidden.append(path)
    if forbidden:
        fail("generated artifacts are tracked: " + ", ".join(sorted(forbidden)))


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_spec_copy(source: Path, copy: Path, label: str) -> None:
    source_files = {
        p.relative_to(source).as_posix(): p
        for p in source.rglob("*.jsonc")
        if "unified_spec" not in p.name and not p.name.endswith("_spec.jsonc")
    }
    copy_files = {
        p.relative_to(copy).as_posix(): p
        for p in copy.rglob("*.jsonc")
        if "unified_spec" not in p.name and not p.name.endswith("_spec.jsonc")
    }
    missing = sorted(set(source_files) - set(copy_files))
    extra = sorted(set(copy_files) - set(source_files))
    changed = sorted(
        rel
        for rel in set(source_files) & set(copy_files)
        if file_digest(source_files[rel]) != file_digest(copy_files[rel])
    )
    print(
        f"NOTICE: {label}: {len(missing)} missing, {len(extra)} extra, "
        f"{len(changed)} byte-divergent JSONC files"
    )
    if missing:
        print("  missing sample:", ", ".join(missing[:5]))
    if extra:
        print("  extra sample:", ", ".join(extra[:5]))
    if changed:
        print("  changed sample:", ", ".join(changed[:5]))


def main() -> int:
    validate_python_metadata()
    version = validate_standard_manifest()
    validate_version_copies(version)
    validate_reconciliation_files()
    validate_no_generated_artifacts()
    audit_spec_copy(
        ROOT / "spec",
        ROOT / "src" / "openrgd" / "seeds" / "default" / "spec",
        "packaged seed audit",
    )
    print(f"PASS: repository invariants; standard bundle {version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
