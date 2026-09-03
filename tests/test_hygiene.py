from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repository_hygiene_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/validate_hygiene.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: repository hygiene" in result.stdout


def test_secret_files_are_ignored_and_not_tracked_as_examples() -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "\n.env\n" in f"\n{ignore}"
    assert ".env.*" in ignore
    assert "!.env.example" in ignore
    assert "!.env.template" in ignore


def test_removed_promotional_and_plugin_surfaces_stay_absent() -> None:
    removed = [
        "Dockerfile",
        "ENTHUSIAST.md",
        "GUIDE_DOCKER.md",
        "MAINTENANCE.md",
        "ONBOARDING.md",
        "PLUGIN_GUIDE.md",
        "plugins.toml",
        "plugins",
        "assets/branding/proposal",
        "src/openrgd/commands/plugins.py",
        "src/openrgd/core/command_registry.py",
        "src/openrgd/core/plugins_policy.py",
        "src/rgd_schema.jsonc",
    ]
    for relative in removed:
        assert not (ROOT / relative).exists(), relative


def test_recovered_aion_backup_is_not_mislabeled_as_original_archive() -> None:
    audit = json.loads(
        (ROOT / "docs/reconciliation/AION_READY_BACKUP_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    expected = audit["historical_expected_archive"]["sha256"]
    observed = audit["uploaded_backup_variant"]["sha256"]
    assert expected != observed
    assert audit["identity_comparison"]["byte_identity_with_historical_archive_proven"] is False
    assert audit["identity_comparison"]["only_env_difference_proven"] is False
    assert audit["secret_handling"]["secret_value_recorded_in_audit"] is False
    assert audit["secret_handling"]["credential_rotation_required"] is True
    assert audit["reconciliation_decision"]["used_as_source_for_pull_request_1"] is False


def test_active_toolchain_metadata_has_no_unverified_contact() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    main = (ROOT / "src/openrgd/main.py").read_text(encoding="utf-8")
    unverified_domain = "openrgd" + ".org"
    assert ("@" + unverified_domain) not in pyproject
    assert "Cognitive BIOS" not in pyproject
    assert "Cognitive BIOS" not in main
