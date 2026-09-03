from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_hygiene_module():
    module_path = ROOT / "tools/validate_hygiene.py"
    spec = importlib.util.spec_from_file_location("openrgd_validate_hygiene", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_hygiene_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/validate_hygiene.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: repository hygiene" in result.stdout


def test_secret_assignment_parser_does_not_cross_lines() -> None:
    module = _load_hygiene_module()
    template = "OPENAI_API_KEY=\nOPENRGD_ORACLE_MODEL=gpt-4o-mini\n"
    assert list(module.SECRET_ASSIGNMENT.finditer(template)) == []

    fake_value = "sk-" + ("x" * 30)
    matches = list(
        module.SECRET_ASSIGNMENT.finditer(
            f"OPENAI_API_KEY={fake_value}\nOPENRGD_ORACLE_MODEL=gpt-4o-mini\n"
        )
    )
    assert len(matches) == 1
    assert matches[0].group("name") == "OPENAI_API_KEY"
    assert matches[0].group("value") == fake_value


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
        "docs/history/ai-generated-prototypes",
    ]
    for relative in removed:
        assert not (ROOT / relative).exists(), relative

    assert (ROOT / "docs/history/stale-prototypes/README.md").is_file()
    assert (ROOT / "docs/history/stale-prototypes/INVENTORY.json").is_file()


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
