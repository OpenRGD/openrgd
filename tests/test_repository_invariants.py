from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from openrgd.core.canonical import compute_integrity
from openrgd.core.utils import strip_jsonc

ROOT = Path(__file__).resolve().parents[1]
DID_FIELD_PATTERN = re.compile(r'("id"\s*:\s*")(?P<did>did:rgd:[^"]+)(")')


def run_script(relative_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def write_minimal_usda(path: Path) -> None:
    path.write_text(
        '''#usda 1.0
(
    defaultPrim = "TestArm"
)

def Xform "TestArm"
{
    def PhysicsRevoluteJoint "joint_1"
    {
        float:physics:lowerLimit = -1.0
        float:physics:upperLimit = 1.5
        float:drive:angular:physics:stiffness = 12.0
        float:drive:angular:physics:damping = 0.75
        float:drive:angular:physics:maxForce = 4.5
    }
}
''',
        encoding="utf-8",
    )


def test_repository_validator_passes() -> None:
    result = run_script("tools/validate_repository.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: repository invariants" in result.stdout


def test_artifact_reconciliation_passes() -> None:
    result = run_script("tools/reconcile_artifacts.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: artifact reconciliation policy" in result.stdout
    assert "0 approved overrides" in result.stdout
    assert "0 unexpected" in result.stdout


def test_canonical_hash_validator_passes() -> None:
    result = run_script("tools/validate_canonical_hash.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: canonical source root" in result.stdout


def test_runtime_boundary_validator_passes() -> None:
    result = run_script("tools/validate_runtime_boundary.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "canonical CLI is non-actuating and fail-closed" in result.stdout


def test_rgd_init_materializes_and_rehashes_default_seed(tmp_path: Path) -> None:
    result = subprocess.run(
        ["rgd", "--quiet", "init", "seed-probe"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    generated_spec = tmp_path / "seed-probe" / "spec"
    policy = json.loads(
        (ROOT / "docs/reconciliation/ARTIFACT_POLICY.json").read_text(
            encoding="utf-8"
        )
    )
    selection = policy["canonical_file_selection"]
    excluded = set(selection["excluded_source_files"])

    expected: dict[str, Path] = {}
    for source in sorted((ROOT / "spec").rglob("*.jsonc")):
        rel = source.relative_to(ROOT / "spec").as_posix()
        if rel not in excluded:
            expected[rel] = source
    for rel in selection["static_files"]:
        expected[rel] = ROOT / "spec" / rel

    for rel, source in expected.items():
        generated = generated_spec / rel
        assert generated.is_file(), f"rgd init omitted {rel}"

        if rel == "00_core/kernel.jsonc":
            source_text = source.read_text(encoding="utf-8")
            generated_text = generated.read_text(encoding="utf-8")
            source_id = DID_FIELD_PATTERN.search(source_text)
            generated_id = DID_FIELD_PATTERN.search(generated_text)

            assert source_id is not None, "canonical kernel has no RGD DID"
            assert generated_id is not None, "generated kernel has no RGD DID"
            assert generated_id.group("did") == "did:rgd:seed-probe"

            normalized_generated = (
                generated_text[: generated_id.start("did")]
                + source_id.group("did")
                + generated_text[generated_id.end("did") :]
            )
            assert normalized_generated == source_text, (
                "rgd init changed kernel content beyond DID personalization"
            )
        elif rel == "manifest.jsonc":
            source_manifest = json.loads(
                strip_jsonc(source.read_text(encoding="utf-8")), strict=False
            )
            generated_manifest = json.loads(
                strip_jsonc(generated.read_text(encoding="utf-8")), strict=False
            )
            generated_hash = generated_manifest["meta_group"]["integrity_hash_str"]
            source_manifest["meta_group"]["integrity_hash_str"] = generated_hash
            assert generated_manifest == source_manifest, (
                "rgd init changed manifest content beyond its integrity root"
            )
        else:
            assert generated.read_bytes() == source.read_bytes(), (
                f"rgd init generated a divergent copy of {rel}"
            )

    integrity = compute_integrity(generated_spec)
    assert integrity.matches
    assert integrity.computed != compute_integrity(ROOT / "spec").computed

    assert not (generated_spec / "openrgd_unified_spec.json").exists()
    assert not (generated_spec / "openrgd_unified_spec.jsonc").exists()
    assert not (generated_spec / "03_agency/skills_library.json").exists()


def test_usd_importer_emits_only_source_supported_partial_evidence(
    tmp_path: Path,
) -> None:
    from openrgd.importers.usd.parser import USDImporter

    source = tmp_path / "test-arm.usda"
    write_minimal_usda(source)

    importer = USDImporter(str(source))
    imported = importer.parse()

    assert importer.robot_name == "TestArm"
    assert set(imported) == {
        "spec/01_foundation/description.jsonc",
        "spec/01_foundation/actuation_dynamics.jsonc",
    }
    assert all("safety_supervisor.jsonc" not in value for value in imported.values())
    assert all("alignment" not in path for path in imported)
    assert all("00_core" not in path for path in imported)

    dynamics_text = imported["spec/01_foundation/actuation_dynamics.jsonc"]
    dynamics = json.loads(dynamics_text.split("\n", 1)[1])
    assert dynamics["joint_1"]["limits"] == {
        "torque_nm": 4.5,
        "range_rad": [-1.0, 1.5],
    }


def test_import_cli_uses_one_spec_root_and_does_not_invent_policy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "test-arm.usda"
    output = tmp_path / "partial-rgd"
    write_minimal_usda(source)

    result = subprocess.run(
        [
            "rgd",
            "--quiet",
            "import",
            str(source),
            "--out",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    spec = output / "spec"
    assert (spec / "01_foundation/description.jsonc").is_file()
    assert (spec / "01_foundation/actuation_dynamics.jsonc").is_file()
    assert not (spec / "spec").exists()
    assert not (spec / "00_core").exists()
    assert not (spec / "02_operation").exists()
    assert not (spec / "04_volition").exists()


def test_candidate_contract_validator_passes() -> None:
    result = run_script("contracts/agent/v0.1.0/validate.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: 4 schemas" in result.stdout


def test_so101_flow_keeps_cognition_and_actuation_separate() -> None:
    example = json.loads(
        (ROOT / "contracts/agent/v0.1.0/examples/so101-causal-flow.json").read_text(
            encoding="utf-8"
        )
    )
    events = [entry["event"] for entry in example["chronon_flow"]]
    assert events.index("action_intent") < events.index("somatic_plan")
    assert events.index("somatic_plan") < events.index("safety_decision")
    assert events.index("safety_decision") < events.index("action_result")


def test_alive_merges_seed_and_rehashes_profile(tmp_path: Path) -> None:
    source = tmp_path / "test-arm.usda"
    output = tmp_path / "RGD-TestArm"
    write_minimal_usda(source)

    result = subprocess.run(
        [
            "rgd",
            "--quiet",
            "alive",
            str(source),
            "--out",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (output / "spec" / "spec").exists()
    assert compute_integrity(output / "spec").matches

    project_manifest = json.loads(
        (output / "manifest.json").read_text(encoding="utf-8")
    )
    assert project_manifest["standard_version"] == "0.2.0"
