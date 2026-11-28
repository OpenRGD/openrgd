"""Contract tests. Real source/wheel fixture, test-only local TUF context.

Registry companion tests exercise actual TUF signatures and SQLite writer.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from proposal import parse, digest, encode_proposal
from ledger_contract import make_receipt
from provenance_fixture import build_source_fixture,verification_inputs
from provenance import verify_provenance
from wheel_inspection import inspect_wheel, review_target
from admission import project_admission
from catalog_contract import (AdmissionError,checked,validate_catalog,check_successor,
                               select_preview,verify_preview_artifact,ROOT)

CAT="org.example.catalog"
LID="00000000-0000-4000-8000-000000000001"
RID="00000000-0000-4000-8000-000000000002"
D="sha256:"+"a"*64

def checkpoint(seq,sha):
    return {"schema_version":"openrgd.release-ledger-checkpoint.v0.1-candidate",
            "catalog_id":CAT,"ledger_id":LID,"legacy_catalog_sha256":D,
            "event_sequence":seq,"event_sha256":sha,"grants_authority":False}

def catalog(a=None,state="RESERVED_CANDIDATE",revision=1,event=1,receipt=None):
    r={"schema_version":"openrgd.catalog-preview.v0.1-candidate",
       "catalog_id":CAT,"ledger_id":LID,"checkpoint":checkpoint(0,None),"entries":[],
       "publication_committed":False,"installable":False,"grants_authority":False}
    if a is not None:
        sha=a["reservation_receipt_sha256"] if receipt is None else receipt
        r["entries"]=[{"admission":a,"state":state,"release_revision":revision,
                      "state_event_sequence":event,"state_receipt_sha256":sha}]
        r["checkpoint"]=checkpoint(event,sha)
    return r

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        f=build_source_fixture(cls.temp.name);args=verification_inputs(f)
        cls.inputs=f["inputs"];cls.p=args["submitted_proposal_raw"];prov=verify_provenance(**args)
        inspection=inspect_wheel(**cls.inputs,submitted_proposal_raw=cls.p)
        cls.review=encode_proposal(review_target(inspection,"org.example"))
        cls.request={"schema_version":"openrgd.release-ledger-request.v0.1-candidate",
            "catalog_id":CAT,"ledger_id":LID,"request_id":RID,
            "module_id":prov["module_id"],"module_version":prov["module_version"],
            "operation":"RESERVE_CANDIDATE","expected_revision":0,"proposal_sha256":digest(cls.p),
            "reason_code":"CANDIDATE_REVIEW","evidence_sha256":digest(cls.review),"grants_authority":False}
        rq=encode_proposal(cls.request)
        # Shape/commitment fixture ONLY. This is not an actual TUF verification.
        cls.ctx={"profile":"TUF_AND_BUILD_PROVENANCE_REVIEW_CANDIDATE",
            "request_sha256":digest(rq),"review_target_sha256":digest(cls.review),
            "tuf_review_context":{"profile":"TUF_OFFLINE_REVIEW_CANDIDATE",
                "request_sha256":digest(rq),"review_target_sha256":digest(cls.review)},
            "provenance_review":prov,"provenance_review_sha256":digest(encode_proposal(prov)),
            "builder_policy_sha256":prov["policy_sha256"],"attestation_sha256":prov["attestation_sha256"],
            "builder_key_separation_verified":True,"publication_committed":False,
            "installable":False,"grants_authority":False}
        cls.raw=encode_proposal(cls.ctx)
        cls.receipt=encode_proposal(make_receipt(cls.request,rq,cls.raw,1,None,None))
    def project(self,**kw):
        args={"manifest_raw":self.inputs["manifest_raw"],"proposal_raw":self.p,
              "review_raw":self.review,"receipt_raw":self.receipt,"authority_raw":self.raw}
        args.update(kw);return project_admission(**args)
    def view(self,**kw):
        return validate_catalog(encode_proposal(catalog(self.project(),**kw)),CAT,LID)
    def test_candidate_only(self):
        s=json.loads((ROOT/"STATUS.json").read_bytes())
        for k in ("normative","accepted","stable_release_allowed","runtime_implemented","publication_implemented"):
            self.assertIs(s[k],False)
    def test_projection_binds_existing_evidence_and_artifact(self):
        a=self.project();m=parse(self.inputs["manifest_raw"])
        self.assertEqual(a["proposal_sha256"],digest(self.p))
        self.assertEqual(a["manifest_sha256"],digest(self.inputs["manifest_raw"]))
        self.assertEqual(a["reservation_receipt_sha256"],digest(self.receipt))
        self.assertEqual(a["authority_context_sha256"],digest(self.raw))
        self.assertEqual(a["dependencies"],m["dependencies"])
        self.assertEqual(a["functional_roles"],m["functional_roles"])
        for k in ("publication_committed","installable","grants_authority","host_compatibility_verified","dependency_resolution_verified"):
            self.assertIs(a[k],False)
        self.assertEqual(verify_preview_artifact(a,self.inputs["artifact_bytes"]["wheel"])["bytes_match"],True)
    def test_exact_input_commitments(self):
        for name,raw in (("manifest_raw",self.inputs["manifest_raw"]),("proposal_raw",self.p),
                         ("review_raw",self.review),("authority_raw",self.raw)):
            with self.subTest(name=name),self.assertRaises(AdmissionError):self.project(**{name:raw+b" "})
    def test_context_missing_provenance_even_if_receipt_binds(self):
        ctx=encode_proposal({"profile":"TUF_OFFLINE_REVIEW_CANDIDATE"})
        rec=encode_proposal(make_receipt(self.request,encode_proposal(self.request),ctx,1,None,None))
        with self.assertRaisesRegex(AdmissionError,"PROVENANCE_CONTEXT_REQUIRED"):self.project(authority_raw=ctx,receipt_raw=rec)
    def test_provenance_report_wrong_proposal_even_if_receipt_binds(self):
        ctx=deepcopy(self.ctx);ctx["provenance_review"]["proposal_sha256"]=D
        ctx["provenance_review_sha256"]=digest(encode_proposal(ctx["provenance_review"]))
        raw=encode_proposal(ctx);rec=encode_proposal(make_receipt(self.request,encode_proposal(self.request),raw,1,None,None))
        with self.assertRaisesRegex(AdmissionError,"PROVENANCE_BINDING_MISMATCH"):
            self.project(authority_raw=raw,receipt_raw=rec)
    def test_exact_selection_no_floating_or_install(self):
        c=self.view();a=self.project()
        self.assertEqual(select_preview(c,a["module_id"],a["module_version"]),a)
        with self.assertRaisesRegex(AdmissionError,"RELEASE_NOT_FOUND"):select_preview(c,a["module_id"],"latest")
        with self.assertRaisesRegex(AdmissionError,"ARTIFACT_BYTES_MISMATCH"):
            verify_preview_artifact(a,self.inputs["artifact_bytes"]["wheel"]+b"x")
    def test_empty_catalog_and_scope(self):
        c=validate_catalog(encode_proposal(catalog()),CAT,LID)
        self.assertEqual(c["entries"],[])
        with self.assertRaisesRegex(AdmissionError,"CATALOG_SCOPE_MISMATCH"):
            validate_catalog(encode_proposal(c),"org.other.catalog",LID)
    def test_duplicate_release_key_or_invalid_head(self):
        c=catalog(self.project());c["entries"].append(deepcopy(c["entries"][0]))
        with self.assertRaises(AdmissionError):validate_catalog(encode_proposal(c),CAT,LID)
        c=catalog(self.project());c["checkpoint"]["event_sha256"]=D
        with self.assertRaisesRegex(AdmissionError,"CHECKPOINT_HEAD_MISMATCH"):
            validate_catalog(encode_proposal(c),CAT,LID)
    def test_successor_withdraw_revoke_and_no_reinstatement(self):
        old=self.view()
        w=self.view(state="WITHDRAWN",revision=2,event=2,receipt=D)
        r=self.view(state="REVOKED",revision=3,event=3,receipt="sha256:"+"b"*64)
        check_successor(old,w);check_successor(w,r)
        a=self.project()
        for c in (w,r):
            with self.assertRaisesRegex(AdmissionError,"RELEASE_NOT_SELECTABLE"):
                select_preview(c,a["module_id"],a["module_version"])
        with self.assertRaises(AdmissionError):check_successor(r,w)
        bad=deepcopy(r);bad["entries"][0]["state"]="WITHDRAWN"
        with self.assertRaises(AdmissionError):check_successor(r,bad)
    def test_same_checkpoint_or_changed_admission_rejected(self):
        old=self.view();c=deepcopy(old);c["entries"][0]["admission"]["display_name"]="altered"
        with self.assertRaisesRegex(AdmissionError,"CATALOG_SAME_CHECKPOINT_CONFLICT"):check_successor(old,c)
        new=self.view(state="WITHDRAWN",revision=2,event=2,receipt=D)
        new["entries"][0]["admission"]["artifact"]["sha256"]=D
        with self.assertRaisesRegex(AdmissionError,"IMMUTABLE_ADMISSION_CONFLICT"):check_successor(old,new)
    def test_entry_cannot_disappear(self):
        old=self.view();c=deepcopy(old);c["entries"]=[]
        c["checkpoint"]["event_sequence"]=2
        with self.assertRaisesRegex(AdmissionError,"CATALOG_ENTRY_DISAPPEARED"):check_successor(old,c)
    def test_no_positive_authority_or_unsupported_kind(self):
        a=self.project()
        for change in ({"installable":True},{"publication_committed":True},{"grants_authority":True}):
            with self.subTest(change=change),self.assertRaises(AdmissionError):checked("AdmissionRecord",{**a,**change})
        a["artifact"]["artifact_kind"]="native_binary"
        with self.assertRaises(AdmissionError):checked("AdmissionRecord",a)

if __name__=="__main__":unittest.main(verbosity=2)
