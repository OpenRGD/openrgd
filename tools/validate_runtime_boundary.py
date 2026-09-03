#!/usr/bin/env python3
"""Validate quarantine and fail-closed behavior of the historical runtime."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_RUNTIME = ROOT / "src" / "openrgd" / "runtime"
ACTIVE_COMMAND = ROOT / "src" / "openrgd" / "commands" / "run.py"
STATUS_PATH = ROOT / "docs" / "reconciliation" / "RUNTIME_STATUS.json"
BOUNDARY_PATH = ROOT / "docs" / "reconciliation" / "RUNTIME_BOUNDARY.md"
ARCHIVE_ROOT = ROOT / "docs" / "history" / "runtime-prototype"

EXPECTED_ARCHIVED_GIT_BLOBS = {
    "commands/run.py": "2dc8fc2f846f2903d8e69e77c709a49f0d841f87",
    "runtime/__init__.py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "runtime/core/__init__py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "runtime/core/engine.py": "29884908c47639f10999181683bb3da213d9af66",
    "runtime/adapters/__init__.py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "runtime/adapters/base.py": "78082934ac714341462b5398bf09d1d92f0a5054",
    "runtime/adapters/ros2/node.py": "a790d786c4bc2ca170dac7a294896195e4e6fcdb",
    "runtime/adapters/viam/__init__.py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "runtime/adapters/viam/node.py": "fddc0f0a42aff487fef85faca9cc9ed4ad07752a",
    "related/core/templates.py": "24339ee9531397b61decafbbc441a4c5eb1a2030",
}

FORBIDDEN_ACTIVE_IMPORT_ROOTS = {
    "rclpy",
    "viam",
    "serial",
    "can",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def validate_archive() -> None:
    if not (ARCHIVE_ROOT / "README.md").is_file():
        fail("runtime prototype archive README is missing")

    for rel, expected in EXPECTED_ARCHIVED_GIT_BLOBS.items():
        path = ARCHIVE_ROOT / rel
        if not path.is_file():
            fail(f"archived runtime evidence missing: {rel}")
        actual = git_blob_sha(path)
        if actual != expected:
            fail(
                f"archived runtime evidence changed: {rel}: "
                f"{actual} != {expected}"
            )


def validate_no_active_runtime_package() -> None:
    if ACTIVE_RUNTIME.exists():
        active_files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in ACTIVE_RUNTIME.rglob("*")
            if path.is_file()
        )
        if active_files:
            fail(
                "quarantined runtime code remains in the installed package: "
                + ", ".join(active_files)
            )

    for path in (ROOT / "src" / "openrgd").rglob("*.py"):
        if path == ACTIVE_COMMAND:
            continue
        text = path.read_text(encoding="utf-8")
        if "02_operation/safety_supervisor.jsonc" in text:
            fail(
                "active source still references the missing historical safety "
                f"module: {path.relative_to(ROOT)}"
            )


def validate_active_command_is_non_actuating() -> None:
    if not ACTIVE_COMMAND.is_file():
        fail("runtime compatibility command is missing")

    source = ACTIVE_COMMAND.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(ACTIVE_COMMAND))

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    forbidden = sorted(imported_roots & FORBIDDEN_ACTIVE_IMPORT_ROOTS)
    if forbidden:
        fail(
            "runtime compatibility command imports middleware/hardware modules: "
            + ", ".join(forbidden)
        )

    forbidden_fragments = (
        "from ..runtime",
        "from openrgd.runtime",
        "RobotClient",
        "create_subscription(",
        "create_publisher(",
        ".spin()",
        "publish_intent(",
    )
    present = [fragment for fragment in forbidden_fragments if fragment in source]
    if present:
        fail(
            "runtime compatibility command contains actuation/runtime code: "
            + ", ".join(present)
        )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["rgd", "--quiet", "run", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def parse_json_stream(value: str, label: str) -> dict[str, Any]:
    text = value.strip()
    if not text:
        fail(f"{label} returned no JSON payload")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"{label} returned invalid JSON: {exc}: {text!r}")
    if not isinstance(payload, dict):
        fail(f"{label} JSON payload must be an object")
    return payload


def validate_status_and_fail_closed_cli() -> None:
    if not STATUS_PATH.is_file() or not BOUNDARY_PATH.is_file():
        fail("runtime reconciliation status or boundary document is missing")

    expected_status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    if expected_status.get("physical_actuation_available") is not False:
        fail("runtime status must declare physical actuation unavailable")
    if expected_status.get("historical_prototype") != "QUARANTINED":
        fail("runtime status must declare the historical prototype quarantined")

    status_result = run_cli("status", "--output", "json")
    if status_result.returncode != 0:
        fail(
            "rgd run status failed: "
            + status_result.stdout
            + status_result.stderr
        )
    status_payload = parse_json_stream(status_result.stdout, "rgd run status")
    for key in (
        "component",
        "canonical_root",
        "status",
        "historical_prototype",
        "physical_actuation_available",
        "contract_package",
        "implementation_repository",
        "repository_name_decision",
        "decision_ref",
    ):
        if status_payload.get(key) != expected_status.get(key):
            fail(
                f"runtime CLI status diverges from RUNTIME_STATUS.json for {key}: "
                f"{status_payload.get(key)!r} != {expected_status.get(key)!r}"
            )

    commands = {
        "ros2": ("ros2", "--kernel", "missing.jsonc", "--output", "json"),
        "viam": ("viam", "--output", "json"),
        "hybrid": ("hybrid", "--output", "json"),
    }
    for adapter, args in commands.items():
        result = run_cli(*args)
        if result.returncode != 2:
            fail(
                f"rgd run {adapter} must fail closed with exit 2; "
                f"got {result.returncode}: {result.stdout}{result.stderr}"
            )
        payload = parse_json_stream(result.stderr, f"rgd run {adapter}")
        if payload.get("outcome") != "BLOCKED":
            fail(f"rgd run {adapter} did not report BLOCKED")
        if payload.get("requested_adapter") != adapter:
            fail(f"rgd run {adapter} reported the wrong adapter")
        if payload.get("physical_actuation_available") is not False:
            fail(f"rgd run {adapter} exposed physical actuation")


def main() -> int:
    try:
        validate_archive()
        validate_no_active_runtime_package()
        validate_active_command_is_non_actuating()
        validate_status_and_fail_closed_cli()
        print(
            "PASS: quarantined runtime evidence intact; canonical CLI is "
            "non-actuating and fail-closed"
        )
        return 0
    except (AssertionError, OSError, SyntaxError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
