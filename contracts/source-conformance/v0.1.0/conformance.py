"""CORE-CAL-01B conformance on real reference and isolated synthetic sources."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from source_conformance import (ROOT,source,encoded,parse_profile,projection,
    assess_conformance,passes_scoped_checks,ConformanceError,validator,DOCS,
    MANIFEST,KERNEL,MASTER,DESCRIPTION,LIBRARY,TOPOLOGY,CALIBRATION,FIDELITY,HAL,RUNTIME,
    EMPTY_DIGEST,RULE_PROFILE)

REPO=ROOT.parents[2]
BHL=(ROOT/"fixtures/bhl-static-review-profile.json").read_bytes()
ROOT_HASH="sha256:c049dc3fb91c19e668ef0d35b9b40d9052caf1a458b1a108d58b1896189dd5f9"
EXCLUDED="06_ether/civilization_manifesto.jsonc"
EXTRA="01_foundation/future_component.jsonc"

def make_profile(required,optional=(),excluded=()):
    return {"schema_version":"openrgd.source-conformance-profile.v0.1-candidate",
        "profile_id":"org.example.static-review","profile_version":"0.1.0",
        "standard_version":"0.2.0","rule_profile":RULE_PROFILE,
        "inventory_policy":"EXPLICIT_CLASSIFICATION_REQUIRED",
        "components":[{"path":p,"applicability":a,"rationale":"Explicit synthetic test policy"}
                      for group,a in ((required,"REQUIRED"),(optional,"OPTIONAL"),(excluded,"NOT_APPLICABLE"))
                      for p in group]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bundle=Path(self.temp.name)/"fixture";self.bundle.mkdir()
        self.spec=self.bundle/"spec";self.spec.mkdir()
        self.put(MANIFEST,{"meta_group":{"integrity_hash_str":"sha256:"+"0"*64,
              "integrity_profile_str":source.PROFILE,"rgd_standard_version_semver_str":"0.2.0",
              "kernel_ref_str":KERNEL,"rgd_schema_ref_str":MASTER}})
        self.put(KERNEL,{"meta_group":{"id":"synthetic"},"module_loading_order_list":[DESCRIPTION]})
        self.put(MASTER,{"description":"test-only master meta-schema"})
        self.put(DESCRIPTION,{"joint_topology_map":{"joint_a":{}},
             "sensors_mounting_map":{"sensor_a":{}},"actuators_topology_map":{}})
        self.p=make_profile([MANIFEST,KERNEL,MASTER,DESCRIPTION],
            [LIBRARY,TOPOLOGY,CALIBRATION,FIDELITY,HAL,RUNTIME],[EXCLUDED])
        self.seal()
    def put(self,path,value):
        p=self.spec/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(value))
    def get(self,path):
        return json.loads((self.spec/path).read_bytes())
    def seal(self):
        source.canonical.update_manifest_integrity(self.spec) # test fixture only
    def report(self,p=None,bundle=None,seal=True):
        if seal and bundle is None:self.seal()
        r=assess_conformance(bundle or self.bundle,encoded(p or self.p))
        validator(DOCS[1],"ConformanceReport").validate(r)
        for key in ("canonical_schema_validated","semantic_consistency_validated","profile_governance_accepted",
                    "publisher_verified","robot_binding_verified","profile_model_hash_bound",
                    "physical_calibration_certified","actuation_enabled","grants_authority"):
            self.assertIs(r[key],False)
        return r
    def row(self,r,path):
        return next(x for x in r["components"] if x["path"]==path)
    def set_app(self,path,app):
        next(x for x in self.p["components"] if x["path"]==path)["applicability"]=app
    def set_kernel_modules(self,paths):
        k=self.get(KERNEL);k["module_loading_order_list"]=paths;self.put(KERNEL,k)
    def ref(self,r,rule,status,target=None):
        matches=[x for x in r["references"] if x["rule_id"]==rule and x["status"]==status
                 and (target is None or x["target_symbol"]==target or x["target_path"]==target)]
        self.assertTrue(matches,(rule,status,target,r["references"]))
        return matches[0]
    def full_fixture(self):
        self.put(LIBRARY,{"component_catalog_map":{"motor_a":{}}})
        d=self.get(DESCRIPTION);d["actuators_topology_map"]["motor_instance_a"]={
            "drives_joint_ref_str":"joint_a","component_model_ref_str":"motor_a"}
        self.put(DESCRIPTION,d)
        self.put(TOPOLOGY,{"control_profiles_map":{"profile_a":{}},
            "joint_actuator_mapping_map":{"actuator_a":{"target_joint_ref_str":"joint_a",
                "component_model_ref_str":"motor_a","use_profile_ref_str":"profile_a"}}})
        self.put(CALIBRATION,{"meta_group":{"target_description_ref_str":DESCRIPTION,
                  "target_description_hash_str":"sha256:"+"a"*64},
              "kinematic_offsets_map":{"joint_a":{}},"sensor_extrinsics_delta_map":{"sensor_a":{}},
              "sensor_intrinsics_map":{"sensor_a":{}},"dynamics_correction_map":{"joint_a":{},"global_body":{}}})
        self.put(FIDELITY,{"meta_group":{"related_files_map":{"description_ref_str":DESCRIPTION,
                 "calibration_ref_str":CALIBRATION,"hal_mapping_ref_str":HAL,
                 "runtime_validation_ref_str":RUNTIME}},"sensor_error_profiles_map":{"sensor_a":{}}})
        self.put(HAL,{"actuator_drivers_map":{"act":{"logical_actuator_ref_str":"motor_instance_a",
                    "qos_profile_ref_str":"qos_a"}},"sensor_drivers_map":{"sens":{"logical_sensor_ref_str":"sensor_a",
                    "qos_profile_ref_str":"qos_a"}},"qos_profiles_map":{"qos_a":{}}})
        self.put(RUNTIME,{"pre_flight_checks_list":[{"check_id_str":"calibration_validity",
                   "severity_enum":"MAJOR","sources_ref_map":{"calibration_str":CALIBRATION,"description_str":DESCRIPTION},
                   "on_failure_policy":{"block_motion_bool":True}}],
                  "severity_policies_map":{"MAJOR":{"allow_motion_bool":False}}})
        self.set_kernel_modules([DESCRIPTION,LIBRARY,TOPOLOGY,CALIBRATION,FIDELITY,HAL,RUNTIME])
    def test_status_candidate(self):
        s=json.loads((ROOT/"STATUS.json").read_bytes())
        self.assertEqual(s["maturity"],"candidate")
        for k in ("normative","accepted","stable_release_allowed","runtime_implemented"):
            self.assertIs(s[k],False)
    def test_bhl_actual_reference_characterization(self):
        r=assess_conformance(REPO,BHL)
        validator(DOCS[1],"ConformanceReport").validate(r)
        a=r["source_assessment"]
        self.assertEqual(a["computed_source_tree_sha256"],ROOT_HASH)
        self.assertEqual(a["integrity_status"],"MATCH")
        self.assertEqual(a["indexed_jsonc_syntax_status"],"PASS")
        self.assertEqual(r["inventory_status"],"PASS")
        self.assertEqual(len(r["components"]),76)
        self.assertEqual(sum(x["applicability"]=="REQUIRED" for x in r["components"]),35)
        self.assertEqual(sum(x["applicability"]=="OPTIONAL" for x in r["components"]),41)
        self.assertEqual(r["fragment_schema_status"],"PASS")
        self.assertEqual(r["reference_status"],"FAIL")
        self.ref(r,"ACTUATION_TARGET_JOINT","SYMBOL_MISSING","leg_right_knee_pitch")
        self.ref(r,"FIDELITY_SENSOR","SYMBOL_MISSING","right_wrist_ft")
        self.ref(r,"FIDELITY_RELATED_FILE","WRONG_TARGET","01_foundation/runtime_validation.jsonc")
        self.assertEqual({x["code"] for x in r["findings"]},
                         {"LEGACY_DESCRIPTION_DIGEST_PLACEHOLDER","DECLARED_MOTION_POLICY_CONFLICT"})
        self.assertFalse(passes_scoped_checks(r))
        print("BHL_REVIEW_SUMMARY",json.dumps({
            "components":len(r["components"]),
            "fragment_pass":sum(x["fragment_status"]=="PASS" for x in r["components"]),
            "not_covered":sum(x["fragment_status"]=="NOT_COVERED" for x in r["components"]),
            "references":len(r["references"]),
            "resolved":sum(x["status"]=="RESOLVED" for x in r["references"]),
            "unresolved":[x for x in r["references"] if x["status"]!="RESOLVED"],
            "findings":r["findings"]},sort_keys=True))
    def test_minimal_scope_optional_absent_and_exclusion_absent(self):
        r=self.report()
        self.assertTrue(passes_scoped_checks(r))
        self.assertEqual(self.row(r,CALIBRATION)["inventory_status"],"OPTIONAL_ABSENT")
        self.assertEqual(self.row(r,EXCLUDED)["inventory_status"],"NOT_APPLICABLE_ABSENT")
        self.assertEqual(self.row(r,MASTER)["fragment_status"],"NOT_COVERED")
    def test_full_synthetic_reference_families_pass(self):
        self.full_fixture();r=self.report()
        self.assertTrue(passes_scoped_checks(r))
        self.assertEqual(sum(x["fragment_status"]=="PASS" for x in r["components"]),9)
        for rule in ("ACTUATION_TARGET_JOINT","CALIBRATION_DYNAMICS_JOINT","FIDELITY_SENSOR",
                     "HAL_ACTUATOR","HAL_SENSOR","HAL_QOS_PROFILE","RUNTIME_SEVERITY"):
            self.ref(r,rule,"RESOLVED")
        self.assertFalse(any(x["target_symbol"]=="global_body" for x in r["references"]))
    def test_required_absent_matching_hash(self):
        self.set_app(CALIBRATION,"REQUIRED")
        r=self.report()
        self.assertEqual(r["source_assessment"]["integrity_status"],"MATCH")
        self.assertEqual(self.row(r,CALIBRATION)["inventory_status"],"REQUIRED_MISSING")
        self.assertEqual(r["inventory_status"],"FAIL")
    def test_optional_absent_but_referenced_fails(self):
        self.set_kernel_modules([DESCRIPTION,CALIBRATION])
        r=self.report()
        self.assertEqual(r["inventory_status"],"PASS")
        self.ref(r,"KERNEL_MODULE","TARGET_MISSING",CALIBRATION)
        self.assertFalse(passes_scoped_checks(r))
    def test_not_applicable_present_is_conflict(self):
        self.put(EXCLUDED,{})
        r=self.report()
        self.assertEqual(self.row(r,EXCLUDED)["inventory_status"],"NOT_APPLICABLE_PRESENT")
        self.assertEqual(self.row(r,EXCLUDED)["fragment_status"],"NOT_ASSESSED")
        self.assertEqual(r["inventory_status"],"FAIL")
    def test_reference_to_excluded_component_fails_even_absent(self):
        self.set_kernel_modules([DESCRIPTION,EXCLUDED])
        self.ref(self.report(),"KERNEL_MODULE","TARGET_NOT_APPLICABLE",EXCLUDED)
        self.put(EXCLUDED,{})
        self.ref(self.report(),"KERNEL_MODULE","TARGET_NOT_APPLICABLE",EXCLUDED)
    def test_unclassified_indexed_file_not_optional(self):
        self.put(EXTRA,{})
        self.set_kernel_modules([DESCRIPTION,EXTRA])
        r=self.report()
        self.assertEqual(self.row(r,EXTRA)["inventory_status"],"UNCLASSIFIED_PRESENT")
        self.ref(r,"KERNEL_MODULE","TARGET_UNCLASSIFIED",EXTRA)
    def test_optional_present_malformed_fragment_checked(self):
        self.put(TOPOLOGY,{"control_profiles_map":[],"joint_actuator_mapping_map":{}})
        r=self.report()
        self.assertEqual(self.row(r,TOPOLOGY)["fragment_status"],"FAIL")
        self.assertEqual(r["fragment_schema_status"],"FAIL")
        self.assertEqual(r["reference_status"],"BLOCKED")
    def test_structural_target_invalid_blocks_reference(self):
        self.put(DESCRIPTION,{"joint_topology_map":[]})
        r=self.report()
        self.ref(r,"KERNEL_MODULE","TARGET_FRAGMENT_INVALID",DESCRIPTION)
        self.assertFalse(passes_scoped_checks(r))
    def test_malformed_noncovered_indexed_source_not_pass(self):
        self.p["components"].append({"path":EXTRA,"applicability":"OPTIONAL","rationale":"test"})
        p=self.spec/EXTRA;p.write_bytes(b'{"x":1,"x":2}')
        r=self.report()
        self.assertEqual(self.row(r,EXTRA)["fragment_status"],"FAIL")
        self.assertEqual(r["source_assessment"]["indexed_jsonc_syntax_status"],"FAIL")
    def test_wrong_manifest_role_even_if_target_exists(self):
        m=self.get(MANIFEST);m["meta_group"]["kernel_ref_str"]=DESCRIPTION;self.put(MANIFEST,m)
        self.ref(self.report(),"MANIFEST_KERNEL","WRONG_TARGET",DESCRIPTION)
    def test_generated_or_mirror_not_source_target(self):
        self.put("openrgd_unified_spec.jsonc",{})
        self.p["components"].append({"path":"openrgd_unified_spec.jsonc","applicability":"OPTIONAL","rationale":"test"})
        self.set_kernel_modules([DESCRIPTION,"openrgd_unified_spec.jsonc"])
        r=self.report()
        self.ref(r,"KERNEL_MODULE","TARGET_MISSING","openrgd_unified_spec.jsonc")
        self.set_kernel_modules(["rgd_schema.json"])
        self.assertEqual(self.row(self.report(),KERNEL)["fragment_status"],"FAIL")
    def test_kernel_duplicates_and_self_reference(self):
        self.set_kernel_modules([DESCRIPTION,DESCRIPTION,KERNEL,MASTER])
        r=self.report()
        self.ref(r,"KERNEL_MODULE","DUPLICATE_REFERENCE",DESCRIPTION)
        self.ref(r,"KERNEL_MODULE","WRONG_TARGET",KERNEL)
        self.ref(r,"KERNEL_MODULE","WRONG_TARGET",MASTER)
    def test_path_traversal_and_uri_not_resolved(self):
        for bad in ("../description.jsonc","https://example.invalid/x.jsonc","/tmp/x.jsonc","01_foundation\\description.jsonc"):
            self.set_kernel_modules([bad])
            with self.subTest(bad=bad):
                r=self.report()
                self.assertFalse(passes_scoped_checks(r))
                self.assertEqual(self.row(r,KERNEL)["fragment_status"],"FAIL")
    def test_exact_case_sensitive_joint_and_symbol_namespace(self):
        self.full_fixture()
        t=self.get(TOPOLOGY);row=t["joint_actuator_mapping_map"]["actuator_a"]
        row["target_joint_ref_str"]="Joint_a";row["component_model_ref_str"]="sensor_a"
        self.put(TOPOLOGY,t)
        r=self.report()
        self.ref(r,"ACTUATION_TARGET_JOINT","SYMBOL_MISSING","Joint_a")
        self.ref(r,"ACTUATION_COMPONENT_MODEL","SYMBOL_MISSING","sensor_a")
    def test_cal_sensor_and_hal_logical_refs_not_inferred(self):
        self.full_fixture()
        cal=self.get(CALIBRATION);cal["sensor_intrinsics_map"]={"unknown_camera":{}}
        self.put(CALIBRATION,cal)
        hal=self.get(HAL);hal["sensor_drivers_map"]["sens"]["logical_sensor_ref_str"]="joint_a";self.put(HAL,hal)
        r=self.report()
        self.ref(r,"CALIBRATION_INTRINSIC_SENSOR","SYMBOL_MISSING","unknown_camera")
        self.ref(r,"HAL_SENSOR","SYMBOL_MISSING","joint_a")
    def test_placeholder_and_policy_contradiction_separate_from_refs(self):
        self.full_fixture()
        cal=self.get(CALIBRATION);cal["meta_group"]["target_description_hash_str"]=EMPTY_DIGEST;self.put(CALIBRATION,cal)
        rt=self.get(RUNTIME);rt["pre_flight_checks_list"][0]["on_failure_policy"]["block_motion_bool"]=False
        self.put(RUNTIME,rt)
        r=self.report()
        self.assertEqual(r["reference_status"],"PASS")
        self.assertEqual(r["review_findings_status"],"FOUND")
        self.assertEqual({x["code"] for x in r["findings"]},
             {"LEGACY_DESCRIPTION_DIGEST_PLACEHOLDER","DECLARED_MOTION_POLICY_CONFLICT"})
        self.assertFalse(passes_scoped_checks(r))
    def test_no_reverse_inference_from_stricter_local_policy(self):
        self.full_fixture()
        rt=self.get(RUNTIME);rt["severity_policies_map"]["MAJOR"]["allow_motion_bool"]=True;self.put(RUNTIME,rt)
        self.assertTrue(passes_scoped_checks(self.report()))
    def test_stale_root_keeps_diagnostic_scope_but_no_success(self):
        p=self.spec/DESCRIPTION;p.write_bytes(p.read_bytes()+b"\n// stale\n")
        r=self.report(seal=False)
        self.assertEqual(r["source_assessment"]["integrity_status"],"MISMATCH")
        self.assertEqual(r["reference_status"],"PASS")
        self.assertFalse(passes_scoped_checks(r))
    def test_profile_version_mismatch_not_assessed(self):
        m=self.get(MANIFEST);m["meta_group"]["rgd_standard_version_semver_str"]="0.3.0";self.put(MANIFEST,m)
        r=self.report()
        self.assertEqual(r["evaluation_status"],"PROFILE_VERSION_MISMATCH")
        self.assertEqual(r["reference_status"],"NOT_ASSESSED")
    def test_invalid_profiles_rejected_no_auto_policy(self):
        for change in ("duplicate","casefold","manifest_optional","empty_rationale","unknown_rules","unsupported_version"):
            p=deepcopy(self.p)
            if change=="duplicate":p["components"].append({**p["components"][0],"applicability":"OPTIONAL"})
            if change=="casefold":p["components"].append({**p["components"][0],"path":"MANIFEST.jsonc"})
            if change=="manifest_optional":p["components"][0]["applicability"]="OPTIONAL"
            if change=="empty_rationale":p["components"][0]["rationale"]=" "
            if change=="unknown_rules":p["rule_profile"]="UNSUPPORTED"
            if change=="unsupported_version":p["standard_version"]="0.3.0"
            with self.subTest(change=change),self.assertRaises(ConformanceError):parse_profile(encoded(p))
        with self.assertRaises(ConformanceError):parse_profile(b'{"x":1,"x":2}')
    def test_profile_digest_projection_and_report_link(self):
        raw=encoded(self.p);r=assess_conformance(self.bundle,raw)
        p,policy=parse_profile(raw)
        self.assertEqual(r["profile_sha256"],source.sha(raw))
        self.assertEqual(r["source_assessment_sha256"],source.sha(encoded(r["source_assessment"])))
        self.assertEqual(r["source_assessment"]["requirements_profile"]["profile_sha256"],source.sha(projection(p,policy)))
        self.assertNotEqual(r["profile_sha256"],r["source_assessment"]["requirements_profile"]["profile_sha256"])
    def test_source_snapshot_mutation_between_checks_is_rejected(self):
        actual=source.assess_source
        def changed(bundle,profile):
            r=actual(bundle,profile)
            p=Path(bundle)/DESCRIPTION;p.write_bytes(p.read_bytes()+b" ")
            return r
        with patch("source_conformance.source.assess_source",side_effect=changed):
            r=self.report()
        self.assertEqual(r["evaluation_status"],"SNAPSHOT_BINDING_FAILED")
        self.assertEqual(r["reference_status"],"NOT_ASSESSED")
    def test_source_unchanged_deterministic_and_symlink_denied(self):
        before={p.relative_to(self.bundle):p.read_bytes() for p in self.bundle.rglob("*") if p.is_file()}
        first=self.report(seal=False);second=self.report(seal=False)
        self.assertEqual(first,second)
        self.assertEqual(before,{p.relative_to(self.bundle):p.read_bytes() for p in self.bundle.rglob("*") if p.is_file()})
        (self.spec/"link.jsonc").symlink_to(self.spec/MANIFEST)
        r=self.report(seal=False)
        self.assertEqual(r["evaluation_status"],"SOURCE_UNAVAILABLE")
        self.assertEqual(r["reference_status"],"NOT_ASSESSED")
    def test_reference_budget_not_silent_success(self):
        with patch("source_conformance.MAX_REFERENCES",1):r=self.report()
        self.assertEqual(r["reference_status"],"FAIL")
        self.assertIn({"code":"REFERENCE_CHECK_LIMIT","path":None,"pointer":None},r["findings"])
    def test_cli_pass_and_failure_are_scoped_json(self):
        p=Path(self.temp.name)/"policy.json";p.write_bytes(encoded(self.p))
        args=[sys.executable,str(ROOT/"source_conformance.py"),"--bundle",str(self.bundle),"--profile",str(p)]
        first=subprocess.run(args,capture_output=True,timeout=20)
        self.assertEqual(first.returncode,0,first.stderr.decode())
        self.assertTrue(passes_scoped_checks(json.loads(first.stdout)))
        self.set_kernel_modules([DESCRIPTION,CALIBRATION]);self.seal()
        second=subprocess.run(args,capture_output=True,timeout=20)
        self.assertEqual(second.returncode,2,second.stderr.decode())
        self.assertEqual(json.loads(second.stdout)["reference_status"],"FAIL")

if __name__=="__main__":
    unittest.main(verbosity=2)
