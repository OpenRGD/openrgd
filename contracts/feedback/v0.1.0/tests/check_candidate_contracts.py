"""Candidate Feedback schema fixture checks — no peripheral/audio access.

Requires 'jsonschema' only when explicitly running this candidate suite;
it is not a runtime dependency of the canonical RGD toolchain.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLE = ROOT / "examples" / "feedback-flow.synthetic.json"
FILES = {
    "signal": "feedback-signal.v0.1.schema.json",
    "cue": "feedback-cue.v0.1.schema.json",
    "capabilities": "feedback-capabilities.v0.1.schema.json",
    "delivery": "feedback-delivery.v0.1.schema.json",
}
CHECKER = FormatChecker()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class FeedbackContractsCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = {}
        for key, filename in FILES.items():
            schema = read_json(SCHEMAS / filename)
            Draft202012Validator.check_schema(schema)
            cls.validators[key] = Draft202012Validator(schema, format_checker=CHECKER)
        cls.fixtures = read_json(EXAMPLE)["cases"]

    def check(self, key: str, data: dict):
        self.validators[key].validate(data)

    def test_status_is_explicit_candidate(self):
        status = read_json(ROOT / "STATUS.json")
        self.assertEqual(status["maturity"], "candidate")
        self.assertFalse(status["normative"])
        self.assertFalse(status["accepted"])

    def test_synthetic_reference_flow_shapes(self):
        self.assertEqual(len(self.fixtures), 2)
        for flow in self.fixtures:
            with self.subTest(flow=flow["name"]):
                signal, cue = flow["signal"], flow["cue"]
                self.check("signal", signal)
                self.check("cue", cue)
                self.assertEqual(cue["source_signal_id"], signal["signal_id"])
                self.assertEqual(cue["robot_instance_id"], signal["robot_instance_id"])
                capabilities = flow["capabilities"]
                for caps in capabilities:
                    self.check("capabilities", caps)
                self.assertEqual(len(set((c["peripheral_id"], c["zone_id"]) for c in capabilities)), len(capabilities))
                for result in flow["delivery"]:
                    self.check("delivery", result)
                    self.assertEqual(result["cue_id"], cue["cue_id"])
                    self.assertEqual(result["robot_instance_id"], cue["robot_instance_id"])
                    self.assertIn(result["modality"], cue["modalities"])
                    matching = [c for c in capabilities
                                if c["peripheral_id"] == result["peripheral_id"]
                                and c["zone_id"] == result["zone_id"]
                                and c["modality"] == result["modality"]]
                    self.assertEqual(len(matching), 1)
                    self.assertIn(result["effect_id"], matching[0]["effect_ids"])
                    self.assertFalse(result["physical_output_observed"])

    def test_fail_closed_on_bad_priority_ttl_or_scope(self):
        cue = self.fixtures[0]["cue"]
        invalids = [
            {"priority": True},
            {"priority": 101},
            {"ttl_ms": 0},
            {"modalities": ["visual", "visual"]},
            {"delivery_policy": "safety_override"},
            {"safety_authority": True},
            {"arbitrary_command": ["exec", "shell"]},
        ]
        for patch in invalids:
            with self.subTest(patch=patch):
                changed = {**cue, **patch}
                with self.assertRaises(ValidationError):
                    self.check("cue", changed)

    def test_reject_physical_proof_from_driver_ack(self):
        result = self.fixtures[0]["delivery"][0]
        bad = [
            {"physical_output_observed": True},
            {"physical_observation_ref": "invented"},
            {"driver_acknowledged": False, "stage": "driver_ack"},
            {"driver_acknowledged": True, "stage": "queued"},
            {"error_code": "/etc/passwd"},
        ]
        for patch in bad:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                self.check("delivery", {**result, **patch})

    def test_never_encode_hardware_addresses_or_cross_modal_effects(self):
        caps = self.fixtures[0]["capabilities"][0]
        bad = [
            {"mac": "00:00:00:00:00:00"},
            {"physical_endpoint_disclosed": True},
            {"effect_ids": ["audio.earcon"]},
            {"limits": {**caps["limits"], "strobe_enabled": True}},
            {"limits": {**caps["limits"], "volume_percent_max": 30}},
        ]
        for patch in bad:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                self.check("capabilities", {**caps, **patch})

    def test_source_has_no_fabricated_clock_or_payload(self):
        signal = self.fixtures[0]["signal"]
        for patch in [
            {"clock_quality": "chronograph_attested"},
            {"evidence_class": "hardware_verified"},
            {"source_sequence": -1},
            {"non_actuating": False},
            {"audio_bytes": "private"},
        ]:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                self.check("signal", {**signal, **patch})


if __name__ == "__main__":
    unittest.main()
