"""CORE-D candidate tests: all temporal/History producers here are synthetic and non-authoritative."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from validate import ContractError, KINDS, SCHEMA, bounded, read_json, validate

ROOT = Path(__file__).resolve().parent
POS = read_json(ROOT / "fixtures/positive.json")["records"]
NEG = read_json(ROOT / "fixtures/negative.json")["cases"]

def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(data).hexdigest()

class LabError(ValueError):
    """Synthetic receiver reports fixed error codes."""

class FakeChronograf:
    """Only this trusted fake can issue recorded test anchors; NOT real Chronograf."""
    def __init__(self):
        self.now = 1000
        self.domain = "fixture:clock:knowledge"
        self.registry = {}
        self.sequence = 50
    def time(self, value):
        if type(value) is not int or value < self.now:
            raise LabError("CLOCK_REGRESSION")
        self.now = value
    def import_anchor(self, claim):
        validate(claim)
        self.sequence += 1
        rec = deepcopy(POS["import_anchor"])
        rec.update(record_id="fixture:import:"+str(self.sequence),
                   historical_assertion_ref=claim["record_id"],
                   anchor_handle_uint64_dec=str(self.sequence),
                   measured_clock_domain_ref=self.domain, measured_at_ms=self.now,
                   time_atom_sha256_hex=digest({"now":self.now, "seq":self.sequence})[7:])
        validate(rec)
        self.registry[rec["record_id"]] = digest(rec)
        return rec
    def verify(self, anchor, claim):
        validate(anchor)
        if (anchor["anchor_issuer_ref"] != "fixture:chronograf"
            or anchor["historical_assertion_ref"] != claim["record_id"]
            or anchor["measured_clock_domain_ref"] != self.domain
            or self.registry.get(anchor["record_id"]) != digest(anchor)):
            raise LabError("UNVERIFIED_ANCHOR")
    def commit_anchor(self):
        self.sequence += 1
        return "fixture:chronograf:commit:"+str(self.sequence)

def request_for(payload, key="fixture:idempotency:one", kind="MEMORY_ANNOTATION", anchor=None):
    r = deepcopy(POS["request"])
    r.update(idempotency_key=key, request_id=key, record_id="fixture:request:"+key.split(":")[-1],
             payload_ref=payload["record_id"], payload_sha256=digest(payload), payload_kind=kind)
    if kind == "LEGACY_IMPORT":
        r["historical_time_assertion_ref"] = payload["record_id"]
        r["import_anchor_evidence_ref"] = anchor["record_id"] if anchor else "fixture:anchor:missing"
    else:
        r["historical_time_assertion_ref"] = None
        r["import_anchor_evidence_ref"] = None
    return validate(r)

class FakeWriter:
    """External authority state is explicitly TEST-INJECTED; no signatures/real persistence."""
    def __init__(self):
        self.clock=FakeChronograf()
        self.owner="fixture:runtime:one"
        self.lease="fixture:lease:history"
        self.life="fixture:life:one"
        self.binding="fixture:binding:one"
        self.epoch=7
        self.policy="fixture:policy:one"
        self.context="sha256:"+"a"*64
        self.root=self.context
        self.gate=None
        self.connected=True
        self.history=[]
        self.dedup={}
        self.availability={}
    def grant(self,r):
        self.gate=(r["request_id"],r["effect_request_ref"],r["effect_gate_decision_ref"])
    def submit(self,r,p,anchor=None,lose_ack=False):
        validate(r);validate(p)
        if not self.connected:
            raise LabError("WRITER_UNAVAILABLE")
        if r["runtime_instance_id"]!=self.owner or r["writer_role_lease_ref"]!=self.lease:
            raise LabError("STALE_WRITER")
        if (r["life_id"],r["life_binding_ref"],r["life_activation_epoch"])!=(self.life,self.binding,self.epoch):
            raise LabError("LIFE_BINDING_INVALID")
        if (r["source_root"],r["context_revision"],r["policy_revision"])!=(self.root,self.context,self.policy):
            raise LabError("CONTEXT_REVOKED")
        if (r["request_id"],r["effect_request_ref"],r["effect_gate_decision_ref"])!=self.gate:
            raise LabError("HISTORY_GATE_NOT_CONNECTED")
        scope=(r["life_id"],r["idempotency_key"])
        fingerprint=digest(r)
        if scope in self.dedup:
            old_fp,receipt=self.dedup[scope]
            if old_fp!=fingerprint:raise LabError("IDEMPOTENCY_CONFLICT")
            if lose_ack:raise LabError("ACK_NOT_RECEIVED")
            return deepcopy(receipt)
        if r["payload_ref"]!=p["record_id"] or r["payload_sha256"]!=digest(p):
            raise LabError("PAYLOAD_MISMATCH")
        kinds={"MEMORY_ANNOTATION":"MemoryAnnotation","LEGACY_IMPORT":"HistoricalTimeAssertion",
               "ONEIRIC_REVIEW":"OneiricReview","COGNITIVE_COMMITMENT":"CognitiveCommitment",
               "EVIDENCE_AVAILABILITY":"EvidenceAvailability"}
        if kinds[r["payload_kind"]]!=p["record_type"]:raise LabError("WRONG_PAYLOAD_TYPE")
        if r["payload_kind"]=="LEGACY_IMPORT":
            if not anchor or r["import_anchor_evidence_ref"]!=anchor["record_id"] or r["historical_time_assertion_ref"]!=p["record_id"]:
                raise LabError("IMPORT_EVIDENCE_MISSING")
            self.clock.verify(anchor,p)
        if p["record_type"]=="MemoryAnnotation":
            if p["knowledge_clock_domain_ref"]!=self.clock.domain or p["knowledge_at_ms"]>self.clock.now:
                raise LabError("UNQUALIFIED_KNOWLEDGE_TIME")
            prior=p["supersedes_annotation_ref"]
            if prior is not None:
                matches=[h for h in self.history if h["payload"]["record_type"]=="MemoryAnnotation" and h["payload"]["record_id"]==prior]
                if len(matches)!=1 or matches[0]["payload"]["subject_ref"]!=p["subject_ref"]:
                    raise LabError("INVALID_SUPERSESSION")
        n=len(self.history)+1
        receipt=deepcopy(POS["receipt"])
        receipt.update(record_id="fixture:receipt:"+str(n),request_id=r["request_id"],
                       idempotency_key=r["idempotency_key"],request_sha256=fingerprint,
                       committed_chronon_ref="fixture:chronon:"+str(n),
                       history_watermark_ref="fixture:watermark:"+str(n),
                       recorded_anchor_ref=self.clock.commit_anchor(),
                       writer_receipt_ref="fixture:writer:proof:"+str(n))
        validate(receipt)
        self.history.append({"payload":deepcopy(p),"receipt":deepcopy(receipt),
                             "known_at_commit_ms":self.clock.now})
        self.dedup[scope]=(fingerprint,deepcopy(receipt))
        if p["record_type"]=="EvidenceAvailability":self.availability[p["evidence_ref"]]=deepcopy(p)
        if lose_ack:raise LabError("ACK_NOT_RECEIVED")
        return deepcopy(receipt)
    def lookup(self,r):
        if not self.connected:raise LabError("WRITER_UNAVAILABLE")
        if r["runtime_instance_id"]!=self.owner:raise LabError("STALE_WRITER")
        entry=self.dedup.get((r["life_id"],r["idempotency_key"]))
        if entry is None:return None
        if entry[0]!=digest(r):raise LabError("IDEMPOTENCY_CONFLICT")
        return deepcopy(entry[1])
    def as_known_at(self,subject,time,domain="fixture:clock:knowledge"):
        if domain!=self.clock.domain:raise LabError("CLOCK_UNALIGNED")
        relevant=[h for h in self.history if h["payload"]["record_type"]=="MemoryAnnotation"
                  and h["payload"]["subject_ref"]==subject and h["known_at_commit_ms"]<=time]
        if not relevant:return None
        h=relevant[-1];p=h["payload"]
        return {"assessment":p["assessment"],"annotation_ref":p["record_id"],
                "event_time_claim_ref":p["about_valid_time_assertion_ref"],
                "known_at_commit_ms":h["known_at_commit_ms"],
                "unavailable_evidence_refs":[x for x in p["evidence_refs"]
                        if x in self.availability and self.availability[x]["reported_state"]!="AVAILABLE"],
                "raw_private_evidence_exposed":False}

class ShapeTests(unittest.TestCase):
    def test_status_not_normative(self):
        status=read_json(ROOT/"STATUS.json")
        self.assertEqual(status["maturity"],"candidate")
        for key in ("accepted","normative","runtime_implemented","stable_release_allowed"):
            self.assertIs(status[key],False)
    def test_ten_types(self):self.assertEqual(len(KINDS),10)
    def test_cannot_hide_unsafe_field(self):
        r=deepcopy(POS["commitment"]);r["private_chain_of_thought"]="NEVER_INCLUDE"
        with self.assertRaisesRegex(ContractError,"SCHEMA_VIOLATION"):validate(r)
    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"private.json";file.write_text('{"x":1,"x":2}')
            with self.assertRaisesRegex(ContractError,"DUPLICATE_KEY"):read_json(file)
    def test_rejects_nan(self):
        with self.assertRaisesRegex(ContractError,"NONFINITE"):bounded({"x":float("nan")})
    def test_rejects_cyclic_containers(self):
        arr=[];arr.append(arr)
        with self.assertRaisesRegex(ContractError,"SHARED_OR_CYCLIC_CONTAINER"):bounded(arr)
    def test_rejects_bad_discriminators(self):
        for value in (None, [], {}, True, 9):
            with self.subTest(str(value)),self.assertRaisesRegex(ContractError,"UNKNOWN_RECORD"):
                validate({"record_type":value})
    def test_offline_no_network_or_subprocess(self):
        with (patch.object(socket,"socket",side_effect=AssertionError("network")),
              patch.object(subprocess,"Popen",side_effect=AssertionError("process"))):
            for record in POS.values():validate(record)
            w=FakeWriter();w.clock.time(2000);p=POS["annotation_initial"];r=request_for(p);w.grant(r);w.submit(r,p)

class FlowTests(unittest.TestCase):
    def setUp(self):self.w=FakeWriter()
    def valid(self,p,key="fixture:idempotency:one",kind="MEMORY_ANNOTATION",anchor=None):
        r=request_for(p,key,kind,anchor);self.w.grant(r);return r
    def test_old_time_not_new_anchor(self):
        claim=POS["historical_time_assertion"];anchor=self.w.clock.import_anchor(claim)
        self.assertEqual(claim["source_clock_domain_ref"],"legacy.posix.system")
        self.assertFalse(claim["measured_by_chronograf"])
        self.assertEqual(anchor["measured_at_ms"],1000)
        self.assertNotEqual(claim["claimed_time_token"],str(anchor["measured_at_ms"]))
        self.assertNotEqual(claim["source_clock_domain_ref"],anchor["measured_clock_domain_ref"])
    def test_legacy_import_has_new_receipt_anchor(self):
        p=POS["historical_time_assertion"];anchor=self.w.clock.import_anchor(p)
        r=self.valid(p,kind="LEGACY_IMPORT",anchor=anchor);receipt=self.w.submit(r,p,anchor)
        self.assertEqual(receipt["receipt_status"],"COMMITTED")
        self.assertNotEqual(receipt["recorded_anchor_ref"],anchor["record_id"])
        self.assertEqual(len(self.w.history),1)
    def test_unverified_retro_anchor_refused(self):
        p=POS["historical_time_assertion"];anchor=self.w.clock.import_anchor(p)
        r=self.valid(p,kind="LEGACY_IMPORT",anchor=anchor);anchor["measured_at_ms"]=3
        with self.assertRaisesRegex(LabError,"UNVERIFIED_ANCHOR"):self.w.submit(r,p,anchor)
        self.assertEqual(len(self.w.history),0)
    def test_no_write_when_disconnected(self):
        p=POS["annotation_initial"];r=self.valid(p);self.w.connected=False
        with self.assertRaisesRegex(LabError,"WRITER_UNAVAILABLE"):self.w.submit(r,p)
        self.assertEqual(self.w.history,[])
    def test_missing_gate(self):
        p=POS["annotation_initial"];r=request_for(p)
        with self.assertRaisesRegex(LabError,"HISTORY_GATE_NOT_CONNECTED"):self.w.submit(r,p)
    def test_ack_loss_query_no_double_write(self):
        p=POS["annotation_initial"];r=self.valid(p);self.w.clock.time(2000)
        with self.assertRaisesRegex(LabError,"ACK_NOT_RECEIVED"):self.w.submit(r,p,lose_ack=True)
        receipt=self.w.lookup(r)
        self.assertEqual(receipt["receipt_status"],"COMMITTED")
        self.assertEqual(self.w.submit(r,p),receipt)
        self.assertEqual(len(self.w.history),1)
    def test_collision_changed_payload_or_context(self):
        p=POS["annotation_initial"];r=self.valid(p);self.w.clock.time(2000);self.w.submit(r,p)
        alt=deepcopy(r);alt["payload_sha256"]="sha256:"+"f"*64
        with self.assertRaisesRegex(LabError,"IDEMPOTENCY_CONFLICT"):self.w.submit(alt,p)
        self.assertEqual(len(self.w.history),1)
    def test_old_runtime_rejected(self):
        p=POS["annotation_initial"];r=self.valid(p);r["runtime_instance_id"]="fixture:old"
        with self.assertRaisesRegex(LabError,"STALE_WRITER"):self.w.submit(r,p)
    def test_no_life_enrollment_from_json(self):
        p=POS["annotation_initial"];r=self.valid(p);r["life_id"]="fixture:fake"
        with self.assertRaisesRegex(LabError,"LIFE_BINDING_INVALID"):self.w.submit(r,p)
    def test_no_restore_of_revoked_grant(self):
        p=POS["annotation_initial"];r=self.valid(p);self.w.gate=None
        with self.assertRaisesRegex(LabError,"HISTORY_GATE_NOT_CONNECTED"):self.w.submit(r,p)
    def test_as_known_and_current_assessment(self):
        a=POS["annotation_initial"];b=POS["annotation_revision"]
        self.w.clock.time(2000);self.w.submit(self.valid(a),a)
        self.w.clock.time(3000);self.w.submit(self.valid(b,"fixture:idempotency:two"),b)
        past=self.w.as_known_at("fixture:hypothesis:firststep",2500)
        now=self.w.as_known_at("fixture:hypothesis:firststep",3000)
        self.assertEqual(past["assessment"],"UNRESOLVED")
        self.assertEqual(now["assessment"],"REFUTED")
        self.assertEqual(past["event_time_claim_ref"],now["event_time_claim_ref"])
        self.assertEqual(self.w.history[0]["payload"],a)
    def test_knowledge_cannot_be_backdated_by_payload(self):
        p=deepcopy(POS["annotation_initial"]);p["knowledge_at_ms"]=100
        self.w.clock.time(2000);self.w.submit(self.valid(p),p)
        self.assertIsNone(self.w.as_known_at(p["subject_ref"],1000))
    def test_cross_clock_query_denied(self):
        with self.assertRaisesRegex(LabError,"CLOCK_UNALIGNED"):
            self.w.as_known_at("fixture:hypothesis:firststep",0,"legacy.posix.system")
    def test_missing_prior_annotation_denied(self):
        p=POS["annotation_revision"];self.w.clock.time(3000)
        with self.assertRaisesRegex(LabError,"INVALID_SUPERSESSION"):
            self.w.submit(self.valid(p),p)
    def test_oneiric_completion_does_not_prove_step(self):
        p=POS["oneiric"];self.assertEqual(p["review_outcome"],"REVIEW_COMPLETED")
        self.assertEqual(p["assessment"],"REFUTED")
        self.assertFalse(p["physical_milestone_verified"])
        self.assertFalse(p["history_committed"])
    def test_cognitive_review_commit_is_computation_not_physical(self):
        p=POS["oneiric"];r=self.valid(p,kind="ONEIRIC_REVIEW");self.w.clock.time(3000)
        self.w.submit(r,p)
        self.assertFalse(self.w.history[-1]["payload"]["physical_milestone_verified"])
    def test_history_commit_not_one_per_raw_sample(self):
        for i in range(100):self.w.clock.time(self.w.clock.now+1)
        self.assertEqual(len(self.w.history),0)
    def test_checkpoint_is_only_hint(self):
        p=POS["checkpoint"];self.assertFalse(p["restores_grants"])
        self.assertIsNone(p["history_watermark_ref"])
    def test_privacy_redaction_updates_projection_availability(self):
        p=POS["annotation_initial"];self.w.clock.time(2000)
        self.w.submit(self.valid(p),p)
        red=deepcopy(POS["evidence"])
        red.update(reported_state="REDACTED",retention_policy_ref="fixture:retention:policy",
                   reason_code="POLICY_ERASURE",proof_ref="fixture:erasure:reported")
        self.w.clock.time(2200);self.w.submit(self.valid(red,"fixture:idempotency:erase","EVIDENCE_AVAILABILITY"),red)
        view=self.w.as_known_at(p["subject_ref"],3000)
        self.assertEqual(view["unavailable_evidence_refs"],["fixture:evidence:original"])
        self.assertFalse(view["raw_private_evidence_exposed"])
        self.assertEqual(red["verification_state"],"REPORTED_NOT_ATTESTED")

# Distinct positive fixture records and negative contract cases.
for name,record in POS.items():
    def make_positive(v):
        def test(self):validate(deepcopy(v))
        return test
    setattr(ShapeTests,"test_positive_"+name,make_positive(record))
for case in NEG:
    def make_negative(v):
        def test(self):
            with self.assertRaises(ContractError):validate(deepcopy(v))
        return test
    setattr(ShapeTests,"test_negative_"+case["case"],make_negative(case["record"]))

if __name__=="__main__":
    unittest.main(verbosity=2)
