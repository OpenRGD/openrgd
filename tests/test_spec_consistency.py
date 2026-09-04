from __future__ import annotations

import json
from pathlib import Path

from openrgd.core.canonical import discover_source_paths
from openrgd.core.utils import strip_jsonc

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"


def load(rel: str) -> dict:
    return json.loads(
        strip_jsonc((SPEC / rel).read_text(encoding="utf-8")), strict=False
    )


def test_current_standard_has_81_canonical_source_files() -> None:
    assert len(discover_source_paths(SPEC)) == 81


def test_active_actuation_bindings_resolve() -> None:
    description = load("01_foundation/description.jsonc")
    library = load("01_foundation/actuation_library.jsonc")
    topology = load("01_foundation/actuation_topology.jsonc")
    dynamics = load("01_foundation/actuation_dynamics.jsonc")
    calibration = load("01_foundation/calibration.jsonc")
    hal = load("01_foundation/hal_mapping.jsonc")

    joints = set(description.get("joint_topology_map", {}))
    models = set(library.get("component_catalog_map", {}))
    profiles = set(topology.get("control_profiles_map", {}))
    active = topology.get("joint_actuator_mapping_map", {})

    assert active
    for actuator_id, record in active.items():
        assert record["target_joint_ref_str"] in joints
        assert record["component_model_ref_str"] in models
        assert record["control_profile_ref_str"] in profiles
        assert record["use_profile_ref_str"] == record["control_profile_ref_str"]
        assert record["binding_status_enum"] == "RESOLVED_REFERENCE_BINDING"

    for record in dynamics.get("joint_dynamics_map", {}).values():
        assert record["target_joint_ref_str"] in joints

    assert set(calibration.get("actuator_calibration_map", {})) <= set(active)
    assert set(hal.get("actuator_drivers_map", {})) <= set(active)


def test_design_actuation_targets_are_not_active_bindings() -> None:
    topology = load("01_foundation/actuation_topology.jsonc")
    targets = topology.get("engineering_design_targets_map", {})
    assert targets
    assert all(item["maturity_enum"] == "ENGINEERING_TARGET" for item in targets.values())
    assert any(
        item["candidate_model_fit_status_enum"] == "TARGET_EXCEEDS_MODEL_PEAK_TORQUE"
        for item in targets.values()
    )
    assert all(
        item["binding_status_enum"] == "UNRESOLVED_REFERENCE_DESCRIPTION"
        for item in targets.values()
    )


def test_low_level_performance_numbers_are_engineering_targets() -> None:
    targets = load("02_operation/control_targets.jsonc")
    meta = targets["meta_group"]
    assert meta["maturity_enum"] == "ENGINEERING_TARGET"
    assert meta["certification_status_enum"] == "NOT_A_CERTIFICATION"
    assert targets["safety_reflex_loop"]["target_frequency_hz_int"] == 1000
    assert targets["safety_reflex_loop"]["target_period_us_int"] == 1000
    assert targets["safety_reflex_loop"]["target_decision_budget_us_int"] == 500
    assert targets["safety_reflex_loop"]["target_sensor_to_safe_action_max_us_int"] == 5000
    assert targets["measurement_contract"]["target_values_must_not_be_reported_as_measured_bool"] is True


def test_safety_and_compliance_do_not_claim_certification() -> None:
    safety = load("02_operation/safety_critical.jsonc")
    compliance = load("02_operation/compliance.jsonc")
    compute = load("01_foundation/compute_topology.jsonc")

    assert safety["meta_group"]["certification_status_enum"] == "NOT_CERTIFIED_BY_OPENRGD_SPEC"
    assert compliance["regulatory_targets_map"]["verification_status_enum"] == "NOT_ASSESSED_BY_OPENRGD_SPEC"
    for node in compute.get("compute_nodes_map", {}).values():
        if "certification_status_enum" in node:
            assert node["certification_status_enum"] == "NOT_ASSERTED_BY_OPENRGD_SPEC"


def test_aion_and_hyperaion_are_representation_not_authority() -> None:
    aion = load("00_core/aion_struct.jsonc")
    hyper = load("04_volition/hyper_aion_semantic_map.jsonc")
    assert aion["meta_group"]["maturity_enum"] == "EXPERIMENTAL_PROTOCOL"
    assert aion["meta_group"]["latency_guarantee_enum"] == "NONE_BY_SPECIFICATION"
    assert "opaque temporal/causal reference" in aion["universal_header_struct"]["fields_ordered_list"][0]["description_str"]
    assert hyper["meta_group"]["maturity_enum"] == "EXPERIMENTAL_PROJECTION"
    assert hyper["projection_contract"]["vector_values_may_authorize_actuation_bool"] is False
    assert hyper["projection_contract"]["hard_invariants_remain_authoritative_bool"] is True


def test_kernel_exposes_the_somatic_safety_boundary() -> None:
    kernel = load("00_core/kernel.jsonc")
    assert kernel["meta_group"]["physical_execution_implemented_here_bool"] is False
    assert kernel["execution_contract"]["stages_ordered_list_enum"] == [
        "ACTION_INTENT",
        "SOMATIC_TRANSLATOR",
        "CAPABILITY_PLAN",
        "OPERATION_SAFETY_GATE",
        "DECISION_TRACE",
        "BODY_ADAPTER",
    ]
    assert kernel["execution_contract"]["cognition_may_bypass_operation_safety_gate_bool"] is False
    assert kernel["execution_contract"]["representation_may_bypass_somatic_translation_bool"] is False
