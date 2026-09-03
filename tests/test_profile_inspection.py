from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "urdf" / "openrgd_minimal_arm.urdf"


def _run_cli(
    args: list[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["rgd", "--quiet", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _make_project(tmp_path: Path, name: str) -> Path:
    project = tmp_path / name
    result = _run_cli(
        ["alive", str(FIXTURE), "--out", str(project)],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return project


def test_check_json_verifies_integrity_and_loaded_modules(tmp_path: Path) -> None:
    project = _make_project(tmp_path, "check-profile")

    result = _run_cli(["check", "--output", "json"], cwd=project)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)

    assert payload["artifact_type"] == "OPENRGD_PROFILE_VALIDATION"
    assert payload["status"] == "VALID"
    assert payload["integrity"]["matches"] is True
    assert payload["robot_id"] == "did:rgd:openrgd_minimal_arm"
    assert payload["modules_count"] == len(payload["modules"])
    assert payload["physical_execution_assessed"] is False
    assert payload["runtime_readiness"] == "NOT_ASSESSED"
    assert {item["path"] for item in payload["modules"]} >= {
        "01_foundation/description.jsonc",
        "01_foundation/actuation_dynamics.jsonc",
        "04_volition/alignment.jsonc",
    }


def test_boot_json_is_deterministic_and_never_authorizes_actuation(
    tmp_path: Path,
) -> None:
    project = _make_project(tmp_path, "boot-profile")

    first = _run_cli(["boot", "--output", "json"], cwd=project)
    second = _run_cli(["boot", "--output", "json"], cwd=project)
    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert first.stdout == second.stdout

    context = json.loads(first.stdout)
    assert (
        context["artifact_type"]
        == "OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT"
    )
    assert context["integrity"]["matches"] is True
    assert context["physical_execution"] == {
        "assessed": False,
        "authorized": False,
        "status": "NOT_AUTHORIZED_BY_BOOT",
    }
    assert "01_foundation/actuation_dynamics.jsonc" in context["modules"]
    assert "04_volition/alignment.jsonc" in context["modules"]
    assert context["summary"]["alignment"]["hard_invariants_count"] == 4


def test_boot_text_removes_runtime_readiness_claims(tmp_path: Path) -> None:
    project = _make_project(tmp_path, "boot-text")

    result = _run_cli(["boot"], cwd=project)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "GROUNDING_ONLY" in result.stdout
    assert "Physical execution authorized: NO" in result.stdout
    assert "I am ready" not in result.stdout
    assert "Cognitive Grounding Complete" not in result.stdout


def test_check_and_boot_reject_stale_source_tree(tmp_path: Path) -> None:
    project = _make_project(tmp_path, "stale-profile")
    description = project / "spec/01_foundation/description.jsonc"
    description.write_text(
        description.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )

    checked = _run_cli(["check", "--output", "json"], cwd=project)
    booted = _run_cli(["boot", "--output", "json"], cwd=project)

    assert checked.returncode == 1
    assert "integrity mismatch" in checked.stderr.lower()
    assert booted.returncode == 1
    assert "integrity mismatch" in booted.stderr.lower()


def test_check_rejects_invalid_module_even_after_rehash(tmp_path: Path) -> None:
    project = _make_project(tmp_path, "invalid-module")
    world_model = project / "spec/03_agency/world_model.jsonc"
    world_model.write_text("[]\n", encoding="utf-8")

    rehash = _run_cli(["hash", "--write"], cwd=project)
    assert rehash.returncode == 0, rehash.stdout + rehash.stderr

    checked = _run_cli(["check", "--output", "json"], cwd=project)
    booted = _run_cli(["boot", "--output", "json"], cwd=project)
    assert checked.returncode == 1
    assert "must contain a json object" in checked.stderr.lower()
    assert booted.returncode == 1
    assert "must contain a json object" in booted.stderr.lower()


def test_check_rejects_unsafe_kernel_module_reference(tmp_path: Path) -> None:
    project = _make_project(tmp_path, "unsafe-module")
    kernel_path = project / "spec/00_core/kernel.jsonc"
    kernel = kernel_path.read_text(encoding="utf-8")
    marker = '"module_loading_order_list": ['
    assert marker in kernel
    kernel = kernel.replace(
        marker,
        marker + '\n    "../outside.jsonc",',
        1,
    )
    kernel_path.write_text(kernel, encoding="utf-8")

    rehash = _run_cli(["hash", "--write"], cwd=project)
    assert rehash.returncode == 0, rehash.stdout + rehash.stderr

    checked = _run_cli(["check", "--output", "json"], cwd=project)
    assert checked.returncode == 1
    assert "unsafe kernel module reference" in checked.stderr.lower()
