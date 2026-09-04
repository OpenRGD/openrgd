from __future__ import annotations

import json
from pathlib import Path
import shutil

from openrgd.core.canonical import (
    INTEGRITY_PROFILE,
    build_machine_bundle,
    build_standard_mirror,
    compute_integrity,
    discover_source_paths,
    update_manifest_integrity,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_FILES = 81


def file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def copy_spec(tmp_path: Path) -> Path:
    destination = tmp_path / "spec"
    shutil.copytree(ROOT / "spec", destination)
    return destination


def test_repository_source_tree_matches_declared_root() -> None:
    result = compute_integrity(ROOT / "spec")
    assert result.profile == INTEGRITY_PROFILE
    assert result.matches
    assert result.files_count == EXPECTED_SOURCE_FILES


def test_machine_bundle_is_byte_deterministic(tmp_path: Path) -> None:
    spec = copy_spec(tmp_path)
    first = tmp_path / "first.json"
    second = tmp_path / "nested" / "second.json"

    first_result = build_machine_bundle(spec, first)
    second_result = build_machine_bundle(spec, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_result["output_sha256"] == second_result["output_sha256"]
    bundle = json.loads(first.read_text(encoding="utf-8"))
    assert bundle["meta"]["bundle_integrity_hash"] == compute_integrity(spec).computed
    assert "generated_at" not in bundle["meta"]


def test_standard_mirror_is_byte_deterministic(tmp_path: Path) -> None:
    spec = copy_spec(tmp_path)
    first = tmp_path / "standard-a"
    second = tmp_path / "standard-b"

    assert build_standard_mirror(spec, first) == EXPECTED_SOURCE_FILES
    assert build_standard_mirror(spec, second) == EXPECTED_SOURCE_FILES
    assert file_map(first) == file_map(second)
    assert len(file_map(first)) == EXPECTED_SOURCE_FILES


def test_generated_aggregate_name_is_not_part_of_source_root(tmp_path: Path) -> None:
    spec = copy_spec(tmp_path)
    before = compute_integrity(spec).computed
    (spec / "openrgd_unified_spec.jsonc").write_text(
        '{"generated": true}\n', encoding="utf-8"
    )
    selected = {
        path.relative_to(spec).as_posix() for path in discover_source_paths(spec)
    }
    assert "openrgd_unified_spec.jsonc" not in selected
    assert compute_integrity(spec).computed == before


def test_source_change_requires_and_stabilizes_rehash(tmp_path: Path) -> None:
    spec = copy_spec(tmp_path)
    original = compute_integrity(spec)
    assert original.matches

    kernel = spec / "00_core" / "kernel.jsonc"
    kernel.write_text(
        kernel.read_text(encoding="utf-8") + "\n// local profile mutation\n",
        encoding="utf-8",
        newline="\n",
    )
    changed = compute_integrity(spec)
    assert not changed.matches
    assert changed.computed != original.computed

    updated = update_manifest_integrity(spec)
    assert updated.matches
    assert updated.computed == changed.computed
