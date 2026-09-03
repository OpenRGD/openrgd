# OPENRGD CORE - ALIVE MODULE
# ------------------------------------------------------------------------------
# This module merges source-derived partial evidence with an explicitly selected
# packaged seed. The resulting profile is integrity-addressed, but seed-to-body
# semantic compatibility remains an operator review concern.
# ------------------------------------------------------------------------------

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import re
from typing import Any, Dict, Mapping


SEEDS_ROOT = Path(__file__).resolve().parent.parent / "seeds"
_DID_RE = re.compile(r'(?P<prefix>"id"\s*:\s*")did:rgd:[^"]+(?P<suffix>")')
_BUNDLE_ID_RE = re.compile(
    r'(?P<prefix>"bundle_id_str"\s*:\s*")[^"]+(?P<suffix>")'
)


def _load_seed_spec(seed_name: str) -> Dict[str, str]:
    """Load one packaged seed as ``relative/path -> UTF-8 contents``."""

    seed_spec_root = SEEDS_ROOT / seed_name / "spec"
    if not seed_spec_root.exists():
        raise FileNotFoundError(
            f"Seed spec not found for seed '{seed_name}' at: {seed_spec_root}"
        )

    spec_map: Dict[str, str] = {}
    for path in sorted(seed_spec_root.rglob("*")):
        if path.is_file():
            rel_path = path.relative_to(seed_spec_root).as_posix()
            spec_map[rel_path] = path.read_text(encoding="utf-8")
    return spec_map


def _did_component(robot_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9._-]+", "-", robot_name.lower()).strip("._-")
    return normalized or "robot"


def _apply_robot_placeholders(
    content: str,
    *,
    relative_path: str,
    robot_name: str,
    project_id: str,
) -> str:
    """Apply explicit placeholders and identity fields to seed material."""

    rendered = content.replace("{{ROBOT_NAME}}", robot_name)
    rendered = rendered.replace("{{PROJECT_ID}}", project_id)

    did_component = _did_component(robot_name)
    if relative_path == "00_core/kernel.jsonc":
        rendered, count = _DID_RE.subn(
            rf'\g<prefix>did:rgd:{did_component}\g<suffix>',
            rendered,
            count=1,
        )
        if count != 1:
            raise ValueError(
                "seed kernel must contain exactly one OpenRGD DID identity field"
            )
    elif relative_path == "manifest.jsonc":
        rendered, count = _BUNDLE_ID_RE.subn(
            rf'\g<prefix>{did_component}_profile\g<suffix>',
            rendered,
            count=1,
        )
        if count != 1:
            raise ValueError(
                "seed manifest must contain exactly one bundle_id_str field"
            )

    return rendered


def _normalize_partial_path(raw_path: str) -> str:
    normalized = str(raw_path).replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("spec/"):
        normalized = normalized[len("spec/") :]

    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.parts[0] == "spec"
    ):
        raise ValueError(f"unsafe partial-spec path: {raw_path!r}")
    return path.as_posix()


def alive_rgd_spec(
    base_spec: Mapping[str, str],
    robot_name: str,
    seed_name: str = "default",
) -> Dict[str, str]:
    """Merge source-derived partial evidence with an explicit packaged seed.

    Imported evidence overrides a seed file only on an exact relative-path
    collision. The merge proves provenance and materialization mechanics; it
    does not certify that every inherited seed module is physically compatible
    with the imported body.
    """

    project_id = f"RGD-{robot_name}"

    normalized_base: Dict[str, str] = {}
    for rel_path, content in base_spec.items():
        if not isinstance(content, str):
            raise ValueError(f"partial-spec content is not text: {rel_path!r}")
        normalized_base[_normalize_partial_path(rel_path)] = content

    seed_spec = _load_seed_spec(seed_name)
    seeded: Dict[str, str] = {}
    for rel_path, content in seed_spec.items():
        seeded[rel_path] = _apply_robot_placeholders(
            content,
            relative_path=rel_path,
            robot_name=robot_name,
            project_id=project_id,
        )

    full_spec: Dict[str, str] = dict(seeded)
    full_spec.update(normalized_base)
    return full_spec


def write_manifest(
    rgd_root: Path,
    robot_name: str,
    standard_version: str = "0.1.0",
    *,
    seed_name: str | None = None,
    source_artifact: Mapping[str, Any] | None = None,
) -> Path:
    """Write project-level provenance for one materialized OpenRGD profile."""

    manifest_path = rgd_root / "manifest.json"
    if manifest_path.exists():
        return manifest_path

    project_id = f"RGD-{robot_name}"
    manifest: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Generated by the non-actuating OpenRGD 'alive' enrichment pipeline.",
        "profile_kind": "SEED_ENRICHED_IMPORTED_EVIDENCE",
        "project_id": project_id,
        "rgd_manifest_version": "0.2.0",
        "robot_name": robot_name,
        "seed_compatibility_status": "UNVERIFIED",
        "standard_version": standard_version,
    }
    if seed_name is not None:
        manifest["seed_profile"] = seed_name
    if source_artifact is not None:
        manifest["source_artifact"] = dict(source_artifact)

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path


def write_readme(
    rgd_root: Path,
    robot_name: str,
    standard_version: str = "0.1.0",
    *,
    seed_name: str | None = None,
) -> Path:
    """Write a plain-text project handoff with the seed-review warning."""

    readme_path = rgd_root / "README.txt"
    if readme_path.exists():
        return readme_path

    project_id = f"RGD-{robot_name}"
    seed_line = f"Seed profile: {seed_name}\n" if seed_name else ""
    content = (
        f"RGD Profile: {robot_name}\n"
        "---------------------------------------------\n"
        "This directory contains source-derived robot evidence\n"
        "enriched with a reviewed OpenRGD seed profile.\n\n"
        f"Format: OpenRGD v{standard_version}\n"
        f"Project ID: {project_id}\n"
        f"{seed_line}"
        "Seed/body compatibility: UNVERIFIED\n\n"
        "Before hardware use, review every inherited physical,\n"
        "safety and HAL module against the actual body.\n\n"
        "Structure:\n"
        "- manifest.json     project-level provenance\n"
        "- spec/             integrity-addressed OpenRGD profile\n\n"
        "Non-actuating workflow:\n"
        "- rgd hash\n"
        "- rgd check\n"
        "- rgd boot\n"
        "- rgd compile-spec\n"
        "- rgd export ros2\n"
    )
    readme_path.write_text(content, encoding="utf-8", newline="\n")
    return readme_path
