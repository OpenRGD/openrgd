"""CORE-RI-01 characterization tests ONLY. Never use this file as an authority gate.

Imports the actual pinned RI producer in isolated synthetic temporary stores.
Core selectors are checked as shapes; there is no production resolver/writer.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator
from reality_ingress.consumer_ref import (
    unverified_ref_from_envelope, verified_ref_from_store,
)
from reality_ingress.evidence import EvidenceStore, IntegrityError
from reality_ingress.generic import SAMPLE_SCHEMA, record_sample
from reality_ingress.derivations import DerivationStore

RI = Path(os.environ["RI_CHECKOUT"])
BASE = Path(__file__).resolve().parents[3]
B = Path(os.environ["CORE_B_CHECKOUT"])
C = Path(os.environ["CORE_C_CHECKOUT"])
D = Path(os.environ["CORE_D_CHECKOUT"])
RI_SCHEMA_PATH = RI / "contracts/consumer-observation-ref.v0.1-candidate.schema.json"
RI_SCHEMA_RAW = RI_SCHEMA_PATH.read_bytes()
EXPECTED_RI_BLOB = "3d92e074e71593bf6db0a735394c628ea131668d"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def checked_schema(path):
    schema = read(path)
    Draft202012Validator.check_schema(schema)
    return schema

def selector(schema, kind):
    return Draft202012Validator({
        "$schema": schema["$schema"], "$defs": schema["$defs"],
        "$ref": "#/$defs/" + kind,
    })

RI_SCHEMA = json.loads(RI_SCHEMA_RAW)
Draft202012Validator.check_schema(RI_SCHEMA)
RV = Draft202012Validator(RI_SCHEMA)
BS = checked_schema(B / "contracts/kernel/v0.1.0/schemas/kernel-goal-effect.schema.json")
CS = checked_schema(C / "contracts/identity/v0.1.0/schemas/identity.schema.json")
DS = checked_schema(D / "contracts/temporal-memory/v0.1.0/schemas/temporal-memory.schema.json")
DPOS = read(D / "contracts/temporal-memory/v0.1.0/fixtures/positive.json")["records"]

def stamp(boot="fixture-boot", receipt=9007199254740993):
    # Deliberately synthetic receipt > JS's max safe integer; no real clock claim.
    return {
        "received_monotonic_ns": receipt,
        "received_unix_estimate_ns": 100000000000,
        "host_wall_pair_span_ns": 100,
        "clock_domain_ref": {
            "clock_kind_enum_str": "MONOTONIC",
            "clock_domain_id_str": "fixture.monotonic:" + boot,
            "boot_id_str": boot,
        },
        "source_time": None,
        "source_time_status_str": "UNKNOWN_NOT_EXPOSED_BY_SOURCE",
    }

def sample(session="fixture-session-one", boot="fixture-boot"):
    return {
        "schema_ref_str": SAMPLE_SCHEMA,
        "producer_str": "fixture-only",
        "source": {
            "source_id_str": "fixture.imu", "modality_str": "imu",
            "reference_frame_id_str": "fixture.frame", "sample_sequence_uint": 1,
            "session_id_str": session,
        },
        "temporal_binding": stamp(boot),
        "payload": {"measurements": {"x": 1}},
    }

class ActualProducerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = EvidenceStore(Path(self.tmp.name) / "evidence")

    def camera(self):
        return self.store.record(
            data=b"synthetic-only fixture, not a decoded camera image",
            source_id="fixture.camera", modality="rgb", reference_frame_id="fixture.camera.frame",
            sequence=1, timestamp=stamp(), media_type="image/jpeg",
            representation={"kind_str": "synthetic_fixture"},
        )

    def ref(self, env):
        ref = verified_ref_from_store(self.store, env["observation_id_str"])
        RV.validate(ref)
        return ref

    def test_exact_ri_schema_pin(self):
        blob = hashlib.sha1(b"blob " + str(len(RI_SCHEMA_RAW)).encode() + b"\0" + RI_SCHEMA_RAW)
        self.assertEqual(blob.hexdigest(), EXPECTED_RI_BLOB)

    def test_camera_id_hash_and_receipt_preserved(self):
        env = self.camera()
        before = deepcopy(env)
        ref = self.ref(env)
        self.assertEqual(env, before)
        self.assertEqual(ref["observation_id"], env["observation_id_str"])
        self.assertEqual(ref["payload_sha256_hex"], env["evidence"]["payload_sha256_hex_str"])
        self.assertEqual(ref["integrity_status"], "verified_local_hash")
        self.assertEqual(ref["time"]["received_monotonic_ns"], 9007199254740993)
        self.assertEqual(json.loads(json.dumps(ref)), ref)
        self.assertEqual(ref["origin_status"], "unknown")
        for flag in ("source_verified", "robot_binding_verified", "history_committed", "actuation_enabled"):
            self.assertIs(ref[flag], False)
        for key in ("source_measurement_time", "chronograf_anchor_ref"):
            self.assertIsNone(ref["time"][key])
        self.assertNotIn("payload_ref_str", ref)
        self.assertNotIn("session_id", ref)

    def test_unverified_projection_has_no_verified_hash(self):
        env = self.camera()
        ref = unverified_ref_from_envelope(env)
        RV.validate(ref)
        self.assertEqual(ref["integrity_status"], "not_verified")

    def test_generic_replay_and_session_collision(self):
        row = sample()
        one, created = record_sample(self.store, row)
        self.assertTrue(created)
        again, created = record_sample(self.store, row)
        self.assertFalse(created)
        self.assertEqual(again, one)
        two, _ = record_sample(self.store, sample("fixture-session-two"))
        self.assertNotEqual(one["observation_id_str"], two["observation_id_str"])
        a, b = self.ref(one), self.ref(two)
        self.assertEqual((a["source_id"], a["sample_sequence"]), (b["source_id"], b["sample_sequence"]))
        self.assertEqual(one["source"]["session_id_str"], "fixture-session-one")
        self.assertNotIn("session_id", a)
        self.assertNotIn("session_id", b)

    def test_different_boot_not_a_global_order(self):
        one, _ = record_sample(self.store, sample())
        two, _ = record_sample(self.store, sample(boot="another-boot"))
        a, b = self.ref(one)["time"], self.ref(two)["time"]
        self.assertEqual(a["received_monotonic_ns"], b["received_monotonic_ns"])
        self.assertNotEqual(a["clock_domain_id"], b["clock_domain_id"])
        self.assertIsNone(a["chronograf_anchor_ref"])
        self.assertIsNone(b["chronograf_anchor_ref"])

    def test_camera_metadata_gap_characterization(self):
        # Test-only edit to a private temporary fixture: legacy camera ID is
        # UUID-like and before any derivations verify() checks payload, not a
        # committed source metadata record. This PASS is a known limitation.
        env = self.camera()
        original = self.ref(env)
        p = self.store.observations / (env["observation_id_str"] + ".json")
        changed = deepcopy(env)
        changed["source"]["source_id_str"] = "fixture.changed-unverified-source"
        p.write_text(json.dumps(changed), encoding="utf-8")
        later = self.ref(changed)
        self.assertEqual(original["observation_id"], later["observation_id"])
        self.assertEqual(original["payload_sha256_hex"], later["payload_sha256_hex"])
        self.assertNotEqual(original["source_id"], later["source_id"])
        self.assertFalse(later["source_verified"])

    def test_generic_metadata_change_detected(self):
        env, _ = record_sample(self.store, sample())
        p = self.store.observations / (env["observation_id_str"] + ".json")
        env["source"]["source_id_str"] = "fixture.changed-unverified-source"
        p.write_text(json.dumps(env), encoding="utf-8")
        with self.assertRaises(IntegrityError):
            verified_ref_from_store(self.store, env["observation_id_str"])

    def test_deleted_payload_does_not_resolve(self):
        env = self.camera()
        self.ref(env)
        self.store._payload_path(env["evidence"]["payload_sha256_hex_str"]).unlink()
        with self.assertRaises(IntegrityError):
            verified_ref_from_store(self.store, env["observation_id_str"])

    def test_derivation_is_not_an_observation_ref(self):
        env = self.camera()
        path = self.store.observations / (env["observation_id_str"] + ".json")
        before = path.read_bytes()
        processor = {"processor_name_str": "synthetic-only"}
        der = DerivationStore(self.store).create(
            observation_id=env["observation_id_str"], processor=processor,
            detections=[],
        )
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(der["derived_from"]["observation_id_str"], env["observation_id_str"])
        self.assertEqual(der["derived_from"]["observation_envelope_sha256_hex_str"],
                         hashlib.sha256(before).hexdigest())
        self.assertFalse(RV.is_valid(der))
        self.ref(env)

    def test_detector_cannot_label_self(self):
        env = self.camera()
        with self.assertRaisesRegex(ValueError, "SELF"):
            DerivationStore(self.store).create(
                observation_id=env["observation_id_str"],
                processor={"processor_name_str": "fixture"},
                detections=[{"class_label_str": "SELF", "confidence_float": 1.0,
                             "bbox_xyxy_normalized_arr": [0.1, 0.1, 0.9, 0.9]}],
            )

    def test_source_cannot_assert_agent_relation(self):
        row = sample()
        row["source"]["self_relation"] = "fixture"
        with self.assertRaises(ValueError):
            record_sample(self.store, row)

    def test_schema_negative_flags_and_foreign_fields(self):
        ref = self.ref(self.camera())
        for key in ("source_verified", "robot_binding_verified", "history_committed", "actuation_enabled"):
            with self.subTest(key=key):
                self.assertFalse(RV.is_valid({**ref, key: True}))
        for key in ("life_id", "robot_instance_id", "chronon_id", "can_command", "payload_path", "session_id"):
            with self.subTest(key=key):
                self.assertFalse(RV.is_valid({**ref, key: "fixture:not-an-authority"}))
        for field in ("chronograf_anchor_ref", "source_measurement_time"):
            tampered = deepcopy(ref)
            tampered["time"][field] = "fixture:invented"
            self.assertFalse(RV.is_valid(tampered))

    def test_origin_claim_enum_not_producer_attestation(self):
        ref = self.ref(self.camera())
        claimed = {**ref, "origin_status": "source_claimed_physical"}
        RV.validate(claimed)  # permitted *claim*, not proof
        self.assertIs(claimed["source_verified"], False)
        self.assertEqual(ref["origin_status"], "unknown")

    def test_ref_not_core_authority_or_history_record(self):
        ref = self.ref(self.camera())
        for schema, kinds in (
            (BS, ("KernelEvent", "CognitiveGoalCandidate", "EffectRequest", "EffectGateDecision")),
            (CS, ("LifeIdentity", "RobotLifeBinding", "RuntimeInstance", "RoleLease")),
            (DS, ("HistoricalTimeAssertion", "ImportAnchorEvidence", "EvidenceAvailability",
                  "MemoryAnnotation", "HistoryCommitRequest", "HistoryCommitReceipt")),
        ):
            for kind in kinds:
                with self.subTest(kind=kind):
                    self.assertFalse(selector(schema, kind).is_valid(ref))

    def test_legacy_core_projection_is_not_ri_ref(self):
        projection = checked_schema(BASE / "contracts/agent/v0.1.0/schemas/memory-projection.schema.json")
        self.assertFalse(Draft202012Validator(projection).is_valid(self.ref(self.camera())))

class CoreGapTests(unittest.TestCase):
    def test_observation_payload_kind_is_not_supported(self):
        validator = selector(DS, "HistoryCommitRequest")
        request = deepcopy(DPOS["request"])
        validator.validate(request)
        for kind in ("OBSERVATION", "OBSERVATION_EVIDENCE_LINK", "PERCEPTION_RESULT", "LIFECYCLE_REPORT"):
            with self.subTest(kind=kind):
                self.assertFalse(validator.is_valid({**request, "payload_kind": kind}))

    def test_legacy_import_requires_separate_assertion_and_anchor(self):
        validator = selector(DS, "HistoryCommitRequest")
        request = {**DPOS["request"], "payload_kind": "LEGACY_IMPORT"}
        self.assertIsNone(request["historical_time_assertion_ref"])
        self.assertIsNone(request["import_anchor_evidence_ref"])
        self.assertFalse(validator.is_valid(request))

    def test_unknown_availability_is_not_available(self):
        validator = selector(DS, "EvidenceAvailability")
        record = deepcopy(DPOS["evidence"])
        validator.validate(record)
        self.assertFalse(validator.is_valid({**record, "reported_state": "UNKNOWN"}))
        self.assertFalse(validator.is_valid({**record, "reported_state": "ERASED"}))

    def test_unbound_history_request_rejected(self):
        validator = selector(DS, "HistoryCommitRequest")
        for field in ("life_id", "life_binding_ref", "writer_role_lease_ref", "effect_gate_decision_ref"):
            with self.subTest(field=field):
                self.assertFalse(validator.is_valid({**DPOS["request"], field: None}))

    def test_unconfirmed_receipt_cannot_claim_chronon(self):
        validator = selector(DS, "HistoryCommitReceipt")
        report = DPOS["unconfirmed"]
        validator.validate(report)
        for field in ("committed_chronon_ref", "history_watermark_ref", "recorded_anchor_ref", "writer_receipt_ref"):
            with self.subTest(field=field):
                self.assertFalse(validator.is_valid({**report, field: "fixture:invented"}))

    def test_shape_valid_commit_is_only_a_claim(self):
        # Actual upstream synthetic receipt is structurally valid. We do not
        # authenticate it, resolve it or use it to emit a second record.
        receipt = DPOS["receipt"]
        selector(DS, "HistoryCommitReceipt").validate(receipt)
        self.assertEqual(receipt["reporter_class"], "WRITER_CLAIM")
        self.assertFalse(receipt["grants_authority"])

    def test_all_core_families_still_candidate(self):
        for root, family in ((B, "kernel"), (C, "identity"), (D, "temporal-memory")):
            status = read(root / ("contracts/" + family + "/v0.1.0/STATUS.json"))
            self.assertEqual(status["maturity"], "candidate")
            for key in ("accepted", "normative", "runtime_implemented"):
                self.assertIs(status[key], False)

if __name__ == "__main__":
    unittest.main(verbosity=2)
