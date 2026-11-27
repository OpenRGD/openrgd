"""CORE-CAL-01A: actual pinned V1, adversarial disposable source snapshots."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from openrgd.core import canonical
from assessment import (ROOT, CORE_REF, PROFILE, assess_source, passes_requested_checks,
                        parse_conservative, manifest_preflight, parse_requirements,
                        AssessmentError, RequirementsError, sha)

REPO=ROOT.parents[2]
EXPECTED_ROOT="sha256:c049dc3fb91c19e668ef0d35b9b40d9052caf1a458b1a108d58b1896189dd5f9"
SCHEMA=json.loads((ROOT/"schemas/source-assessment.schema.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR=Draft202012Validator(SCHEMA)
BHL=(ROOT/"fixtures/bhl-genesis-required-paths.json").read_bytes()

def raw(obj):
    return (json.dumps(obj,ensure_ascii=True,sort_keys=True)+"\n").encode()

def requirements(paths,version="0.2.0"):
    return raw({"schema_version":"openrgd.required-source-profile.v0.1-candidate",
                "profile_id":"org.example.test-paths","profile_version":"0.1.0",
                "standard_version":version,"required_paths":paths})

def put(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)

def source_tree(root):
    spec=root/"spec";spec.mkdir()
    put(spec/"manifest.jsonc",raw({"meta_group":{
        "integrity_profile_str":PROFILE,"integrity_hash_str":"sha256:"+"0"*64,
        "rgd_standard_version_semver_str":"0.2.0"}}))
    put(spec/"01_foundation/description.jsonc",b'{"meta_group":{"model_id_str":"fixture"}}\n')
    canonical.update_manifest_integrity(spec)  # test-only seal, never assessment
    return spec

class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle=Path(self.tmp.name)/"fixture";self.bundle.mkdir()
        self.spec=source_tree(self.bundle)
    def report(self,policy=None,bundle=None):
        r=assess_source(bundle or self.bundle,policy)
        VALIDATOR.validate(r)
        for k in ("canonical_schema_validated","semantic_consistency_validated","kernel_selection_assessed",
                  "publisher_verified","robot_binding_verified","profile_model_hash_bound",
                  "physical_calibration_certified","actuation_enabled","grants_authority"):
            self.assertIs(r[k],False)
        return r
    def seal(self):
        return canonical.update_manifest_integrity(self.spec)
    def test_status_candidate(self):
        s=json.loads((ROOT/"STATUS.json").read_text())
        self.assertEqual(s["maturity"],"candidate")
        for k in ("accepted","normative","stable_release_allowed","runtime_implemented"):
            self.assertIs(s[k],False)
    def test_actual_bhl_root_and_independent_required_paths(self):
        r=self.report(BHL,REPO)
        self.assertTrue(r["core_source_files_pin_checked"])
        self.assertEqual(r["computed_source_tree_sha256"],EXPECTED_ROOT)
        self.assertEqual(r["declared_source_tree_sha256"],EXPECTED_ROOT)
        self.assertEqual(r["integrity_status"],"MATCH")
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
        self.assertEqual(len(r["source_index"]["files"]),76)
        self.assertEqual(r["source_index"],canonical.compute_integrity(REPO/"spec").index)
        print("BHL_REFERENCE_SYNTAX",r["indexed_jsonc_syntax_status"],json.dumps(r["diagnostics"]))
        self.assertEqual(r["indexed_jsonc_syntax_status"],"PASS")
    def test_no_policy_never_claims_completeness(self):
        r=self.report()
        self.assertEqual(r["integrity_status"],"MATCH")
        self.assertEqual(r["indexed_jsonc_syntax_status"],"PASS")
        self.assertEqual(r["required_paths_status"],"NOT_ASSESSED")
        self.assertTrue(passes_requested_checks(r))
    def test_self_consistent_partial_tree_fails_external_requirements(self):
        r=self.report(BHL)
        self.assertEqual(r["integrity_status"],"MATCH")
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_MISSING")
        self.assertIn("00_core/kernel.jsonc",r["missing_required_paths"])
        self.assertFalse(passes_requested_checks(r))
    def test_present_paths_not_valid_schema_or_physical_model(self):
        r=self.report(requirements(["manifest.jsonc","01_foundation/description.jsonc"]))
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
        self.assertTrue(passes_requested_checks(r))
        self.assertFalse(r["canonical_schema_validated"])
        self.assertFalse(r["robot_binding_verified"])
    def test_version_mismatch_separate_from_root(self):
        r=self.report(requirements(["manifest.jsonc"],"0.3.0"))
        self.assertEqual(r["integrity_status"],"MATCH")
        self.assertEqual(r["required_paths_status"],"PROFILE_VERSION_MISMATCH")
        self.assertFalse(passes_requested_checks(r))
    def test_raw_manifest_digest_is_not_normalized_manifest_entry(self):
        r=self.report()
        by_path={x["path"]:x for x in r["source_index"]["files"]}
        actual={x["path"]:x for x in r["raw_file_commitments"]}
        manifest=(self.spec/"manifest.jsonc").read_bytes()
        self.assertEqual(actual["manifest.jsonc"]["raw_sha256"],sha(manifest))
        self.assertNotEqual(actual["manifest.jsonc"]["raw_sha256"],"sha256:"+by_path["manifest.jsonc"]["sha256"])
        for name,item in actual.items():
            if name!="manifest.jsonc":
                self.assertEqual(item["raw_sha256"],"sha256:"+by_path[name]["sha256"])
    def test_assessment_does_not_write_or_reseal(self):
        before={x.relative_to(self.bundle):x.read_bytes() for x in self.bundle.rglob("*") if x.is_file()}
        self.report();self.report(BHL)
        self.assertEqual(before,{x.relative_to(self.bundle):x.read_bytes() for x in self.bundle.rglob("*") if x.is_file()})
    def test_root_mismatch_does_not_erase_syntax_or_path_assessment(self):
        path=self.spec/"01_foundation/description.jsonc"
        path.write_bytes(path.read_bytes()+b"// changed exact source bytes\n")
        r=self.report(requirements(["manifest.jsonc", "01_foundation/description.jsonc"]))
        self.assertEqual(r["integrity_status"],"MISMATCH")
        self.assertEqual(r["indexed_jsonc_syntax_status"],"PASS")
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
        self.assertFalse(passes_requested_checks(r))
    def test_matching_root_does_not_prove_jsonc_syntax(self):
        put(self.spec/"01_foundation/description.jsonc",b'{"x":1,"x":2}')
        self.seal()
        r=self.report(requirements(["01_foundation/description.jsonc"]))
        self.assertEqual(r["integrity_status"],"MATCH")
        self.assertEqual(r["indexed_jsonc_syntax_status"],"FAIL")
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
        self.assertIn({"code":"JSONC_DUPLICATE_KEY","path":"01_foundation/description.jsonc"},r["diagnostics"])
        self.assertFalse(passes_requested_checks(r))
    def test_excluded_generated_and_json_not_in_source_index(self):
        base=self.report()
        put(self.spec/"openrgd_unified_spec.jsonc",b'{invalid generated')
        put(self.spec/"01_foundation/calibration.json",b'{}')
        r=self.report(requirements(["openrgd_unified_spec.jsonc"]))
        self.assertEqual(r["computed_source_tree_sha256"],base["computed_source_tree_sha256"])
        self.assertEqual(r["indexed_jsonc_syntax_status"],"PASS")
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_MISSING")
        self.assertNotIn("01_foundation/calibration.json",{x["path"] for x in r["raw_file_commitments"]})
    def manifest_case(self,data,code,status="REJECTED"):
        put(self.spec/"manifest.jsonc",data)
        r=self.report()
        self.assertEqual(r["manifest_status"],status)
        self.assertIsNone(r["computed_source_tree_sha256"])
        self.assertIsNone(r["source_index"])
        self.assertIn({"code":code,"path":"manifest.jsonc"},r["diagnostics"])
    def test_ambiguous_comment_self_hash_rejected_before_v1(self):
        data=(self.spec/"manifest.jsonc").read_bytes()
        with patch("assessment.canonical.compute_integrity",side_effect=AssertionError("V1 must not run")):
            self.manifest_case(b'// "integrity_hash_str": "sha256:OTHER"\n'+data,"MANIFEST_SELF_FIELD_AMBIGUOUS")
    def test_duplicate_decoded_manifest_keys_rejected(self):
        data=(self.spec/"manifest.jsonc").read_bytes()
        self.manifest_case(data.replace(b'"meta_group":',b'"meta_group":{},"meta_group":',1),"JSONC_DUPLICATE_KEY")
    def test_escaped_self_hash_key_not_silently_normalized(self):
        data=(self.spec/"manifest.jsonc").read_bytes()
        self.manifest_case(data.replace(b'"integrity_hash_str"',b'"\\u0069ntegrity_hash_str"'),"MANIFEST_SELF_FIELD_AMBIGUOUS")
    def test_self_hash_in_wrong_path_rejected(self):
        m=json.loads((self.spec/"manifest.jsonc").read_bytes())
        m["integrity_hash_str"]=m["meta_group"].pop("integrity_hash_str")
        self.manifest_case(raw(m),"MANIFEST_SELF_FIELD_AMBIGUOUS")
    def test_second_hash_field_in_nested_object_rejected(self):
        m=json.loads((self.spec/"manifest.jsonc").read_bytes())
        m["other"]={"integrity_hash_str":"sha256:"+"a"*64}
        self.manifest_case(raw(m),"MANIFEST_SELF_FIELD_AMBIGUOUS")
    def test_unknown_integrity_profile_no_fallback_hash(self):
        data=(self.spec/"manifest.jsonc").read_bytes()
        self.manifest_case(data.replace(PROFILE.encode(),b"UNSUPPORTED"),"UNSUPPORTED_INTEGRITY_PROFILE","UNSUPPORTED_PROFILE")
    def test_invalid_declared_digest_no_root(self):
        m=json.loads((self.spec/"manifest.jsonc").read_bytes())
        m["meta_group"]["integrity_hash_str"]="sha256:SELF"
        self.manifest_case(raw(m),"MANIFEST_DIGEST_INVALID")
    def test_missing_manifest_and_mirror_only(self):
        (self.spec/"manifest.jsonc").unlink()
        self.assertIn({"code":"MANIFEST_MISSING","path":"manifest.jsonc"},self.report()["diagnostics"])
        shutil.rmtree(self.spec);(self.bundle/"standard").mkdir()
        self.assertEqual(self.report()["input_status"],"SOURCE_TREE_UNAVAILABLE")
    def test_direct_spec_directory(self):
        self.assertEqual(self.report(bundle=self.spec),self.report())
    def test_symlink_entry_rejected(self):
        (self.spec/"link.jsonc").symlink_to(self.spec/"manifest.jsonc")
        r=self.report()
        self.assertEqual(r["input_status"],"SNAPSHOT_REJECTED")
        self.assertFalse(r["core_source_files_pin_checked"])
    def test_casefold_path_collision_rejected(self):
        put(self.spec/"01_foundation/Description.jsonc",b'{}')
        self.assertEqual(self.report()["input_status"],"SNAPSHOT_REJECTED")
    def test_oversized_tree_rejected_before_hash(self):
        put(self.spec/"too-large.jsonc",b'x'*4194305)
        self.assertIn({"code":"SOURCE_BYTE_LIMIT","path":None},self.report()["diagnostics"])
    def test_wrong_core_pin_fails_closed(self):
        with patch("assessment.CORE_BLOBS",{"canonical.py":"0"*40}), \
             patch("assessment.canonical.compute_integrity",side_effect=AssertionError("V1 must not run")):
            r=self.report()
        self.assertEqual(r["integrity_status"],"VERIFICATION_FAILED")
        self.assertFalse(r["core_source_files_pin_checked"])
    def test_invalid_external_policy_is_not_reinterpreted(self):
        for policy in (requirements(["../outside.jsonc"]),requirements(["manifest.jsonc","manifest.jsonc"]),
                       requirements(["manifest.jsonc","MANIFEST.jsonc"]),b'{"x":1,"x":2}',b'{}'):
            with self.subTest(policy=policy),self.assertRaises(RequirementsError):
                assess_source(self.bundle,policy)
    def test_cli_json_and_exit_scope(self):
        script=ROOT/"assessment.py"
        run=subprocess.run([sys.executable,str(script),"--bundle",str(self.bundle)],capture_output=True,timeout=20)
        self.assertEqual(run.returncode,0,run.stderr.decode())
        self.assertEqual(json.loads(run.stdout),self.report())
        run=subprocess.run([sys.executable,str(script),"--bundle",str(self.bundle),
                            "--required-profile",str(ROOT/"fixtures/bhl-genesis-required-paths.json")],capture_output=True,timeout=20)
        self.assertEqual(run.returncode,2,run.stderr.decode())
        self.assertEqual(json.loads(run.stdout)["required_paths_status"],"REQUIRED_PATHS_MISSING")

class ParserTests(unittest.TestCase):
    def test_duplicate_decoded_keys_and_nonfinite_numbers(self):
        for data,code in [(b'{"x":1,"\\u0078":2}',"JSONC_DUPLICATE_KEY"),(b'{"x":1e999}',"JSONC_NONFINITE_NUMBER"),
                          (b'{"x":NaN}',"JSONC_NONFINITE_NUMBER"),(b'{"x":Infinity}',"JSONC_NONFINITE_NUMBER")]:
            with self.subTest(data=data),self.assertRaisesRegex(AssessmentError,code):
                parse_conservative(data)
    def test_trailing_comma_and_unterminated_comment(self):
        for data,code in [(b'{"x":1,}',"JSONC_INVALID"),(b'{"x":1}/* incomplete',"JSONC_UNTERMINATED_COMMENT"),
                          (b'{"x":1/*comment*/2}',"JSONC_INVALID")]:
            with self.subTest(data=data),self.assertRaisesRegex(AssessmentError,code):
                parse_conservative(data)
    def test_comments_inside_strings_not_stripped(self):
        _,_,value=parse_conservative(b'{"uri":"https://example.invalid/a/*b*/","value":1 /* ok */}')
        self.assertEqual(value,{"uri":"https://example.invalid/a/*b*/","value":1})
    def test_backslash_parity_legacy_disagreement_is_rejected(self):
        # Legacy stripper counts at most two preceding backslashes. Three
        # backslashes before a quote means it remains inside the JSON string.
        data=b'{"x":"a'+b'\\'*3+b'"//literal"}'
        with self.assertRaisesRegex(AssessmentError,"LEGACY_PARSER_DISAGREEMENT"):
            parse_conservative(data)
    def test_invalid_utf8_surrogate_control_and_nonobject(self):
        for data in (b'{"x":"\xff"}',b'{"x":"\\ud800"}',b'{"x":"\x01"}',b'[]'):
            with self.subTest(data=data),self.assertRaises(AssessmentError):
                parse_conservative(data)
    def test_bounded_structure(self):
        data=b'{"x":'+b'['*70+b'0'+b']'*70+b'}'
        with self.assertRaisesRegex(AssessmentError,"JSONC_STRUCTURE_LIMIT"):
            parse_conservative(data)

if __name__=="__main__":
    unittest.main(verbosity=2)
