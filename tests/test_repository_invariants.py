from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(relative_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
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


def test_rgdi_init_materializes_the_complete_default_seed(tmp_path: Path) -> None:
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
        assert generated.read_bytes() == source.read_bytes(), (
            f"rgd init generated a divergent copy of {rel}"
        )

    assert not (generated_spec / "openrgd_unified_spec.json").exists()
    assert not (generated_spec / "openrgd_unified_spec.jsonc").exists()
    assert not (generated_spec / "03_agency/skills_library.json").exists()


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
