from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from openrgd.core.utils import strip_jsonc
from openrgd.importers.urdf.parser import URDFImporter


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "urdf" / "openrgd_minimal_arm.urdf"


def _jsonc_text(text: str) -> dict:
    return json.loads(strip_jsonc(text), strict=False)


def _jsonc_file(path: Path) -> dict:
    return _jsonc_text(path.read_text(encoding="utf-8"))


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


def test_owned_urdf_fixture_is_hermetic_and_has_provenance() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    provenance = FIXTURE.with_name("PROVENANCE.md")

    assert provenance.is_file()
    assert "SPDX-License-Identifier: MIT" in text
    assert "package://" not in text
    assert "mesh filename=" not in text
    assert "robot_ip" not in text
    assert "/home/" not in text
    assert "/ros" not in text


def test_urdf_importer_emits_only_source_supported_foundation_evidence() -> None:
    importer = URDFImporter(str(FIXTURE))
    imported = importer.parse()

    assert importer.robot_name == "openrgd_minimal_arm"
    assert set(imported) == {
        "spec/01_foundation/description.jsonc",
        "spec/01_foundation/actuation_dynamics.jsonc",
    }
    assert all("00_core" not in path for path in imported)
    assert all("04_volition" not in path for path in imported)
    assert all("alignment" not in text.lower() for text in imported.values())
    assert all(str(FIXTURE.resolve()) not in text for text in imported.values())

    description = _jsonc_text(
        imported["spec/01_foundation/description.jsonc"]
    )
    dynamics = _jsonc_text(
        imported["spec/01_foundation/actuation_dynamics.jsonc"]
    )

    source = description["meta_group"]["source_artifact_map"]
    assert source == {
        "source_filename_str": FIXTURE.name,
        "source_format_enum": "URDF",
        "source_sha256_str": (
            "sha256:" + hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        ),
        "source_size_bytes_int": len(FIXTURE.read_bytes()),
    }

    assert [item["link_id_str"] for item in description["kinematic_chain_list"]] == [
        "base_link",
        "arm_link",
        "slider_link",
        "tool_link",
    ]

    topology = description["joint_topology_map"]
    assert topology["shoulder_joint"]["connectivity"] == {
        "child_link_ref_str": "arm_link",
        "parent_link_ref_str": "base_link",
    }
    assert topology["shoulder_joint"]["limits_ideal"] == {
        "effort_max_nm_float": 4.5,
        "position_lower_rad_float": -1.0,
        "position_upper_rad_float": 1.5,
        "velocity_max_rad_s_float": 2.0,
    }
    assert topology["slide_joint"]["limits_ideal"] == {
        "effort_max_n_float": 50.0,
        "position_lower_m_float": 0.0,
        "position_upper_m_float": 0.2,
        "velocity_max_m_s_float": 0.3,
    }
    assert topology["tool_fixed"]["type_enum"] == "FIXED"

    joint_dynamics = dynamics["joint_dynamics_map"]
    assert set(joint_dynamics) == {"shoulder_joint", "slide_joint"}
    assert joint_dynamics["shoulder_joint"]["joint_limits"] == {
        "max_effort_nm_float": 4.5,
        "max_velocity_rad_s_float": 2.0,
        "soft_max_position_rad_float": 1.5,
        "soft_min_position_rad_float": -1.0,
    }
    assert joint_dynamics["slide_joint"]["joint_limits"] == {
        "max_effort_n_float": 50.0,
        "max_velocity_m_s_float": 0.3,
        "soft_max_position_m_float": 0.2,
        "soft_min_position_m_float": 0.0,
    }


def test_urdf_importer_rejects_non_finite_limits(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.urdf"
    invalid.write_text(
        """<robot name="invalid">
<link name="a"/><link name="b"/>
<joint name="j" type="revolute">
<parent link="a"/><child link="b"/>
<limit effort="nan" velocity="1" lower="-1" upper="1"/>
</joint>
</robot>
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-finite"):
        URDFImporter(str(invalid)).parse()


def test_urdf_import_cli_writes_one_partial_spec_root(tmp_path: Path) -> None:
    output = tmp_path / "partial-rgd"
    result = _run_cli(
        ["import", str(FIXTURE), "--out", str(output)],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    spec = output / "spec"
    assert set(
        path.relative_to(spec).as_posix()
        for path in spec.rglob("*")
        if path.is_file()
    ) == {
        "01_foundation/actuation_dynamics.jsonc",
        "01_foundation/description.jsonc",
    }
    assert not (spec / "spec").exists()
    assert not (spec / "00_core").exists()
    assert not (spec / "02_operation").exists()
    assert not (spec / "04_volition").exists()


def test_urdf_lifecycle_through_deterministic_static_ros2_export(
    tmp_path: Path,
) -> None:
    project = tmp_path / "RGD-openrgd-minimal-arm"

    alive = _run_cli(
        ["alive", str(FIXTURE), "--out", str(project)],
        cwd=tmp_path,
    )
    assert alive.returncode == 0, alive.stdout + alive.stderr

    kernel = _jsonc_file(project / "spec/00_core/kernel.jsonc")
    assert (
        kernel["meta_group"]["id"]
        == "did:rgd:openrgd_minimal_arm"
    )

    source_manifest = _jsonc_file(project / "spec/manifest.jsonc")
    assert (
        source_manifest["meta_group"]["bundle_id_str"]
        == "openrgd_minimal_arm_profile"
    )

    project_manifest = json.loads(
        (project / "manifest.json").read_text(encoding="utf-8")
    )
    assert project_manifest["profile_kind"] == (
        "SEED_ENRICHED_IMPORTED_EVIDENCE"
    )
    assert project_manifest["seed_profile"] == "default"
    assert project_manifest["seed_compatibility_status"] == "UNVERIFIED"
    assert project_manifest["source_artifact"]["source_filename_str"] == (
        FIXTURE.name
    )

    hashed = _run_cli(["hash", ".", "--output", "json"], cwd=project)
    assert hashed.returncode == 0, hashed.stdout + hashed.stderr
    hash_result = json.loads(hashed.stdout)
    assert hash_result["matches"] is True

    checked = _run_cli(["check"], cwd=project)
    assert checked.returncode == 0, checked.stdout + checked.stderr

    booted = _run_cli(["boot", "--output", "json"], cwd=project)
    assert booted.returncode == 0, booted.stdout + booted.stderr
    assert "actuation_dynamics" in booted.stdout

    compiled = _run_cli(
        ["compile-spec", ".", "--output", "json"],
        cwd=project,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    compile_result = json.loads(compiled.stdout)
    bundle_path = project / "spec/openrgd_unified_spec.json"
    assert bundle_path.is_file()
    assert compile_result["bundle_integrity_hash"] == hash_result["computed"]

    export_a = _run_cli(
        [
            "export",
            "ros2",
            "--out",
            "export/ros2-a",
            "--output",
            "json",
        ],
        cwd=project,
    )
    assert export_a.returncode == 0, export_a.stdout + export_a.stderr
    export_result = json.loads(export_a.stdout)
    assert export_result["status"] == "CONFIGURATION_ONLY"
    assert export_result["hardware_binding_complete"] is False

    export_b = _run_cli(
        [
            "export",
            "ros2",
            "--out",
            "export/ros2-b",
            "--output",
            "json",
        ],
        cwd=project,
    )
    assert export_b.returncode == 0, export_b.stdout + export_b.stderr

    directory_a = project / "export/ros2-a"
    directory_b = project / "export/ros2-b"
    manifest = json.loads(
        (directory_a / "export_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["joint_count"] == 2
    assert [item["joint_name"] for item in manifest["joints"]] == [
        "shoulder_joint",
        "slide_joint",
    ]
    assert manifest["hardware_binding"] == {
        "complete": False,
        "driver_plugins": [],
        "missing_joint_bindings": ["shoulder_joint", "slide_joint"],
        "reason": "MISSING_EXPLICIT_HAL_BINDINGS",
    }
    assert not (directory_a / "rgd_hardware.xacro").exists()

    for name in manifest["generated_files"]:
        assert (directory_a / name).read_bytes() == (
            directory_b / name
        ).read_bytes()

    limits = (directory_a / "rgd_limits.xacro").read_text(encoding="utf-8")
    assert 'name="shoulder_joint_effort" value="4.5"' in limits
    assert 'name="slide_joint_effort" value="50"' in limits
    assert "tool_fixed" not in limits

    unavailable = _run_cli(
        ["export", "isaac", "--out", "export/isaac"],
        cwd=project,
    )
    assert unavailable.returncode == 2
    assert not (project / "export/isaac").exists()
