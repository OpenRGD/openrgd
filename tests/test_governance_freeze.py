from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_governance_freeze_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/validate_governance.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: governance freeze" in result.stdout


def test_agent_contracts_remain_candidate_and_non_normative() -> None:
    status = json.loads(
        (ROOT / "contracts/agent/v0.1.0/STATUS.json").read_text(
            encoding="utf-8"
        )
    )
    assert status["maturity"] == "candidate"
    assert status["normative"] is False
    assert status["accepted"] is False
    assert status["stable_release_allowed"] is False


def test_aion_ready_expected_archive_and_backup_variant_remain_distinct() -> None:
    scope = json.loads(
        (ROOT / "docs/reconciliation/EVIDENCE_SCOPE.json").read_text(
            encoding="utf-8"
        )
    )
    artifact = scope["excluded_artifacts"][0]
    recovered = artifact["recovered_backup_variant"]
    assert artifact["artifact_name"] == "openrgd-v0.2-aion-ready.zip"
    assert artifact["classification"] == (
        "EXPECTED_IDENTITY_UNAVAILABLE_RECOVERED_BACKUP_VARIANT_MISMATCH"
    )
    assert artifact["expected_sha256"] != recovered["sha256"]
    assert artifact["expected_archive_contents_inspected"] is False
    assert recovered["contents_inspected"] is True
    assert recovered["contains_local_env_secret"] is True
    assert artifact["used_as_source_for_pull_request"] is False
    assert artifact["merge_blocking"] is False


def test_merge_policy_preserves_granular_history_and_protects_main() -> None:
    policy = json.loads(
        (ROOT / "governance/policy.json").read_text(encoding="utf-8")
    )
    merge = policy["merge_policy"]
    assert merge["pull_request_required"] is True
    assert merge["direct_pushes_to_main_allowed"] is False
    assert merge["force_push_to_main_allowed"] is False
    assert merge["delete_main_allowed"] is False
    assert merge["default_merge_method"] == "merge_commit"
    assert merge["squash_requires_explicit_decision"] is True
    assert merge["reconciliation_pr_1_merge_method"] == "merge_commit"
