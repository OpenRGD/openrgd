#!/usr/bin/env python3
"""Validate the repository-tree governance freeze.

This validator checks versioned policy and repository files. GitHub server-side
branch protection is intentionally verified outside CI because it is not part
of the Git tree.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class GovernanceError(ValueError):
    """Raised when the governance freeze is internally inconsistent."""


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def require_file(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GovernanceError(f"missing governance file: {relative}")
    return path.read_text(encoding="utf-8")


def validate_policy() -> dict[str, Any]:
    policy = load_json("governance/policy.json")
    if policy["canonical_repository"] != "OpenRGD/openrgd":
        raise GovernanceError("unexpected canonical repository")
    if policy["repository_role"] != "NON_ACTUATING_CANONICAL_AND_TOOLING_ROOT":
        raise GovernanceError("canonical repository role drifted")
    if policy["default_branch"] != "main":
        raise GovernanceError("default branch policy drifted")
    if policy["normative_source_root"] != "spec":
        raise GovernanceError("normative source root drifted")

    expected_checks = [
        "Validate Python 3.10",
        "Validate Python 3.12",
        "Build Windows executable",
    ]
    if policy["required_ci_checks"] != expected_checks:
        raise GovernanceError("required CI check list drifted")

    merge = policy["merge_policy"]
    required_true = [
        "pull_request_required",
        "status_checks_required",
        "branch_must_be_up_to_date",
        "conversation_resolution_required",
        "single_maintainer_mode",
        "self_review_checklist_required",
        "squash_requires_explicit_decision",
    ]
    for key in required_true:
        if merge.get(key) is not True:
            raise GovernanceError(f"merge policy must enable {key}")
    for key in [
        "direct_pushes_to_main_allowed",
        "force_push_to_main_allowed",
        "delete_main_allowed",
    ]:
        if merge.get(key) is not False:
            raise GovernanceError(f"merge policy must disable {key}")
    if merge["required_approvals_current"] != 0:
        raise GovernanceError("single-maintainer approval count must be explicit")
    if merge["required_approvals_after_second_maintainer"] < 1:
        raise GovernanceError("multi-maintainer approval floor is missing")
    if merge["default_merge_method"] != "merge_commit":
        raise GovernanceError("granular commit history must be preserved by default")
    if merge["reconciliation_pr_1_merge_method"] != "merge_commit":
        raise GovernanceError("reconciliation PR #1 must preserve its commit sequence")

    tags = policy["tag_policy"]
    if tags != {
        "unscoped_new_tags_allowed": False,
        "standard_prefix": "standard-v",
        "toolchain_prefix": "toolchain-v",
        "agent_contract_prefix": "contracts-agent-v",
    }:
        raise GovernanceError("scoped tag policy drifted")

    if policy["current_contract_packages"] != {"agent/v0.1.0": "candidate"}:
        raise GovernanceError("current contract maturity map drifted")
    return policy


def validate_contract_status(policy: dict[str, Any]) -> None:
    status = load_json("contracts/agent/v0.1.0/STATUS.json")
    if status["maturity"] != "candidate":
        raise GovernanceError("Agent Contracts were promoted without governance")
    if status["normative"] is not False or status["accepted"] is not False:
        raise GovernanceError("candidate Agent Contracts cannot be normative")
    if status["stable_release_allowed"] is not False:
        raise GovernanceError("candidate Agent Contracts cannot use a stable tag")
    if status["merge_behavior"] != "PRESERVE_CANDIDATE_STATUS":
        raise GovernanceError("candidate merge behavior drifted")
    if status["source"]["archive_sha256"] != (
        "a295463bfc9fb9ad26bc2bff90800874d9e4f7c5db8219fc9a0b7123d2ceb987"
    ):
        raise GovernanceError("Agent Contracts provenance digest drifted")
    if policy["maturity_states"]["candidate"]["normative"] is not False:
        raise GovernanceError("candidate maturity policy is inconsistent")


def validate_evidence_scope() -> None:
    scope = load_json("docs/reconciliation/EVIDENCE_SCOPE.json")
    policy = scope["policy"]
    if policy["digest_only_contents_may_be_inferred"] is not False:
        raise GovernanceError("digest-only contents must not be inferred")
    if policy["mismatched_recovered_variant_may_be_treated_as_expected_archive"] is not False:
        raise GovernanceError("mismatched archive variants must retain separate identity")
    if policy["secrets_must_not_be_imported_or_recorded"] is not True:
        raise GovernanceError("evidence policy must exclude secret material")

    artifacts = scope["excluded_artifacts"]
    if len(artifacts) != 1:
        raise GovernanceError("unexpected evidence-exclusion set")
    artifact = artifacts[0]
    if artifact["artifact_name"] != "openrgd-v0.2-aion-ready.zip":
        raise GovernanceError("AION-ready evidence record missing")
    if artifact["classification"] != (
        "EXPECTED_IDENTITY_UNAVAILABLE_RECOVERED_BACKUP_VARIANT_MISMATCH"
    ):
        raise GovernanceError("AION-ready archive identity classification drifted")
    expected = artifact["expected_sha256"]
    if not HEX64.fullmatch(expected):
        raise GovernanceError("AION-ready expected digest is not lowercase SHA-256")
    if artifact["expected_archive_bytes_available_in_reconciliation_workspace"] is not False:
        raise GovernanceError("expected AION-ready archive incorrectly marked available")
    if artifact["expected_archive_contents_inspected"] is not False:
        raise GovernanceError("unavailable expected archive cannot be marked inspected")

    recovered = artifact["recovered_backup_variant"]
    observed = recovered["sha256"]
    if not HEX64.fullmatch(observed):
        raise GovernanceError("recovered backup digest is not lowercase SHA-256")
    if observed == expected:
        raise GovernanceError("mismatched backup variant was relabelled as expected archive")
    if recovered["bytes_available"] is not True or recovered["contents_inspected"] is not True:
        raise GovernanceError("recovered backup inspection state is inconsistent")
    if recovered["contains_local_env_secret"] is not True:
        raise GovernanceError("recovered backup secret contamination is not recorded")
    if recovered["contains_post_checksum_source_delta"] is not True:
        raise GovernanceError("post-checksum source delta is not recorded")
    if recovered["relationship"] != "SAME_LINEAGE_SUPPORTED_BYTE_IDENTITY_NOT_PROVEN":
        raise GovernanceError("recovered backup relationship classification drifted")

    audit = load_json("docs/reconciliation/AION_READY_BACKUP_AUDIT.json")
    if audit["historical_expected_archive"]["sha256"] != expected:
        raise GovernanceError("AION-ready audit expected digest drifted")
    if audit["uploaded_backup_variant"]["sha256"] != observed:
        raise GovernanceError("AION-ready audit observed digest drifted")
    if audit["secret_handling"]["secret_value_recorded_in_audit"] is not False:
        raise GovernanceError("AION-ready audit must not retain secret values")
    if artifact["used_as_source_for_pull_request"] is not False:
        raise GovernanceError("excluded backup variant cannot be a PR source")
    if artifact["merge_blocking"] is not False:
        raise GovernanceError("explicitly excluded backup variant must not remain ambiguous")


def validate_repository_controls(policy: dict[str, Any]) -> None:
    codeowners = require_file(".github/CODEOWNERS")
    for path in ["*", "/spec/", "/contracts/", "/governance/"]:
        if f"{path} @phate6872" not in codeowners:
            raise GovernanceError(f"CODEOWNERS missing {path}")

    pr_template = require_file(".github/pull_request_template.md")
    for heading in [
        "## Change classification",
        "## Authority impact",
        "## Safety boundary",
        "## Governance checklist",
    ]:
        if heading not in pr_template:
            raise GovernanceError(f"PR template missing {heading}")

    require_file(".github/ISSUE_TEMPLATE/rfc.md")
    require_file("GOVERNANCE.md")
    require_file("RELEASE_POLICY.md")
    require_file("SECURITY.md")
    require_file("docs/reconciliation/SPEC_CONTENT_HYGIENE.md")
    require_file("docs/reconciliation/SPEC_CONTENT_HYGIENE.json")
    protection = require_file("docs/governance/BRANCH_PROTECTION.md")
    for check in policy["required_ci_checks"]:
        if check not in protection:
            raise GovernanceError(f"branch protection docs missing check: {check}")


def validate_workflow_and_versioning() -> None:
    workflow = require_file(".github/workflows/ci.yml")
    if '"v*.*.*"' in workflow:
        raise GovernanceError("legacy unscoped tag trigger remains active")
    for pattern in [
        '"standard-v*"',
        '"toolchain-v*"',
        '"contracts-agent-v*"',
    ]:
        if pattern not in workflow:
            raise GovernanceError(f"workflow missing scoped tag trigger {pattern}")
    if "refs/tags/toolchain-v" not in workflow:
        raise GovernanceError("Windows release is not scoped to toolchain tags")
    if "python tools/validate_governance.py" not in workflow:
        raise GovernanceError("governance validator is not enforced by CI")
    if "python tools/validate_hygiene.py" not in workflow:
        raise GovernanceError("hygiene validator is not enforced by CI")

    versioning = require_file("VERSIONING.md")
    for prefix in ["standard-v", "toolchain-v", "contracts-agent-v"]:
        if prefix not in versioning:
            raise GovernanceError(f"versioning docs missing {prefix}")
    if "New unscoped tags are prohibited" not in versioning:
        raise GovernanceError("unscoped-tag prohibition is not frozen")


def main() -> int:
    try:
        policy = validate_policy()
        validate_contract_status(policy)
        validate_evidence_scope()
        validate_repository_controls(policy)
        validate_workflow_and_versioning()
    except (
        GovernanceError,
        FileNotFoundError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS: governance freeze; canonical root non-actuating; "
        "Agent Contracts candidate; recovered evidence identity separated; "
        "scoped release and hygiene policy enforced"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
