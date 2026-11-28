"""Actual Git and DSSE verification; independently mutated signed fixtures."""
import base64
import csv
from copy import deepcopy
import hashlib
from io import BytesIO,StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from securesystemslib.signer import CryptoSigner
from proposal import parse,digest,encode_proposal
from wheel_inspection import read_archive
from provenance import ROOT,verify_provenance,ProvenanceError,source_inventory,policy_from_bytes
from provenance_fixture import (build_source_fixture,verification_inputs,statement_for,
                                sign_statement,PACKAGE,run)

def changed_wheel(raw):
    files=read_archive(raw)
    files[PACKAGE+"/__init__.py"]+=b"\n# altered package code\n"
    record=next(p for p in files if p.endswith(".dist-info/RECORD"))
    text=StringIO(newline="");writer=csv.writer(text,lineterminator="\n")
    for path,data in sorted(files.items()):
        if path==record:continue
        h=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        writer.writerow([path,"sha256="+h,str(len(data))])
    writer.writerow([record,"",""]);files[record]=text.getvalue().encode()
    out=BytesIO()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p,b in files.items():z.writestr(p,b)
    return out.getvalue()

class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.fixture=build_source_fixture(cls.temp.name)
    def args(self,**kwargs):return verification_inputs(self.fixture,**kwargs)
    def check(self,**kwargs):return verify_provenance(**self.args(**kwargs))
    def test_candidate_only(self):
        s=json.loads((ROOT/"STATUS.json").read_bytes())
        for k in ("normative","accepted","stable_release_allowed","runtime_implemented","publication_implemented"):
            self.assertIs(s[k],False)
    def test_real_commit_build_dsse_and_wheel_package(self):
        args=self.args();r=verify_provenance(**args)
        for k in ("source_commit_membership_verified","builder_signature_verified","builder_policy_matched","wheel_package_bytes_matched"):
            self.assertIs(r[k],True)
        for k in ("build_execution_independently_verified","dependency_materials_complete","reproducible_build_verified",
                  "slsa_level_verified","publisher_verified","publication_committed","installable","grants_authority"):
            self.assertIs(r[k],False)
        self.assertEqual(r["proposal_sha256"],digest(args["submitted_proposal_raw"]))
        self.assertEqual(r["artifact_sha256"],digest(args["artifact_bytes"]["wheel"]))
        self.assertEqual(r["attestation_sha256"],digest(args["attestation_raw"]))
        self.assertEqual(r["policy_sha256"],digest(args["policy_raw"]))
        self.assertEqual(r["git_commit"],run(["git","rev-parse","HEAD"],self.fixture["repository"]).decode().strip())
        self.assertNotIn(PACKAGE,sys.modules)
        print("PROVENANCE_FIXTURE",json.dumps({k:r[k] for k in ("git_commit","source_tree_sha256","recipe_sha256","artifact_sha256")},sort_keys=True))
    def test_dirty_worktree_not_used_as_source(self):
        repo=self.fixture["repository"];path=repo/PACKAGE/"__init__.py";original=path.read_bytes()
        try:
            path.write_bytes(b"not committed")
            self.assertTrue(self.check()["wheel_package_bytes_matched"])
        finally:path.write_bytes(original)
    def test_wrong_signer(self):
        with self.assertRaises(ProvenanceError):self.check(signer=CryptoSigner.generate_ed25519())
    def test_payload_tamper_without_resigning(self):
        args=self.args();env=parse(args["attestation_raw"])
        statement=parse(base64.b64decode(env["payload"]))
        statement["predicate"]["runDetails"]["builder"]["id"]="https://example.invalid/other"
        env["payload"]=base64.b64encode(encode_proposal(statement)).decode()
        args["attestation_raw"]=encode_proposal(env)
        with self.assertRaisesRegex(ProvenanceError,"BUILDER_ATTESTATION_REJECTED"):verify_provenance(**args)
    def test_valid_signature_wrong_subject_or_builder_or_recipe(self):
        for variant in ("subject","builder","recipe","build_type","extra_parameter","source"):
            st=statement_for(self.fixture)
            d=st["predicate"]["buildDefinition"]
            if variant=="subject":st["subject"][0]["digest"]["sha256"]="b"*64
            if variant=="builder":st["predicate"]["runDetails"]["builder"]["id"]="https://example.invalid/other"
            if variant=="recipe":d["resolvedDependencies"][1]["digest"]["sha256"]="b"*64
            if variant=="build_type":d["buildType"]="https://example.invalid/other"
            if variant=="extra_parameter":d["externalParameters"]["unreviewed"]=True
            if variant=="source":d["resolvedDependencies"][0]["digest"]["gitCommit"]="b"*40
            with self.subTest(variant=variant),self.assertRaisesRegex(ProvenanceError,"ATTESTATION_BINDING_MISMATCH"):
                self.check(statement=st)
    def test_source_claim_wrong_uri_or_commit(self):
        for k,v in (("repository_uri","https://example.invalid/another"),("git_commit","b"*40)):
            inputs=deepcopy(self.fixture["inputs"]);src=parse(inputs["source_claim"]);src[k]=v;inputs["source_claim"]=encode_proposal(src)
            with self.subTest(k=k),self.assertRaisesRegex(ProvenanceError,"SOURCE_POLICY_MISMATCH"):self.check(inputs=inputs)
    def test_policy_scope_mismatch(self):
        p={**self.fixture["policy"],"module_id":"org.example.other"}
        with self.assertRaisesRegex(ProvenanceError,"RELEASE_POLICY_MISMATCH"):self.check(policy=p)
    def test_wrong_source_inventory_even_when_signed(self):
        f={**self.fixture,"policy":{**self.fixture["policy"],"source_tree_sha256":"sha256:"+"f"*64}}
        with self.assertRaisesRegex(ProvenanceError,"SOURCE_INVENTORY_MISMATCH"):
            verify_provenance(**verification_inputs(f))
    def test_wrong_recipe_even_when_signed(self):
        f={**self.fixture,"policy":{**self.fixture["policy"],"recipe_sha256":"sha256:"+"f"*64}}
        with self.assertRaisesRegex(ProvenanceError,"BUILD_RECIPE_MISMATCH"):
            verify_provenance(**verification_inputs(f))
    def test_modified_wheel_with_recomputed_record_and_resigned_subject(self):
        i=deepcopy(self.fixture["inputs"]);i["artifact_bytes"]["wheel"]=changed_wheel(i["artifact_bytes"]["wheel"])
        with self.assertRaisesRegex(ProvenanceError,"WHEEL_COMMITTED_PACKAGE_MISMATCH"):
            self.check(inputs=i)
    def test_missing_git_object_and_ref_not_commit(self):
        p=self.fixture["policy"];repo=self.fixture["repository"]
        for commit in ("HEAD","main","a"*40):
            with self.subTest(commit=commit),self.assertRaises(ProvenanceError):
                source_inventory(repo,commit,p["package_root"])
    def test_actual_git_tag_not_commit(self):
        repo=self.fixture["repository"]
        run(["git","-c","user.name=Test","-c","user.email=test@example.invalid","tag","-a","fixture-tag","-m","tag"],repo)
        try:
            tag=run(["git","rev-parse","fixture-tag"],repo).decode().strip()
            with self.assertRaisesRegex(ProvenanceError,"COMMIT_OBJECT_REQUIRED"):
                source_inventory(repo,tag,PACKAGE)
        finally:run(["git","tag","-d","fixture-tag"],repo)
    def test_invalid_policy_and_duplicate_envelope(self):
        for raw in (b'{}',b'{"x":1,"x":2}',encode_proposal({**self.fixture["policy"],"grants_authority":True})):
            with self.subTest(raw=raw),self.assertRaises(ProvenanceError):policy_from_bytes(raw)
        args=self.args();args["attestation_raw"]=b'{"payload":"a","payload":"b"}'
        with self.assertRaises(ProvenanceError):verify_provenance(**args)
    def test_wrong_payload_type_and_extra_signature(self):
        for field in ("type","duplicate"):
            args=self.args();e=parse(args["attestation_raw"])
            if field=="type":e["payloadType"]="application/json"
            else:e["signatures"].append(e["signatures"][0])
            args["attestation_raw"]=encode_proposal(e)
            with self.subTest(field=field),self.assertRaises(ProvenanceError):verify_provenance(**args)
    def test_symlink_or_submodule_not_supported(self):
        # A distinct trusted test repository, never the producer fixture.
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d);run(["git","init","--object-format=sha1"],repo)
            (repo/"pyproject.toml").write_text("fixture")
            (repo/PACKAGE).mkdir();(repo/PACKAGE/"__init__.py").write_text("")
            (repo/PACKAGE/"link").symlink_to("outside")
            run(["git","add","--all"],repo)
            run(["git","-c","user.name=Test","-c","user.email=test@example.invalid","commit","--no-gpg-sign","-m","fixture"],repo)
            commit=run(["git","rev-parse","HEAD"],repo).decode().strip()
            with self.assertRaisesRegex(ProvenanceError,"UNSUPPORTED_GIT_ENTRY"):
                source_inventory(repo,commit,PACKAGE)

if __name__=="__main__":unittest.main(verbosity=2)
