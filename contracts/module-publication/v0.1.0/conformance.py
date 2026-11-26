"""Exact historical schema/fixture and new publication envelope checks. No I/O except test fixture reads."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import os
import unittest
from unittest.mock import patch
import socket
import subprocess
from proposal import (ROOT,HIST,DOCS,EXT,CLI,PUB, ProposalError, parse,
                      digest,validate,propose,inspect_manifest,compare_same_key,encode_proposal)
from rgd_registry import core as legacy

MOTION="extensions/motion.json"
FACADE="cli/motion.json"
SOMATIC="extensions/somatic.json"
def load(path):
    return path.read_bytes()
EXT_RAW=load(HIST/"extensions/v0.1.0/examples/manifests/motion.json")
CLI_RAW=load(HIST/"command-plugin/v0.1.0/migration/rgd-motion.json")
SOM_RAW=load(HIST/"extensions/v0.1.0/examples/manifests/somatic-runtime.json")
def raw(v):
    return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def source():
    return raw({"repository_uri":"https://example.invalid/synthetic/review","git_commit":"a"*40})
def fixture():
    d={MOTION:EXT_RAW,FACADE:CLI_RAW}
    m={
        "schema_version":"openrgd.module-manifest.v0.1-candidate",
        "module_id":"org.example.test-motion","module_version":"0.1.0-dev.0",
        "display_name":"Synthetic publication probe",
        "functional_roles":["motion_planning"],
        "extension_descriptors":[{"path":MOTION,"sha256":digest(EXT_RAW)}],
        "command_facades":[{"descriptor":{"path":FACADE,"sha256":digest(CLI_RAW)},
                            "extension_descriptor_path":MOTION,"artifact_slot_id":"wheel"}],
        "artifact_slots":[{"slot_id":"wheel","artifact_kind":"python_wheel",
                           "media_type":"application/zip","platform_profile":"synthetic-only",
                           "package_name":"rgd-motion","package_version":"0.1.13.dev0",
                           "extension_descriptor_paths":[MOTION]}],
        "dependencies":[],"grants_authority":False,
    }
    return m,d,{"wheel":b"not a real wheel; fixture only"}

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.m,self.d,self.a=fixture()
    def project(self):
        return propose(raw(self.m),self.d,self.a,source())
    def change_descriptor(self,path,obj):
        self.d[path]=raw(obj)
        for r in self.m["extension_descriptors"]+[x["descriptor"] for x in self.m["command_facades"]]:
            if r["path"]==path:r["sha256"]=digest(self.d[path])
    def test_exact_historical_files(self):
        expected={
            "extensions/v0.1.0/schemas/extension-manifest.schema.json":"8279a0f69737e8f3704e4d09f326c073ad2ad61b3d7b1f10df694803f8f80a33",
            "extensions/v0.1.0/schemas/composition.schema.json":"16c4d3d88de53ba3f853a805ebbebfcfe837753d457d423a615683d525a6d2cb",
            "command-plugin/v0.1.0/schemas/command-plugin.schema.json":"8d666cb1f554223503df3381efd0b43f70a7e7186b44163b2ec1010456f12294",
            "extensions/v0.1.0/examples/manifests/motion.json":"31eddf1387444f3bce913bd54fbc74d132842bd2935ae9da2de254a3666db3a3",
            "extensions/v0.1.0/examples/manifests/somatic-runtime.json":"fd4abe4d3e9d811194968056c9491ec6624f82ecfdbdc6f917a4222b5ff6474f",
            "command-plugin/v0.1.0/migration/rgd-motion.json":"2f1acd8f46674d4c8329e6a2bf7d096d6a2bfa6d36a091f7d8909d0aea0694f9"
        }
        for path,h in expected.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((HIST/path).read_bytes()).hexdigest(),h)
        self.assertEqual(DOCS[2]["properties"]["cli"],DOCS[4]["properties"]["cli"])
    def test_status_remains_candidate(self):
        s=parse((ROOT/"STATUS.json").read_bytes())
        self.assertEqual(s["maturity"],"candidate")
        for k in ("accepted","normative","stable_release_allowed","runtime_implemented","publication_implemented"):
            self.assertIs(s[k],False)
    def test_actual_legacy_fixture_to_proposal(self):
        p=self.project()
        self.assertEqual(p["manifest_sha256"],digest(raw(self.m)))
        self.assertEqual(p["artifact_commitments"],[{"slot_id":"wheel","sha256":digest(self.a["wheel"]),
                                                     "size_bytes":len(self.a["wheel"])}])
        self.assertEqual(p["publication_status"],"review_required")
        for k in ("publisher_verified","source_commit_verified","artifact_format_verified","installable","grants_authority"):
            self.assertIs(p[k],False)
        self.assertNotIn("capabilities",p)
        self.assertNotIn("cli",p)
    def test_deterministic_and_exact_manifest_bytes(self):
        p=self.project()
        self.assertEqual(encode_proposal(p),encode_proposal(self.project()))
        q=propose(raw(self.m)+b"\n",self.d,self.a,source())
        self.assertNotEqual(q["manifest_sha256"],p["manifest_sha256"])
        with self.assertRaisesRegex(ProposalError,"RELEASE_KEY_CONTENT_CONFLICT"):
            compare_same_key(encode_proposal(p),encode_proposal(q))
    def test_same_release_retry_and_changed_artifact(self):
        a=encode_proposal(self.project())
        self.assertEqual(compare_same_key(a,a),"SAME_PROPOSAL")
        self.a["wheel"]+=b"changed"
        b=encode_proposal(self.project())
        with self.assertRaisesRegex(ProposalError,"RELEASE_KEY_CONTENT_CONFLICT"):
            compare_same_key(a,b)
        self.m["module_version"]="0.2.0"
        self.assertEqual(compare_same_key(a,encode_proposal(self.project())),"DISTINCT_RELEASE_KEY")
    def test_duplicate_artifact_commitment_rejected_by_compare(self):
        q=self.project()
        changed=deepcopy(q)
        changed["artifact_commitments"].append({**q["artifact_commitments"][0],"sha256":"sha256:"+"b"*64})
        with self.assertRaisesRegex(ProposalError,"NONCANONICAL_COMMITMENT_SET"):
            compare_same_key(raw(q),raw(changed))
    def test_descriptor_bytes_cannot_change(self):
        self.d[MOTION]+=b" "
        with self.assertRaisesRegex(ProposalError,"DESCRIPTOR_DIGEST_MISMATCH"):self.project()
    def test_missing_or_extra_descriptor(self):
        del self.d[FACADE]
        with self.assertRaisesRegex(ProposalError,"DESCRIPTOR_SET_MISMATCH"):self.project()
    def test_cli_projection_mismatch(self):
        cli=parse(CLI_RAW);cli["cli"]["namespace"]="renamed"
        self.change_descriptor(FACADE,cli)
        with self.assertRaisesRegex(ProposalError,"CLI_EXTENSION_MISMATCH"):self.project()
    def test_package_native_version_not_silently_normalized(self):
        self.m["artifact_slots"][0]["package_version"]="0.1.13-dev.0"
        with self.assertRaisesRegex(ProposalError,"CLI_ARTIFACT_MISMATCH"):self.project()
    def test_legacy_package_version_not_module_release_key(self):
        self.m["module_version"]="0.1.13.dev0"
        with self.assertRaisesRegex(ProposalError,"MANIFEST_SHAPE"):self.project()
    def test_missing_cli_facade(self):
        self.m["command_facades"]=[];del self.d[FACADE]
        with self.assertRaisesRegex(ProposalError,"CLI_FACADE_SET_MISMATCH"):self.project()
    def test_invalid_cli_authority(self):
        cli=parse(CLI_RAW);cli["grants_authority"]=True
        self.change_descriptor(FACADE,cli)
        with self.assertRaisesRegex(ProposalError,"CLI_DESCRIPTOR_SHAPE"):self.project()
    def test_invalid_extension_authority(self):
        ext=parse(EXT_RAW);ext["authority"]["grants_authority"]=True
        self.change_descriptor(MOTION,ext)
        with self.assertRaisesRegex(ProposalError,"EXTENSION_SHAPE"):self.project()
    def test_duplicate_slot_id(self):
        alt=deepcopy(self.m["artifact_slots"][0]);alt["platform_profile"]="another"
        self.m["artifact_slots"].append(alt)
        with self.assertRaisesRegex(ProposalError,"DUPLICATE_ARTIFACT_SLOT"):self.project()
    def test_unknown_extension_binding(self):
        self.m["artifact_slots"][0]["extension_descriptor_paths"]=["missing.json"]
        with self.assertRaisesRegex(ProposalError,"UNKNOWN_EXTENSION_BINDING"):self.project()
    def test_artifact_set_mismatch(self):
        self.a["other"]=b"extra"
        with self.assertRaisesRegex(ProposalError,"ARTIFACT_SET_MISMATCH"):self.project()
    def test_manifest_cannot_self_publish(self):
        self.m["publication_status"]="published"
        with self.assertRaisesRegex(ProposalError,"MANIFEST_SHAPE"):self.project()
    def test_source_commit_is_not_floating(self):
        with self.assertRaisesRegex(ProposalError,"SOURCE_CLAIM_SHAPE"):
            propose(raw(self.m),self.d,self.a,raw({"repository_uri":"https://example.invalid/repo","git_commit":"main"}))
    def test_self_dependency_blocked(self):
        self.m["dependencies"]=[{"module_id":self.m["module_id"],"module_version":"0.1.0"}]
        with self.assertRaisesRegex(ProposalError,"DEPENDENCY_DECLARATION_CONFLICT"):self.project()
    def test_path_traversal_and_duplicate_json(self):
        self.m["extension_descriptors"][0]["path"]="../motion.json"
        with self.assertRaises(ProposalError):self.project()
        for text in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e1000}',b'{"x":"\\ud800"}'):
            with self.subTest(text=text),self.assertRaises(ProposalError):parse(text)
    def test_artifact_size_limit(self):
        self.a["wheel"]=b"x"*1048577
        with self.assertRaisesRegex(ProposalError,"INPUT_BYTES_LIMIT"):self.project()
    def test_native_binary_legacy_descriptor_without_cli(self):
        self.m["command_facades"]=[]
        self.m["extension_descriptors"]=[{"path":SOMATIC,"sha256":digest(SOM_RAW)}]
        self.m["artifact_slots"]=[{"slot_id":"binary","artifact_kind":"native_binary",
            "media_type":"application/octet-stream","platform_profile":"synthetic-only",
            "package_name":"openrgd-somatic-runtime","package_version":"0.1.0.dev0",
            "extension_descriptor_paths":[SOMATIC]}]
        self.d={SOMATIC:SOM_RAW};self.a={"binary":b"not a real executable"}
        p=self.project()
        self.assertFalse(p["installable"])
        self.assertFalse(p["grants_authority"])
    def test_no_socket_subprocess_or_runtime_import(self):
        with patch.object(socket,"socket",side_effect=AssertionError("network")),patch.object(subprocess,"Popen",side_effect=AssertionError("process")):
            self.project()

class LegacyRegistryTests(unittest.TestCase):
    def test_actual_catalog_remains_legacy_and_rejects_new_proposal(self):
        root=Path(os.environ["REGISTRY_CHECKOUT"])
        cal=Path(os.environ["CAL_CHECKOUT"])
        with patch.object(legacy,"REGISTRY_ROOT",root/"registry"):
            d=legacy.entry("org.openrgd.calibration","0.2.0")
        m=parse((cal/"module.openrgd.json").read_bytes())
        self.assertEqual(d["id"],m["module_id"])
        self.assertEqual(d["version"],m["module_version"])
        self.assertEqual(set(d["capabilities"]),set(m["capabilities"]))
        self.assertEqual(d["source"]["commit_sha"],"81700401e2fa6d370a86b6c1f5a48802bc5f1fc7")
        self.assertEqual(d["distribution"]["kind"],"pinned_git_cargo")
        # No silent conversion to a new wrapper/CLI descriptor.
        with self.assertRaisesRegex(ProposalError,"MANIFEST_SHAPE"):
            inspect_manifest((cal/"module.openrgd.json").read_bytes(),{})
        a,b,c=fixture()
        p=propose(raw(a),b,c,source())
        with self.assertRaises(legacy.RegistryError):
            legacy._validate_descriptor(p)

if __name__=="__main__":
    unittest.main(verbosity=2)
