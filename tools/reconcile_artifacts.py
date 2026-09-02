#!/usr/bin/env python3
"""Reconcile the normative spec, strict-JSON mirror, and packaged default seed.

The policy is intentionally conservative:

- ``spec/`` is the normative human-readable source.
- ``standard/`` must be semantically equivalent strict JSON.
- the packaged default seed must be byte-identical to selected canonical sources,
  unless a hash-pinned runtime-profile override is explicitly approved.
- generated aggregate bundles are outside the leaf-mirror contract.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "reconciliation" / "ARTIFACT_POLICY.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonc(path: Path) -> Any:
    from openrgd.core.utils import strip_jsonc

    return json.loads(strip_jsonc(path.read_text(encoding="utf-8")), strict=False)


def load_policy(path: Path) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "canonical_source_root",
        "standard_mirror_root",
        "default_seed_root",
        "canonical_file_selection",
        "standard_mirror",
        "default_seed",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise ValueError("artifact policy missing keys: " + ", ".join(missing))
    return policy


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def canonical_files(root: Path, policy: dict[str, Any]) -> dict[str, Path]:
    source_root = root / policy["canonical_source_root"]
    selection = policy["canonical_file_selection"]
    excluded = set(selection.get("excluded_source_files", []))

    selected: dict[str, Path] = {}
    if selection.get("jsonc_recursive", False):
        for path in sorted(source_root.rglob("*.jsonc")):
            rel = path.relative_to(source_root).as_posix()
            if rel not in excluded:
                selected[rel] = path

    for rel in selection.get("static_files", []):
        path = source_root / rel
        if not path.is_file():
            raise FileNotFoundError(f"canonical static file missing: {rel}")
        selected[rel] = path

    if not selected:
        raise ValueError("artifact policy selected no canonical files")
    return selected


def standard_target_rel(source_rel: str) -> str:
    path = PurePosixPath(source_rel)
    return path.with_suffix(".json").as_posix() if path.suffix == ".jsonc" else source_rel


def validate_override_declarations(
    root: Path,
    policy: dict[str, Any],
    canonical: dict[str, Path],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    seed_root = root / policy["default_seed_root"]
    seed_policy = policy["default_seed"]
    required_fields = set(seed_policy.get("override_required_fields", []))
    overrides: dict[str, dict[str, str]] = {}
    errors: list[str] = []

    for index, raw in enumerate(seed_policy.get("allowed_overrides", [])):
        if not isinstance(raw, dict):
            errors.append(f"seed override #{index} must be an object")
            continue
        missing = sorted(required_fields - set(raw))
        if missing:
            errors.append(
                f"seed override #{index} missing fields: {', '.join(missing)}"
            )
            continue

        rel = str(raw["path"])
        if rel in overrides:
            errors.append(f"duplicate seed override declaration: {rel}")
            continue
        if rel not in canonical:
            errors.append(f"seed override does not target a canonical file: {rel}")
            continue
        if raw.get("classification") != "RUNTIME_PROFILE_OVERRIDE":
            errors.append(
                f"seed override {rel} must use classification "
                "RUNTIME_PROFILE_OVERRIDE"
            )
        if not str(raw.get("reason", "")).strip():
            errors.append(f"seed override {rel} has no reason")
        if not str(raw.get("decision_ref", "")).strip():
            errors.append(f"seed override {rel} has no decision_ref")

        seed_path = seed_root / rel
        if not seed_path.is_file():
            errors.append(f"declared seed override file missing: {rel}")
            continue

        canonical_digest = sha256(canonical[rel])
        seed_digest = sha256(seed_path)
        if canonical_digest != raw.get("canonical_sha256"):
            errors.append(
                f"canonical digest changed for declared override {rel}: "
                f"{canonical_digest}"
            )
        if seed_digest != raw.get("seed_sha256"):
            errors.append(
                f"seed digest changed for declared override {rel}: {seed_digest}"
            )
        if canonical_digest == seed_digest:
            errors.append(
                f"seed override {rel} is byte-identical and should be removed"
            )

        overrides[rel] = {str(k): str(v) for k, v in raw.items()}

    return overrides, errors


def check_standard(
    root: Path,
    policy: dict[str, Any],
    canonical: dict[str, Path],
) -> tuple[list[str], dict[str, int]]:
    standard_root = root / policy["standard_mirror_root"]
    standard_policy = policy["standard_mirror"]
    allowed_generated = list(standard_policy.get("allowed_generated_paths", []))
    errors: list[str] = []
    expected_targets: set[str] = set()
    missing = 0
    mismatched = 0

    for source_rel, source_path in canonical.items():
        target_rel = standard_target_rel(source_rel)
        expected_targets.add(target_rel)
        target_path = standard_root / target_rel
        if not target_path.is_file():
            errors.append(f"standard mirror missing: {target_rel}")
            missing += 1
            continue

        try:
            if source_path.suffix == ".jsonc":
                source_value = load_jsonc(source_path)
                target_value = json.loads(target_path.read_text(encoding="utf-8"))
                equivalent = source_value == target_value
            else:
                equivalent = source_path.read_bytes() == target_path.read_bytes()
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            errors.append(f"standard mirror unreadable {target_rel}: {exc}")
            mismatched += 1
            continue

        if not equivalent:
            errors.append(f"standard mirror diverges semantically: {target_rel}")
            mismatched += 1

    actual = {
        path.relative_to(standard_root).as_posix()
        for path in standard_root.rglob("*")
        if path.is_file()
    }
    unexpected = sorted(
        rel
        for rel in actual - expected_targets
        if not matches_any(rel, allowed_generated)
    )
    errors.extend(f"unexpected standard artifact: {rel}" for rel in unexpected)

    return errors, {
        "expected": len(expected_targets),
        "missing": missing,
        "mismatched": mismatched,
        "unexpected": len(unexpected),
    }


def check_seed(
    root: Path,
    policy: dict[str, Any],
    canonical: dict[str, Path],
) -> tuple[list[str], dict[str, int]]:
    seed_root = root / policy["default_seed_root"]
    seed_policy = policy["default_seed"]
    allowed_extra = list(seed_policy.get("allowed_extra_paths", []))
    overrides, errors = validate_override_declarations(root, policy, canonical)
    missing = 0
    mismatched = 0

    for rel, source_path in canonical.items():
        seed_path = seed_root / rel
        if not seed_path.is_file():
            errors.append(f"default seed missing: {rel}")
            missing += 1
            continue
        if rel in overrides:
            continue
        if source_path.read_bytes() != seed_path.read_bytes():
            errors.append(f"default seed diverges without approval: {rel}")
            mismatched += 1

    actual = {
        path.relative_to(seed_root).as_posix()
        for path in seed_root.rglob("*")
        if path.is_file()
    }
    expected = set(canonical)
    unexpected = sorted(
        rel for rel in actual - expected if not matches_any(rel, allowed_extra)
    )
    errors.extend(f"unexpected default-seed artifact: {rel}" for rel in unexpected)

    return errors, {
        "expected": len(expected),
        "missing": missing,
        "mismatched": mismatched,
        "overrides": len(overrides),
        "unexpected": len(unexpected),
    }


def write_standard(
    root: Path,
    policy: dict[str, Any],
    canonical: dict[str, Path],
) -> None:
    standard_root = root / policy["standard_mirror_root"]
    for source_rel, source_path in canonical.items():
        target_path = standard_root / standard_target_rel(source_rel)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.suffix == ".jsonc":
            value = load_jsonc(source_path)
            target_path.write_text(
                json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        else:
            shutil.copyfile(source_path, target_path)


def write_seed(
    root: Path,
    policy: dict[str, Any],
    canonical: dict[str, Path],
    *,
    prune: bool,
) -> None:
    seed_root = root / policy["default_seed_root"]
    overrides, errors = validate_override_declarations(root, policy, canonical)
    if errors:
        raise ValueError(
            "cannot write seed while override declarations are invalid: "
            + "; ".join(errors)
        )

    for rel, source_path in canonical.items():
        if rel in overrides:
            continue
        target_path = seed_root / rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)

    if not prune:
        return

    allowed_extra = list(policy["default_seed"].get("allowed_extra_paths", []))
    expected = set(canonical)
    for path in sorted(seed_root.rglob("*"), reverse=True):
        if path.is_file():
            rel = path.relative_to(seed_root).as_posix()
            if rel not in expected and not matches_any(rel, allowed_extra):
                path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or regenerate the OpenRGD canonical leaf mirrors. "
            "Generated domain/unified bundles are intentionally out of scope."
        )
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY,
        help="Path to ARTIFACT_POLICY.json",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate standard leaf mirrors and synchronize seed source files.",
    )
    parser.add_argument(
        "--prune-seed",
        action="store_true",
        help="With --write, remove undeclared files from the active seed namespace.",
    )
    args = parser.parse_args()

    if args.prune_seed and not args.write:
        parser.error("--prune-seed requires --write")

    policy_path = args.policy
    if not policy_path.is_absolute():
        policy_path = ROOT / policy_path

    try:
        policy = load_policy(policy_path)
        canonical = canonical_files(ROOT, policy)

        if args.write:
            write_standard(ROOT, policy, canonical)
            write_seed(ROOT, policy, canonical, prune=args.prune_seed)

        standard_errors, standard_stats = check_standard(ROOT, policy, canonical)
        seed_errors, seed_stats = check_seed(ROOT, policy, canonical)
        errors = standard_errors + seed_errors

        print(
            "STANDARD: "
            f"{standard_stats['expected']} expected, "
            f"{standard_stats['missing']} missing, "
            f"{standard_stats['mismatched']} mismatched, "
            f"{standard_stats['unexpected']} unexpected"
        )
        print(
            "DEFAULT SEED: "
            f"{seed_stats['expected']} expected, "
            f"{seed_stats['missing']} missing, "
            f"{seed_stats['mismatched']} mismatched, "
            f"{seed_stats['overrides']} approved overrides, "
            f"{seed_stats['unexpected']} unexpected"
        )

        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1

        mode = "write+check" if args.write else "check"
        print(f"PASS: artifact reconciliation policy ({mode})")
        return 0
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
