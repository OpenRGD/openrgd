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
