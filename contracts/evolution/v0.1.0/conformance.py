"""Hermetic evolution ABI conformance: synthetic robot only; NO CAN/serial/network/writes."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from validate import ContractError, digest, read_json, validate, validate_chain, validate_transition

S = lambda ch: "sha256:" + ch * 64

def seal(obj):
    obj["record_digest"] = digest(obj)
    return obj

def slot(state="UNKNOWN", model=None, serial=None, condition="UNKNOWN", evidence=()):
    return {
        "slot_id": "arm_right_shoulder",
        "state": state,
        "component_model_ref": model,
        "hardware_serial_claim": serial,
        "condition_claim": condition,
        "mount_xyz_m": None, "mount_rpy_rad": None,
        "link_refs": ["arm_right_shoulder_pitch"],
        "joint_refs": ["arm_right_shoulder_pitch_joint"],
        "sensor_refs": [],
        "evidence_refs": list(evidence),
    }

def common(record_type, record_id):
    return {
        "schema_version":"openrgd.evolution.v0.1-candidate",
        "record_type":record_type,
        "record_id":record_id,
        "record_digest":S("0"),
        "digest_profile":"CANDIDATE_SORTED_JSON_SHA256_V0",
        "robot_instance_ref":"paky-01-synthetic",
        "physical_enrollment_ref":None,
        "actor_claim_ref":"lab-operator",
        "evidence_refs":[],
        "claimed_event_time":{"token":"2026-11-17T09:00:00Z","clock_domain":"operator_wall_clock_claim"},
        "history_commit_receipt_ref":None,
        "grants_authority":False,
        "physical_execution_authorized":False,
        "life_identity_issued":False,
        "history_committed":False,
        "calibration_verified":False,
    }

def build_chain():
    before = {
        **common("AsBuiltRevision", "asbuilt-000"),
        "revision_number":0,
        "previous_revision_ref":None,
        "previous_revision_digest":None,
        "triggering_mutation_ref":None,
        "design_source_root":S("a"),
        "visual_manifest_sha256":S("b"),
        "component_slots":[slot()],
        "calibration_revision_claim":"calibration-before",
        "calibration_status":"UNKNOWN",
        "safety_review_required":False,
        "evidence_class":"OPERATOR_REPORTED_UNVERIFIED",
    }
    seal(before)
    after = {
        **common("AsBuiltRevision", "asbuilt-001"),
        "revision_number":1,
        "previous_revision_ref":before["record_id"],
        "previous_revision_digest":before["record_digest"],
        "triggering_mutation_ref":"mutation-001",
        "design_source_root":S("a"),
        "visual_manifest_sha256":S("c"),
        "component_slots":[slot("INSTALLED_REPORTED", "actuator_5010",
                                "SERIAL_CLAIM_001", "NOMINAL_REPORTED", ("inspection-photo-001",))],
        "calibration_revision_claim":None,
        "calibration_status":"REVIEW_REQUIRED",
        "safety_review_required":True,
        "evidence_class":"OPERATOR_REPORTED_UNVERIFIED",
        "evidence_refs":["inspection-photo-001"],
    }
    seal(after)
    event = {
        **common("HardwareMutationEvent", "mutation-001"),
        "before_revision_ref":before["record_id"],
        "before_revision_digest":before["record_digest"],
        "after_revision_ref":after["record_id"],
        "after_revision_digest":after["record_digest"],
        "design_source_root_before":S("a"),
        "design_source_root_after":S("a"),
        "visual_manifest_before":S("b"),
        "visual_manifest_after":S("c"),
        "change_kind":"INSTALL_COMPONENT",
        "assertion_stage":"INSTALLED_REPORTED_UNVERIFIED",
        "slot_changes":[{
            "slot_id":"arm_right_shoulder",
            "before":deepcopy(before["component_slots"][0]),
            "after":deepcopy(after["component_slots"][0]),
        }],
        "affected_links":["arm_right_shoulder_pitch"],
        "affected_joints":["arm_right_shoulder_pitch_joint"],
        "affected_sensors":[],
        "invalidated_calibration_refs":["calibration-before"],
        "requires_calibration_review":True,
        "requires_safety_review":True,
        "plasticity_governance":{
            "plasticity_policy_ref":"05_evolution/plasticity.jsonc",
            "hardware_mutation_policy_ref":"05_evolution/hardware_mutation.jsonc",
            "policy_source_root_claim":None,
            "human_review_required":True,
            "external_authorization_verified":False
        },
        "evidence_refs":["inspection-photo-001"],
    }
    seal(event)
    return before, event, after

class CandidateEvolutionConformance(unittest.TestCase):
    def setUp(self):
        self.before, self.event, self.after = build_chain()

    def test_reference_chain_and_no_positive_authority(self):
        for obj in (self.before,self.event,self.after):
            self.assertIs(validate(obj),obj)
        result = validate_transition(self.before,self.event,self.after)
        self.assertEqual(result["status"],"CONSISTENT_UNVERIFIED")
        self.assertFalse(result["physical_truth_verified"])
        self.assertFalse(result["history_written"])
        self.assertFalse(result["life_verified"])
        self.assertFalse(result["authorization_granted"])
        self.assertEqual(validate_chain([self.before,self.after],[self.event])["revisions"],2)

    def test_pure_visual_asset_replacement_never_mutates_physical_body(self):
        # Visual-only change is a different visual manifest revision, not a
        # HardwareMutationEvent or a new AsBuiltRevision.
        proposed = deepcopy(self.event)
        proposed["slot_changes"][0]["after"] = deepcopy(proposed["slot_changes"][0]["before"])
        seal(proposed)
        with self.assertRaisesRegex(ContractError,"VISUAL_OR_EVIDENCE_ONLY_MUTATION"):
            validate(proposed)
        self.assertEqual(self.before["record_id"],"asbuilt-000")

    def test_unknown_or_stale_calibration_must_not_survive_component_replacement(self):
        after=deepcopy(self.after)
        after["calibration_revision_claim"]="calibration-before"
        seal(after)
        with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):
            validate(after)
        event=deepcopy(self.event)
        event["invalidated_calibration_refs"]=[]
        seal(event)
        with self.assertRaisesRegex(ContractError,"STALE_CALIBRATION_NOT_INVALIDATED"):
            validate_transition(self.before,event,self.after)

    def test_different_robot_or_enrollment_not_inherited(self):
        after=deepcopy(self.after)
        after["robot_instance_ref"]="other-robot"
        seal(after)
        with self.assertRaisesRegex(ContractError,"ROBOT_CONTEXT_MISMATCH"):
            validate_transition(self.before,self.event,after)
        after=deepcopy(self.after)
        after["physical_enrollment_ref"]="reported-enrollment-xyz"
        seal(after)
        with self.assertRaisesRegex(ContractError,"ROBOT_CONTEXT_MISMATCH"):
            validate_transition(self.before,self.event,after)

    def test_changed_revision_without_new_link_is_rejected(self):
        after=deepcopy(self.after)
        after["previous_revision_digest"]=S("f")
        seal(after)
        with self.assertRaisesRegex(ContractError,"BROKEN_REVISION_LINK"):
            validate_transition(self.before,self.event,after)
        after=deepcopy(self.after)
        after["revision_number"]=2
        seal(after)
        event=deepcopy(self.event)
        event["after_revision_digest"]=after["record_digest"]
        seal(event)
        with self.assertRaisesRegex(ContractError,"NONSEQUENTIAL_REVISION"):
            validate_transition(self.before,event,after)

    def test_reordering_and_duplicate_history_fails(self):
        with self.assertRaisesRegex(ContractError,"NO_GENESIS_REVISION"):
            validate_chain([self.after,self.before],[self.event])
        extra=deepcopy(self.after)
        with self.assertRaisesRegex(ContractError,"DUPLICATE_RECORD_ID"):
            validate_chain([self.before,self.after,extra],[self.event,self.event])

    def test_life_rin_or_self_granted_permission_is_never_accepted(self):
        for attr,value in (
            ("grants_authority",True),("physical_execution_authorized",True),
            ("life_identity_issued",True),("history_committed",True),
            ("calibration_verified",True),("life_id","fabricated-life"),
            ("rin","invented-rin")
        ):
            with self.subTest(attr=attr):
                item=deepcopy(self.after)
                item[attr]=value
                seal(item)
                with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):
                    validate(item)

    def test_plasticity_policy_reference_cannot_grant_mutation(self):
        event=deepcopy(self.event)
        event["plasticity_governance"]["external_authorization_verified"]=True
        seal(event)
        with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):
            validate(event)
        event=deepcopy(self.event)
        event["plasticity_governance"]["plasticity_policy_ref"]="other_unsafe_policy"
        seal(event)
        with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):
            validate(event)

    def test_proposed_event_has_no_result_snapshot(self):
        event=deepcopy(self.event)
        event["assertion_stage"]="PROPOSED"
        seal(event)
        with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):
            validate(event)
        event["after_revision_ref"]=None
        event["after_revision_digest"]=None
        seal(event)
        validate(event)
        with self.assertRaisesRegex(ContractError,"PROPOSAL_NOT_INSTALLATION"):
            validate_transition(self.before,event,self.after)

    def test_undeclared_joint_impact_or_extra_mutation_is_rejected(self):
        event=deepcopy(self.event)
        event["affected_joints"]=[]
        seal(event)
        with self.assertRaisesRegex(ContractError,"IMPACT_UNDERDECLARED"):
            validate(event)
        event=deepcopy(self.event)
        event["slot_changes"].append(deepcopy(event["slot_changes"][0]))
        seal(event)
        with self.assertRaisesRegex(ContractError,"DUPLICATE_SLOT_CHANGE"):
            validate(event)

    def test_malformed_snapshot_slots(self):
        before=deepcopy(self.before)
        before["component_slots"].append(deepcopy(before["component_slots"][0]))
        seal(before)
        with self.assertRaisesRegex(ContractError,"DUPLICATE_SLOT"):
            validate(before)
        before=deepcopy(self.before)
        before["component_slots"][0]["hardware_serial_claim"]="SERIAL_NOT_INSTALLED"
        seal(before)
        with self.assertRaisesRegex(ContractError,"UNKNOWN_SLOT_HAS_HARDWARE"):
            validate(before)

    def test_genesis_and_new_slot_are_supported_without_fake_prior_hardware(self):
        before=deepcopy(self.before)
        before["component_slots"]=[]
        seal(before)
        after=deepcopy(self.after)
        after["previous_revision_digest"]=before["record_digest"]
        seal(after)
        event=deepcopy(self.event)
        event["before_revision_digest"]=before["record_digest"]
        event["after_revision_digest"]=after["record_digest"]
        event["slot_changes"][0]["before"]=None
        seal(event)
        self.assertEqual(validate_transition(before,event,after)["revision_number"],1)

    def test_record_and_zip_mutation_replay_tampering_detected(self):
        after=deepcopy(self.after)
        after["component_slots"][0]["hardware_serial_claim"]="DIFFERENT"
        with self.assertRaisesRegex(ContractError,"DIGEST_MISMATCH"):
            validate(after)
        event=deepcopy(self.event)
        event["slot_changes"][0]["after"]["hardware_serial_claim"]="DIFFERENT"
        seal(event)
        with self.assertRaisesRegex(ContractError,"DELTA_DOES_NOT_MATCH_SNAPSHOTS"):
            validate_transition(self.before,event,self.after)

    def test_nonfinite_bounded_input_and_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"input.json"
            target.write_text('{"record_type":"AsBuiltRevision","record_type":"HardwareMutationEvent"}')
            with self.assertRaisesRegex(ContractError,"DUPLICATE_KEY"):
                read_json(target)
            target.write_text('{"x":NaN}')
            with self.assertRaisesRegex(ContractError,"NONFINITE"):
                read_json(target)
            target.write_bytes(b" " * 131073)
            with self.assertRaisesRegex(ContractError,"SIZE_LIMIT"):
                read_json(target)
            target.write_bytes(b"\xff")
            with self.assertRaisesRegex(ContractError,"JSON_READ_FAILED"):
                read_json(target)

    def test_anything_that_looks_like_time_or_history_receipt_remains_unverified(self):
        item=deepcopy(self.event)
        item["history_commit_receipt_ref"]="unverified-history-receipt"
        item["claimed_event_time"]["token"]="1990-01-01T00:00:00Z"
        seal(item)
        self.assertEqual(validate(item)["history_committed"],False)
        self.assertEqual(validate_transition(self.before,item,self.after)["history_written"],False)

if __name__ == "__main__":
    unittest.main(verbosity=2)
