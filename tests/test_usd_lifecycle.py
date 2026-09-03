from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

import pytest

from openrgd.core.utils import strip_jsonc
from openrgd.importers.usd.parser import USDImporter


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "usd" / "openrgd_minimal_arm.usda"


def _jsonc_text(text: str) -> dict:
    return json.loads(strip_jsonc(text), strict=False)


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


def test_owned_usda_fixture_is_hermetic_and_has_provenance() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    provenance = FIXTURE.with_name("PROVENANCE.md")

    assert provenance.is_file()
    assert "SPDX-License-Identifier: MIT" in text
    assert "@" not in text
    assert "asset " not in text
    assert "payload " not in text
    assert "reference" not in text.lower()
    assert "package://" not in text
    assert "/home/" not in text
    assert "robot_ip" not in text


def test_usda_importer_converts_authored_stage_units_without_defaults() -> None:
    importer = USDImporter(str(FIXTURE))
    imported = importer.parse()

    assert importer.robot_name == "OpenRGDUsdArm"
    assert set(imported) == {
        "spec/01_foundation/description.jsonc",
        "spec/01_foundation/actuation_dynamics.jsonc",
    }
    assert all("00_core" not in path for path in imported)
    assert all("04_volition" not in path for path in imported)
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
        "source_format_enum": "USD_ASCII",
        "source_sha256_str": (
            "sha256:" + hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        ),
        "source_size_bytes_int": len(FIXTURE.read_bytes()),
    }
    stage = description["meta_group"]["source_stage_metadata_map"]
    assert stage == {
        "angular_unit_enum": "DEGREE",
        "default_prim_str": "OpenRGDUsdArm",
        "kilograms_per_unit_float": 1.0,
        "meters_per_unit_float": 0.01,
        "source_profile_str": "OPENUSD_USDA_LIGHTWEIGHT_V1",
        "up_axis_enum": "Z",
    }

    topology = description["joint_topology_map"]
    shoulder = topology["shoulder_joint"]
    assert shoulder["type_enum"] == "REVOLUTE"
    assert shoulder["geometry_ideal"]["axis_xyz_vec3_float"] == [0.0, 1.0, 0.0]
    assert shoulder["limits_ideal"] == pytest.approx(
        {
            "effort_max_nm_float": 4.5,
            "position_lower_rad_float": -math.pi / 2,
            "position_upper_rad_float": math.pi / 4,
        }
    )
    source_joint = shoulder["source_usd_joint_map"]
    assert source_joint["body0_prim_path_str"] == "/OpenRGDUsdArm/base_link"
    assert source_joint["body1_prim_path_str"] == "/OpenRGDUsdArm/arm_link"
    assert source_joint["source_position_unit_enum"] == "DEGREE"
    assert source_joint["source_reference_frames_map"]["frame_0"][
        "position_m_vec3_float"
    ] == [0.0, 0.0, 0.1]

    slide = topology["slide_joint"]
    assert slide["type_enum"] == "PRISMATIC"
    assert slide["geometry_ideal"]["axis_xyz_vec3_float"] == [1.0, 0.0, 0.0]
    assert slide["limits_ideal"] == pytest.approx(
        {
            "effort_max_n_float": 50.0,
            "position_lower_m_float": 0.0,
            "position_upper_m_float": 0.2,
        }
    )
    assert (
        slide["source_usd_joint_map"]["source_position_unit_enum"]
        == "STAGE_DISTANCE_UNIT"
    )

    joint_dynamics = dynamics["joint_dynamics_map"]
    assert joint_dynamics["shoulder_joint"]["joint_limits"] == pytest.approx(
        {
            "max_effort_nm_float": 4.5,
            "soft_max_position_rad_float": math.pi / 4,
            "soft_min_position_rad_float": -math.pi / 2,
        }
    )
    assert joint_dynamics["slide_joint"]["joint_limits"] == pytest.approx(
        {
            "max_effort_n_float": 50.0,
            "soft_max_position_m_float": 0.2,
            "soft_min_position_m_float": 0.0,
        }
    )


def test_usda_missing_values_remain_absent(tmp_path: Path) -> None:
    source = tmp_path / "unbounded.usda"
    source.write_text(
        """#usda 1.0
def PhysicsRevoluteJoint "free_joint"
{
    rel physics:body0 = </a>
    rel physics:body1 = </b>
}
""",
        encoding="utf-8",
    )

    imported = USDImporter(str(source)).parse()
    description = _jsonc_text(
        imported["spec/01_foundation/description.jsonc"]
    )
    dynamics = _jsonc_text(
        imported["spec/01_foundation/actuation_dynamics.jsonc"]
    )

    assert "limits_ideal" not in description["joint_topology_map"]["free_joint"]
    assert "joint_limits" not in dynamics["joint_dynamics_map"]["free_joint"]


def test_usda_prismatic_conversion_requires_authored_meters_per_unit(
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing-units.usda"
    source.write_text(
        """#usda 1.0
def PhysicsPrismaticJoint "slide"
{
    float physics:lowerLimit = 0
    float physics:upperLimit = 1
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="metersPerUnit"):
        USDImporter(str(source)).parse()


def test_usda_non_finite_values_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "invalid.usda"
    source.write_text(
        """#usda 1.0
(
    metersPerUnit = nan
)
def PhysicsRevoluteJoint "joint"
{
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-finite"):
        USDImporter(str(source)).parse()


def test_usda_import_cli_writes_one_partial_spec_root(tmp_path: Path) -> None:
    output = tmp_path / "partial-usd"
    result = _run_cli(
        ["import", str(FIXTURE), "--out", str(output)],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    spec = output / "spec"
    assert {
        path.relative_to(spec).as_posix()
        for path in spec.rglob("*")
        if path.is_file()
    } == {
        "01_foundation/actuation_dynamics.jsonc",
        "01_foundation/description.jsonc",
    }
    assert not (spec / "spec").exists()
    assert not (spec / "00_core").exists()
    assert not (spec / "04_volition").exists()


def test_usda_lifecycle_reaches_deterministic_configuration_only_export(
    tmp_path: Path,
) -> None:
    project = tmp_path / "RGD-OpenRGDUsdArm"
    alive = _run_cli(
        ["alive", str(FIXTURE), "--out", str(project)],
        cwd=tmp_path,
    )
    assert alive.returncode == 0, alive.stdout + alive.stderr

    checked = _run_cli(["check", "--output", "json"], cwd=project)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    check_payload = json.loads(checked.stdout)
    assert check_payload["status"] == "VALID"
    assert check_payload["physical_execution_assessed"] is False

    booted_a = _run_cli(["boot", "--output", "json"], cwd=project)
    booted_b = _run_cli(["boot", "--output", "json"], cwd=project)
    assert booted_a.returncode == 0, booted_a.stdout + booted_a.stderr
    assert booted_a.stdout == booted_b.stdout
    context = json.loads(booted_a.stdout)
    assert context["physical_execution"]["authorized"] is False
    assert context["summary"]["described_joints_count"] == 2

    compiled = _run_cli(
        ["compile-spec", ".", "--output", "json"],
        cwd=project,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr

    export_a = _run_cli(
        [
            "export",
            "ros2",
            "--out",
            "export/usd-a",
            "--output",
            "json",
        ],
        cwd=project,
    )
    export_b = _run_cli(
        [
            "export",
            "ros2",
            "--out",
            "export/usd-b",
            "--output",
            "json",
        ],
        cwd=project,
    )
    assert export_a.returncode == 0, export_a.stdout + export_a.stderr
    assert export_b.returncode == 0, export_b.stdout + export_b.stderr
    result = json.loads(export_a.stdout)
    assert result["status"] == "CONFIGURATION_ONLY"
    assert result["hardware_binding_complete"] is False

    directory_a = project / "export/usd-a"
    directory_b = project / "export/usd-b"
    manifest = json.loads(
        (directory_a / "export_manifest.json").read_text(encoding="utf-8")
    )
    assert [item["joint_name"] for item in manifest["joints"]] == [
        "shoulder_joint",
        "slide_joint",
    ]
    for name in manifest["generated_files"]:
        assert (directory_a / name).read_bytes() == (
            directory_b / name
        ).read_bytes()
