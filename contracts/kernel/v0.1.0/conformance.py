"""Synthetic reference consumers ONLY. Not a production admission/policy service.

The oracle below is deliberately test-owned, not derived from untrusted records.
Authentication, signature checks, distributed leases and actual effect dispatch
are NOT implemented. The tested consumers never perform a requested effect.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("core_b_shape_validator", ROOT / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
POS = v.read_json(ROOT / "fixtures/positive.json")["records"]
NEG = v.read_json(ROOT / "fixtures/negative.json")["cases"]


def record(name):
    return deepcopy(POS[name]["record"])


def require(condition, code):
    if not condition:
        raise v.ContractError(code)


class FixtureConsumer:
    """Finite, session-only test oracle; NOT exported from the installed Core."""

    def __init__(self):
        self.context = record("goal")["context"]
        self.now_ms = 150
        self.clock = "fixture:monotonic:1"
        self.effects = {"INTERNAL_READ_ONLY"}
        self.grants = {"fixture:grant:read"}
        self.limits = record("goal")["budget"]
        self.admitter = "fixture:admitter:1"
        self.work_owner = "fixture:work:1"
        self.gates = {"INTERNAL_READ_ONLY": "fixture:gate:read"}
        self.producers = {"fixture:kernel:Work"}
        self.receipts = {"fixture:receipt:read": record("request")}
        self.seen = {}
        self.last_transition = None

    def current(self, item):
        require(item["context"] == self.context, "CONTEXT_OR_FENCE_MISMATCH")
        require(self.context["scope"] == "SESSION_SCOPED", "LIFE_VERIFIER_NOT_CONNECTED")
        life = item["lifetime"]
        require(life["quality"] == "MONOTONIC_SESSION" and life["clock_domain"] == self.clock,
                "CLOCK_UNALIGNED")
        require(life["created_ms"] <= self.now_ms < life["created_ms"] + life["ttl_ms"],
                "EXPIRED_OR_FUTURE")

    def goal(self, goal, parent=None, siblings=0):
        v.validate("CognitiveGoalCandidate", goal)
        self.current(goal)
        require(set(goal["requested_effects"]) <= self.effects, "EFFECT_NOT_PERMITTED")
        require(all(goal["budget"][k] <= self.limits[k] for k in self.limits), "BUDGET_EXCEEDED")
        require(goal["depth"] <= goal["budget"]["depth"], "DEPTH_EXCEEDED")
        if goal["parent_goal_id"] is not None:
            require(parent is not None, "PARENT_UNRESOLVED")
            require(goal["parent_goal_id"] == parent["goal_id"] and
                    goal["depth"] == parent["depth"] + 1, "PARENT_DEPTH_MISMATCH")
            require(siblings < parent["budget"]["subgoals"], "SUBGOAL_LIMIT")
            require(goal["budget"]["depth"] <= parent["budget"]["depth"], "PARENT_DEPTH_ESCALATION")
        return "GOAL_CHECKED_NOT_ADMITTED"

    def admission(self, goal, decision):
        self.goal(goal)
        v.validate("GoalAdmissionDecision", decision)
        self.current(decision)
        require(decision["admission_authority_ref"] == self.admitter, "UNTRUSTED_ADMITTER")
        require((decision["goal_id"], decision["goal_revision"]) ==
                (goal["goal_id"], goal["goal_revision"]), "GOAL_BINDING_MISMATCH")
        require(decision["outcome"] == "ADMIT", "NOT_ADMITTED")
        require(set(decision["eligible_effects"]) <= set(goal["requested_effects"]), "EFFECT_ESCALATION")
        require(set(decision["evaluated_grant_refs"]) <= self.grants, "UNVERIFIED_GRANT")
        require(all(decision["allocated_budget"][k] <= goal["budget"][k]
                    for k in self.limits), "BUDGET_ESCALATION")
        return "ADMISSION_CHECKED_NOT_EFFECT_AUTHORIZED"

    def effect(self, goal, admission, request, decision):
        self.admission(goal, admission)
        v.validate("EffectRequest", request)
        v.validate("EffectGateDecision", decision)
        self.current(request)
        self.current(decision)
        require((request["goal_id"], request["goal_revision"], request["admission_ref"]) ==
                (goal["goal_id"], goal["goal_revision"], admission["decision_id"]), "REQUEST_BINDING_MISMATCH")
        require(request["category"] in admission["eligible_effects"], "EFFECT_NOT_ADMITTED")
        require(set(request["requested_grant_refs"]) <= self.grants, "UNVERIFIED_GRANT")
        require((decision["request_id"], decision["category"]) ==
                (request["request_id"], request["category"]), "GATE_BINDING_MISMATCH")
        require(decision["outcome"] == "ALLOW", "GATE_NOT_ALLOW")
        require(decision["gate_owner_ref"] == self.gates.get(request["category"]), "WRONG_GATE")
        require(set(decision["evaluated_grant_refs"]) <= self.grants, "REVOKED_OR_UNKNOWN_GRANT")
        require(self.receipts.get(decision["verification_receipt_ref"]) == request,
                "RECEIPT_NOT_VERIFIED_FOR_EXACT_REQUEST")
        return "FIXTURE_CONFORMANT_NO_EFFECT_EXECUTED"

    def event(self, item, payload):
        v.validate("KernelEvent", item)
        self.current(item)
        require(item["producer_kernel_id"] in self.producers, "UNAUTHENTICATED_PRODUCER")
        require(item["kind"] == "openrgd.kernel.v0_1.goal_candidate", "PAYLOAD_KIND_MISMATCH")
        v.validate("CognitiveGoalCandidate", payload)
        require((item["payload_ref"], item["payload_digest"], item["context"]) ==
                (payload["goal_id"], payload["goal_revision"], payload["context"]), "PAYLOAD_BINDING_MISMATCH")
        key = (item["producer_kernel_id"], item["context"]["session_id"], item["idempotency_key"])
        if key in self.seen:
            require(self.seen[key] == item, "DUPLICATE_KEY_CONFLICT")
            return "DUPLICATE_NO_REEXECUTION"
        require(len(self.seen) < self.limits["queue_items"], "QUEUE_FULL_DEFER")
        self.seen[key] = deepcopy(item)
        return "EVENT_RECEIVED_NO_AUTHORITY"

    def transition(self, goal, admission, item):
        self.admission(goal, admission)
        v.validate("AgendaTransition", item)
        self.current(item)
        require(item["work_owner_ref"] == self.work_owner, "WRONG_WORK_OWNER")
        require((item["goal_id"], item["goal_revision"], item["admission_ref"]) ==
                (goal["goal_id"], goal["goal_revision"], admission["decision_id"]), "TRANSITION_BINDING_MISMATCH")
        allowed = {"PROPOSED": {"ADMITTED"}, "ADMITTED": {"RUNNING", "CANCELLED"},
                   "RUNNING": {"PAUSED", "COMPLETED", "FAILED", "CANCELLED"},
                   "PAUSED": {"RUNNING", "CANCELLED", "FAILED"}}
        require(item["to_state"] in allowed.get(item["from_state"], set()), "ILLEGAL_TRANSITION")
        old = self.last_transition
        if old is None:
            require(item["sequence"] == 0 and item["previous_transition_ref"] is None and
                    item["from_state"] == "PROPOSED", "TRANSITION_START_INVALID")
        else:
            if item["idempotency_key"] == old["idempotency_key"]:
                require(item == old, "TRANSITION_REPLAY_CONFLICT")
                return "DUPLICATE_NO_REEXECUTION"
            require(item["sequence"] == old["sequence"] + 1 and
                    item["previous_transition_ref"] == old["transition_id"] and
                    item["from_state"] == old["to_state"], "TRANSITION_CHAIN_INVALID")
        self.last_transition = deepcopy(item)
        return "TRANSITION_CHECKED_NO_EFFECT"


class ShapeTests(unittest.TestCase):
    def test_status_candidate(self):
        status = v.read_json(ROOT / "STATUS.json")
        self.assertEqual(status["maturity"], "candidate")
        for field in ("normative", "accepted", "stable_release_allowed", "runtime_implemented"):
            self.assertIs(status[field], False)

    def test_all_schema_selectors(self):
        self.assertEqual(set(v.validators()), set(v.TYPES))

    def test_finite(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(v.ContractError):
                v.validate("CognitiveGoalCandidate", v.mutated(record("goal"), {"depth": value}))

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text('{"x": 1, "x": 2}')
            with self.assertRaisesRegex(v.ContractError, "DUPLICATE_KEY"):
                v.read_json(path)

    def test_structure_bound(self):
        x = {}
        for _ in range(30):
            x = {"x": x}
        with self.assertRaisesRegex(v.ContractError, "STRUCTURE_LIMIT"):
            v.validate("KernelEvent", x)

    def test_record_size_bound(self):
        with self.assertRaisesRegex(v.ContractError, "RECORD_TOO_LARGE"):
            v.validate("KernelEvent", {"x": "x" * 65537})

    def test_offline_no_process_or_network(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("process")):
            self.assertEqual(v.check_fixtures(), (11, 24))

    def test_unknown_type(self):
        with self.assertRaisesRegex(v.ContractError, "UNKNOWN_CONTRACT"):
            v.validate("AgentIdentity", {})

    def test_roundtrip_and_no_mutation(self):
        for item in POS.values():
            copy = deepcopy(item)
            v.validate(item["type"], json.loads(json.dumps(item["record"])))
            self.assertEqual(item, copy)

    def test_optimized_python(self):
        result = subprocess.run([sys.executable, "-O", str(ROOT / "validate.py")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["authorization_verified"])


for name, item in POS.items():
    def positive(self, item=item):
        v.validate(item["type"], item["record"])
    setattr(ShapeTests, "test_positive_" + name, positive)
for case in NEG:
    def negative(self, case=case):
        src = POS[case["base"]]
        with self.assertRaises(v.ContractError):
            v.validate(src["type"], v.mutated(src["record"], case["set"]))
    setattr(ShapeTests, "test_negative_" + case["id"], negative)


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.consumer = FixtureConsumer()
        self.flow = [record(k) for k in ("goal", "admission", "request", "gate")]

    def test_valid_flow_no_effect(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("process")):
            self.assertEqual(self.consumer.effect(*self.flow), "FIXTURE_CONFORMANT_NO_EFFECT_EXECUTED")

    def test_deterministic_replay(self):
        self.assertEqual(FixtureConsumer().effect(*self.flow), FixtureConsumer().effect(*self.flow))

    def test_revoked_grant(self):
        self.consumer.grants.clear()
        with self.assertRaises(v.ContractError):
            self.consumer.effect(*self.flow)

    def test_admission_not_effect_authority(self):
        self.assertEqual(self.consumer.admission(*self.flow[:2]), "ADMISSION_CHECKED_NOT_EFFECT_AUTHORIZED")
        self.consumer.receipts.clear()
        with self.assertRaises(v.ContractError):
            self.consumer.effect(*self.flow)

    def test_all_external_effects_need_separate_policy(self):
        for effect in ("HISTORY_COMMIT_REQUEST", "COMMUNICATION_REQUEST", "DIGITAL_EFFECT_REQUEST", "PHYSICAL_ACTION_REQUEST"):
            flow = deepcopy(self.flow)
            flow[0]["requested_effects"] = [effect]
            with self.assertRaisesRegex(v.ContractError, "EFFECT_NOT_PERMITTED"):
                self.consumer.effect(*flow)

    def test_changed_receipt_target(self):
        self.flow[2]["target_ref"] = "fixture:other-target"
        with self.assertRaisesRegex(v.ContractError, "RECEIPT_NOT_VERIFIED"):
            self.consumer.effect(*self.flow)

    def test_ttl_boundary(self):
        self.consumer.now_ms = 1100
        with self.assertRaisesRegex(v.ContractError, "EXPIRED_OR_FUTURE"):
            self.consumer.effect(*self.flow)

    def test_unresolved_parent(self):
        goal = v.mutated(self.flow[0], {"parent_goal_id": "fixture:parent", "depth": 1})
        with self.assertRaisesRegex(v.ContractError, "PARENT_UNRESOLVED"):
            self.consumer.goal(goal)

    def test_subgoal_requires_new_admission(self):
        parent = self.flow[0]
        child = v.mutated(parent, {"goal_id": "fixture:child", "parent_goal_id": parent["goal_id"], "depth": 1})
        self.assertEqual(self.consumer.goal(child, parent), "GOAL_CHECKED_NOT_ADMITTED")
        with self.assertRaises(v.ContractError):
            self.consumer.admission(child, self.flow[1])

    def test_subgoal_limit(self):
        parent = self.flow[0]
        child = v.mutated(parent, {"goal_id": "fixture:child", "parent_goal_id": parent["goal_id"], "depth": 1})
        with self.assertRaisesRegex(v.ContractError, "SUBGOAL_LIMIT"):
            self.consumer.goal(child, parent, siblings=2)

    def test_duplicate_event(self):
        item = record("event")
        self.consumer.event(item, self.flow[0])
        self.assertEqual(self.consumer.event(item, self.flow[0]), "DUPLICATE_NO_REEXECUTION")
        item["event_id"] = "fixture:changed-event"
        with self.assertRaisesRegex(v.ContractError, "DUPLICATE_KEY_CONFLICT"):
            self.consumer.event(item, self.flow[0])

    def test_queue_bounded(self):
        for i in range(8):
            item = v.mutated(record("event"), {"event_id": f"fixture:event:{i}", "idempotency_key": f"fixture:event:{i}"})
            self.consumer.event(item, self.flow[0])
        with self.assertRaisesRegex(v.ContractError, "QUEUE_FULL_DEFER"):
            item = v.mutated(record("event"), {"idempotency_key": "fixture:overflow"})
            self.consumer.event(item, self.flow[0])

    def test_untrusted_producer(self):
        with self.assertRaisesRegex(v.ContractError, "UNAUTHENTICATED_PRODUCER"):
            self.consumer.event(v.mutated(record("event"), {"producer_kernel_id": "fixture:impostor"}), self.flow[0])

    def test_transition_chain_and_terminal(self):
        item = record("transition")
        self.consumer.transition(*self.flow[:2], item)
        self.assertEqual(self.consumer.transition(*self.flow[:2], item), "DUPLICATE_NO_REEXECUTION")
        for index, (start, end) in enumerate((("ADMITTED", "RUNNING"), ("RUNNING", "PAUSED"), ("PAUSED", "RUNNING"), ("RUNNING", "COMPLETED")), 1):
            item = v.mutated(item, {"transition_id": f"fixture:t:{index}", "idempotency_key": f"fixture:t:{index}", "sequence": index, "previous_transition_ref": item["transition_id"], "from_state": start, "to_state": end})
            self.consumer.transition(*self.flow[:2], item)
        with self.assertRaisesRegex(v.ContractError, "ILLEGAL_TRANSITION"):
            self.consumer.transition(*self.flow[:2], v.mutated(item, {"from_state": "COMPLETED", "to_state": "RUNNING"}))

    def test_wrong_work_owner(self):
        with self.assertRaisesRegex(v.ContractError, "WRONG_WORK_OWNER"):
            self.consumer.transition(*self.flow[:2], v.mutated(record("transition"), {"work_owner_ref": "fixture:second-primary"}))

    def test_skipped_transition(self):
        with self.assertRaisesRegex(v.ContractError, "TRANSITION_START_INVALID"):
            self.consumer.transition(*self.flow[:2], v.mutated(record("transition"), {"sequence": 2}))


# Cross-record semantic faults: these records remain individually shape-valid.
SEMANTIC_CASES = [
    ("stale_context", 0, "context.revision", "sha256:" + "3" * 64),
    ("stale_rtx_generation", 0, "context.role_fencing_generation", 6),
    ("reboot_session", 0, "context.session_id", "fixture:old-session"),
    ("old_runtime", 0, "context.runtime_instance_id", "fixture:old-runtime"),
    ("policy_changed", 0, "context.policy_revision", "fixture:old-policy"),
    ("unknown_clock", 0, "lifetime.quality", "UNALIGNED"),
    ("foreign_clock", 0, "lifetime.clock_domain", "fixture:other-clock"),
    ("future_event", 0, "lifetime.created_ms", 1000),
    ("expired_event", 0, "lifetime.ttl_ms", 20),
    ("model_self_admits", 1, "admission_authority_ref", "fixture:model"),
    ("second_coordinator", 1, "admission_authority_ref", "fixture:other-primary"),
    ("foreign_goal", 1, "goal_id", "fixture:other-goal"),
    ("changed_goal", 1, "goal_revision", "sha256:" + "4" * 64),
    ("budget_escalation", 1, "allocated_budget.steps", 100),
    ("effect_escalation", 1, "eligible_effects", ["DIGITAL_EFFECT_REQUEST"]),
    ("unknown_grant", 1, "evaluated_grant_refs", ["fixture:self-grant"]),
    ("request_foreign_admission", 2, "admission_ref", "fixture:other-admission"),
    ("request_stale_fence", 2, "context.role_fencing_generation", 6),
    ("request_unadmitted_effect", 2, "category", "HISTORY_COMMIT_REQUEST"),
    ("request_unknown_grant", 2, "requested_grant_refs", ["fixture:self-grant"]),
    ("gate_wrong_owner", 3, "gate_owner_ref", "fixture:model"),
    ("gate_wrong_category", 3, "category", "PHYSICAL_ACTION_REQUEST"),
    ("gate_wrong_request", 3, "request_id", "fixture:other-request"),
    ("gate_fake_receipt", 3, "verification_receipt_ref", "fixture:invented"),
    ("gate_expired", 3, "lifetime.ttl_ms", 20),
]
for name, index, path, value in SEMANTIC_CASES:
    def fault(self, index=index, path=path, value=value):
        self.flow[index] = v.mutated(self.flow[index], {path: value})
        kind = ("CognitiveGoalCandidate", "GoalAdmissionDecision", "EffectRequest", "EffectGateDecision")[index]
        v.validate(kind, self.flow[index])
        with self.assertRaises(v.ContractError):
            self.consumer.effect(*self.flow)
    setattr(ConsumerTests, "test_reject_" + name, fault)


if __name__ == "__main__":
    unittest.main(verbosity=2)
