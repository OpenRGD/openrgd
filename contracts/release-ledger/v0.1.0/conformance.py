"""Candidate-only contract tests; no DB or authentication."""
from copy import deepcopy
import unittest
from ledger_contract import (checked, decode, transition, validate_evidence, make_receipt,
                             LedgerContractError, ROOT, parse, digest, encode_proposal)

A="sha256:"+"a"*64
B="sha256:"+"b"*64
C="sha256:"+"c"*64
CAT="org.example.catalog"
LID="00000000-0000-4000-8000-000000000001"
RID="00000000-0000-4000-8000-000000000002"
def fixture():
    p={"schema_version":"openrgd.module-release-proposal.v0.1-candidate",
       "module_id":"org.example.fixture","module_version":"1.0.0",
       "manifest_sha256":A,"source_claim":{"repository_uri":"https://example.invalid/project","git_commit":"a"*40},
       "artifact_commitments":[{"slot_id":"wheel","sha256":B,"size_bytes":12}],
       "publication_status":"review_required","publisher_verified":False,
       "source_commit_verified":False,"artifact_format_verified":False,
       "extension_semantics_verified":False,"dependency_resolution_verified":False,
       "installable":False,"grants_authority":False}
    proposal=encode_proposal(p)
    e=encode_proposal({"schema_version":"openrgd.registry-review-target.v0.1-candidate",
         "module_id":p["module_id"],"module_version":p["module_version"],"publisher_namespace":"org.example",
         "proposal_sha256":digest(proposal),"inspection_sha256":C,"disposition":"REVIEWED_CANDIDATE",
         "publication_committed":False,"installable":False,"grants_authority":False})
    r={"schema_version":"openrgd.release-ledger-request.v0.1-candidate",
       "catalog_id":CAT,"ledger_id":LID,"request_id":RID,
       "module_id":p["module_id"],"module_version":p["module_version"],
       "operation":"RESERVE_CANDIDATE","expected_revision":0,"proposal_sha256":digest(proposal),
       "evidence_sha256":digest(e),"reason_code":"CANDIDATE_REVIEW","grants_authority":False}
    return r,proposal,e

def control(r,op,rev):
    x={**r,"operation":op,"expected_revision":rev,"reason_code":"SECURITY" if op=="REVOKE" else "POLICY"}
    notice={k:v for k,v in x.items() if k!="evidence_sha256"}
    notice["schema_version"]="openrgd.release-disposition-notice.v0.1-candidate"
    evidence=encode_proposal(notice)
    x["evidence_sha256"]=digest(evidence)
    return x,evidence

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.r,self.p,self.e=fixture()
        self.first=make_receipt(self.r,encode_proposal(self.r),b"fixture context",1,None,None)
    def test_candidate_maturity(self):
        s=parse((ROOT/"STATUS.json").read_bytes())
        self.assertEqual(s["maturity"],"candidate")
        for k in ("accepted","normative","runtime_implemented","publication_implemented","stable_release_allowed"):
            self.assertIs(s[k],False)
    def test_first_receipt_and_negative_authority(self):
        validate_evidence(self.r,self.p,self.e)
        self.assertEqual(self.first["state_after"],"RESERVED_CANDIDATE")
        self.assertEqual(self.first["request_sha256"],digest(encode_proposal(self.r)))
        self.assertTrue(self.first["committed_to_candidate_ledger"])
        for key in ("publication_committed","installable","grants_authority"):
            self.assertIs(self.first[key],False)
            with self.assertRaises(LedgerContractError):
                checked("ReleaseLedgerReceipt",{**self.first,key:True})
    def test_never_implicit_publish(self):
        for op in ("PUBLISH","REINSTATE","DELETE"):
            with self.subTest(op=op),self.assertRaises(LedgerContractError):
                checked("ReleaseLedgerRequest",{**self.r,"operation":op})
    def test_revision_and_reason_required(self):
        for changes in ({"expected_revision":1},{"reason_code":"SECURITY"},{"expected_revision":True},
                        {"module_version":"latest"},{"catalog_id":"bad"},{"request_id":"short"}):
            with self.subTest(changes=changes),self.assertRaises(LedgerContractError):
                checked("ReleaseLedgerRequest",{**self.r,**changes})
    def test_content_and_scope_conflict(self):
        for changes,code in (({"proposal_sha256":A},"RELEASE_KEY_CONTENT_CONFLICT"),
                             ({"catalog_id":"org.other.catalog"},"RELEASE_SCOPE_MISMATCH")):
            with self.subTest(changes=changes),self.assertRaisesRegex(LedgerContractError,code):
                transition({**self.r,**changes},self.first)
        with self.assertRaisesRegex(LedgerContractError,"RELEASE_ALREADY_RESERVED"):
            transition(self.r,self.first)
    def test_evidence_exact_binding(self):
        with self.assertRaisesRegex(LedgerContractError,"LEDGER_COMMITMENT_MISMATCH"):
            validate_evidence(self.r,self.p,self.e+b" ")
        e=parse(self.e);e["disposition"]="WITHDRAWN"
        raw=encode_proposal(e)
        with self.assertRaisesRegex(LedgerContractError,"REVIEW_TARGET_BINDING_MISMATCH"):
            validate_evidence({**self.r,"evidence_sha256":digest(raw)},self.p,raw)
    def test_withdraw_and_terminal_revoke(self):
        w,e=control(self.r,"WITHDRAW",1)
        validate_evidence(w,self.p,e)
        wrec=make_receipt(w,encode_proposal(w),b"context",2,digest(encode_proposal(self.first)),self.first)
        self.assertEqual(wrec["state_after"],"WITHDRAWN")
        revoke,notice=control(self.r,"REVOKE",2)
        validate_evidence(revoke,self.p,notice)
        rec=make_receipt(revoke,encode_proposal(revoke),b"context",3,digest(encode_proposal(wrec)),wrec)
        self.assertEqual(rec["state_after"],"REVOKED")
        self.assertEqual(rec["release_revision"],3)
        with self.assertRaisesRegex(LedgerContractError,"TERMINAL_RELEASE_STATE"):
            transition(control(self.r,"REVOKE",3)[0],rec)
        with self.assertRaisesRegex(LedgerContractError,"RELEASE_ALREADY_RESERVED"):
            transition(self.r,rec)
    def test_stale_revision_or_unknown_release(self):
        w,e=control(self.r,"WITHDRAW",2)
        with self.assertRaisesRegex(LedgerContractError,"STALE_RELEASE_REVISION"):transition(w,self.first)
        with self.assertRaisesRegex(LedgerContractError,"RELEASE_UNKNOWN"):transition(w,None)
    def test_notice_request_binding(self):
        w,e=control(self.r,"WITHDRAW",1)
        with self.assertRaisesRegex(LedgerContractError,"DISPOSITION_NOTICE_BINDING_MISMATCH"):
            validate_evidence({**w,"request_id":"00000000-0000-4000-8000-000000000099"},self.p,e)
    def test_checkpoint_genesis_and_chain(self):
        c={"schema_version":"openrgd.release-ledger-checkpoint.v0.1-candidate","catalog_id":CAT,
           "ledger_id":LID,"legacy_catalog_sha256":A,"event_sequence":0,"event_sha256":None,
           "grants_authority":False}
        checked("ReleaseLedgerCheckpoint",c)
        with self.assertRaises(LedgerContractError):checked("ReleaseLedgerCheckpoint",{**c,"event_sha256":A})
        with self.assertRaises(LedgerContractError):checked("ReleaseLedgerCheckpoint",{**c,"event_sequence":1})
        checked("ReleaseLedgerCheckpoint",{**c,"event_sequence":1,"event_sha256":digest(encode_proposal(self.first))})
    def test_parser_fail_closed(self):
        for raw in (b'{"operation":1,"operation":2}',b'{"expected_revision":0.0}',b'{"x":NaN}',b'{}'):
            with self.subTest(raw=raw),self.assertRaises(LedgerContractError):
                decode("ReleaseLedgerRequest",raw)

if __name__=="__main__":
    unittest.main(verbosity=2)
