"""Scoped review tests on actual reference and non-BHL synthetic model profiles."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from consistency import (ROOT,sc,source,LEGACY,RAW,VALIDATOR,declared_failure_policy,
                         review_consistency,group_references)
REPO=ROOT.parents[2]
BHL=(sc.ROOT/"fixtures/bhl-static-review-profile.json").read_bytes()
MIGRATION=json.loads((ROOT/"fixtures/bhl-reference-path-migration.json").read_bytes())
ROOT_HASH=MIGRATION["old_source_tree_sha256"]

def profile(required,optional,excluded,identifier="org.example.fixture-review"):
    return sc.encoded({"schema_version":"openrgd.source-conformance-profile.v0.1-candidate",
        "profile_id":identifier,"profile_version":"0.1.0","standard_version":"0.2.0",
        "rule_profile":sc.RULE_PROFILE,"inventory_policy":"EXPLICIT_CLASSIFICATION_REQUIRED",
        "components":[{"path":p,"applicability":app,"rationale":"Explicit synthetic scoped test fixture"}
                      for paths,app in ((required,"REQUIRED"),(optional,"OPTIONAL"),(excluded,"NOT_APPLICABLE"))
                      for p in paths]})

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle=Path(self.tmp.name)/"fixture";self.bundle.mkdir()
        self.spec=self.bundle/"spec";self.spec.mkdir()

    def put(self,path,obj):
        p=self.spec/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sc.encoded(obj))
    def get(self,path):
        return json.loads((self.spec/path).read_bytes())
    def seal(self):
        source.canonical.update_manifest_integrity(self.spec)
    def core(self,modules,identity):
        self.put(sc.MANIFEST,{"meta_group":{"integrity_hash_str":"sha256:"+"0"*64,
                "integrity_profile_str":source.PROFILE,"rgd_standard_version_semver_str":"0.2.0",
                "kernel_ref_str":sc.KERNEL,"rgd_schema_ref_str":sc.MASTER}})
        self.put(sc.KERNEL,{"meta_group":{"id":identity},"module_loading_order_list":modules})
        self.put(sc.MASTER,{"description":"synthetic test-only meta-schema"})
    def hardware(self,kind="manipulator",calibration=False):
        # Different identifiers and topologies; no claim of actual geometry,
        # dynamics, coupling, calibration measurements or safety certification.
        joints=("azimuth","extension") if kind=="manipulator" else ("drive_port","drive_starboard")
        motors=("rotary_drive","linear_drive") if kind=="manipulator" else ("wheel_drive","wheel_drive")
        self.core([sc.DESCRIPTION,sc.LIBRARY,sc.TOPOLOGY,sc.RUNTIME]+([sc.CALIBRATION] if calibration else []),
                  "synthetic-"+kind)
        self.put(sc.DESCRIPTION,{"joint_topology_map":{j:{"type_enum":
                    "PRISMATIC" if j=="extension" else "REVOLUTE"} for j in joints},
                "sensors_mounting_map":{},
                "actuators_topology_map":{"unit_"+str(i):{"drives_joint_ref_str":j,"component_model_ref_str":m}
                    for i,(j,m) in enumerate(zip(joints,motors))}})
        self.put(sc.LIBRARY,{"component_catalog_map":{m:{} for m in motors}})
        self.put(sc.TOPOLOGY,{"control_profiles_map":{"closed_loop":{}},
             "joint_actuator_mapping_map":{"mapping_"+str(i):{"target_joint_ref_str":j,
                 "component_model_ref_str":m,"use_profile_ref_str":"closed_loop"}
                 for i,(j,m) in enumerate(zip(joints,motors))}})
        self.runtime()
        if calibration:
            self.put(sc.CALIBRATION,{"meta_group":{"target_description_ref_str":sc.DESCRIPTION,
                "target_description_hash_str":source.sha((self.spec/sc.DESCRIPTION).read_bytes())},
                "kinematic_offsets_map":{},"sensor_extrinsics_delta_map":{},
                "sensor_intrinsics_map":{},"dynamics_correction_map":{}})
        self.policy=profile([sc.MANIFEST,sc.KERNEL,sc.MASTER,sc.DESCRIPTION,sc.LIBRARY,sc.TOPOLOGY,sc.RUNTIME],
                       [sc.CALIBRATION,sc.HAL,sc.FIDELITY],[],"org.example."+kind+"-review")
        self.seal()
    def runtime(self,allow=False,block=True):
        self.put(sc.RUNTIME,{"pre_flight_checks_list":[{"check_id_str":"fixture_preflight",
            "severity_enum":"CUSTOM_SEVERITY","sources_ref_map":{"description_str":sc.DESCRIPTION},
            "on_failure_policy":{"block_motion_bool":block}}],
            "severity_policies_map":{"CUSTOM_SEVERITY":{"allow_motion_bool":allow}}})
    def virtual(self):
        world="03_agency/world_model.jsonc"
        self.core([world],"synthetic-virtual")
        self.put(world,{"description":"no physical modules in selected profile"})
        self.policy=profile([sc.MANIFEST,sc.KERNEL,sc.MASTER,world],[],
             [sc.DESCRIPTION,sc.LIBRARY,sc.TOPOLOGY,sc.CALIBRATION,sc.HAL,sc.FIDELITY,sc.RUNTIME],
             "org.example.virtual-review")
        self.seal()
    def report(self,digest_profile=LEGACY,bundle=None,policy=None):
        r=review_consistency(bundle or self.bundle,policy or self.policy,digest_profile)
        VALIDATOR.validate(r)
        for k in ("canonical_schema_validated","semantic_consistency_validated","runtime_evaluated",
                  "physical_binding_verified","profile_model_hash_bound","physical_calibration_certified",
                  "publication_committed","actuation_enabled","grants_authority"):
            self.assertIs(r[k],False)
        self.assertEqual(r["source_conformance_sha256"],source.sha(sc.encoded(r["source_conformance"])))
        return r
    def test_status_candidate(self):
        obj=json.loads((ROOT/"STATUS.json").read_bytes())
        self.assertEqual(obj["maturity"],"candidate")
        for k in ("normative","accepted","stable_release_allowed","runtime_implemented"):
            self.assertIs(obj[k],False)
    def test_generic_failure_policy_truth_table(self):
        cases=[
            (False,False,"GLOBAL_BLOCK_LOCAL_NONBLOCK_CONFLICT","BLOCK_REQUIRED"),
            (False,True,"POLICY_CONSISTENT","BLOCK_REQUIRED"),
            (True,True,"LOCAL_STRICTER_THAN_GLOBAL","BLOCK_REQUIRED"),
            (True,False,"POLICY_CONSISTENT","NO_BLOCK_FROM_THIS_RULE"),
            (None,False,"POLICY_UNRESOLVED","INDETERMINATE"),
            (False,None,"POLICY_UNRESOLVED","INDETERMINATE"),
            (1,False,"POLICY_UNRESOLVED","INDETERMINATE"),
            (True,0,"POLICY_UNRESOLVED","INDETERMINATE")]
        for a,b,s,c in cases:
            with self.subTest(a=a,b=b):self.assertEqual(declared_failure_policy(a,b),(s,c))
    def test_actual_bhl_preserves_all_29_and_two_prior_findings(self):
        r=self.report(bundle=REPO,policy=BHL)
        a=r["source_conformance"]
        self.assertEqual(a["source_assessment"]["computed_source_tree_sha256"],ROOT_HASH)
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
        self.assertEqual(len(a["references"]),162)
        self.assertEqual(sum(g["occurrences"] for g in r["reference_groups"]),29)
        self.assertEqual(len(r["reference_groups"]),22)
        missing=next(g for g in r["reference_groups"] if g["target_symbol"]=="tmotor_ak60_6_v1")
        self.assertEqual(missing["disposition"],"CATALOG_EVIDENCE_REQUIRED")
        self.assertEqual(missing["occurrences"],8)
        self.assertEqual(len(missing["source_locations"]),8)
        self.assertEqual({x["code"] for x in a["findings"]},
               {"LEGACY_DESCRIPTION_DIGEST_PLACEHOLDER","DECLARED_MOTION_POLICY_CONFLICT"})
        row=next(x for x in r["runtime_policy_rows"] if x["check_id"]=="calibration_validity")
        self.assertEqual(row["declared_failure_constraint"],"BLOCK_REQUIRED")
        self.assertEqual(row["review_status"],"GLOBAL_BLOCK_LOCAL_NONBLOCK_CONFLICT")
        self.assertEqual(r["description_commitment"]["status"],"PLACEHOLDER")
        print("REFERENCE_REVIEW",json.dumps({"root":ROOT_HASH,"occurrences":29,"groups":22,
            "findings":a["findings"],"policy":row,"digest":r["description_commitment"]},sort_keys=True))
    def test_private_reference_path_migration_reduces_only_one_occurrence(self):
        shutil.rmtree(self.spec);shutil.copytree(REPO/"spec",self.spec)
        original=source.canonical.compute_integrity(self.spec)
        self.assertTrue(original.matches);self.assertEqual(original.computed,ROOT_HASH)
        path=self.spec/MIGRATION["source_path"];before=path.read_bytes()
        self.assertEqual(source.git_blob(before),MIGRATION["source_git_blob"])
        _,_,obj=source.parse_conservative(before)
        self.assertEqual(obj["meta_group"]["related_files_map"]["runtime_validation_ref_str"],MIGRATION["old_value"])
        old=('"runtime_validation_ref_str": "'+MIGRATION["old_value"]+'"').encode()
        new=('"runtime_validation_ref_str": "'+MIGRATION["new_value"]+'"').encode()
        self.assertEqual(before.count(old),1)
        original_files={p.relative_to(self.spec).as_posix():p.read_bytes()
                        for p in self.spec.rglob("*") if p.is_file()}
        path.write_bytes(before.replace(old,new,1))
        changed=source.canonical.update_manifest_integrity(self.spec)
        self.assertTrue(changed.matches);self.assertNotEqual(changed.computed,ROOT_HASH)
        current={p.relative_to(self.spec).as_posix():p.read_bytes()
                 for p in self.spec.rglob("*") if p.is_file()}
        self.assertEqual({k for k in current if current[k]!=original_files[k]},
                         {sc.MANIFEST,MIGRATION["source_path"]})
        self.assertEqual(current[MIGRATION["source_path"]],before.replace(old,new,1))
        r=self.report(policy=BHL)
        self.assertEqual(sum(g["occurrences"] for g in r["reference_groups"]),28)
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
        self.assertEqual(r["description_commitment"]["status"],"PLACEHOLDER")
        self.assertEqual(len(r["source_conformance"]["findings"]),2)
        self.assertEqual(source.canonical.compute_integrity(REPO/"spec").computed,ROOT_HASH)
        print("PRIVATE_PATH_MIGRATION",json.dumps({"before":ROOT_HASH,"after":changed.computed,
                "unresolved_before":29,"unresolved_after":28,"published":False},sort_keys=True))
    def test_manipulator_without_sensors_or_bhl_ids(self):
        self.hardware("manipulator")
        r=self.report()
        self.assertEqual(r["review_status"],"SCOPED_CLEAR")
        self.assertEqual(r["description_commitment"]["status"],"ABSENT_OPTIONAL")
        self.assertEqual(r["runtime_policy_rows"][0]["check_id"],"fixture_preflight")
    def test_differential_drive_with_reused_component_model(self):
        self.hardware("differential-drive")
        r=self.report()
        self.assertEqual(r["review_status"],"SCOPED_CLEAR")
        models=[x for x in r["source_conformance"]["references"] if x["rule_id"]=="ACTUATION_COMPONENT_MODEL"]
        self.assertEqual(len(models),2)
        self.assertTrue(all(x["target_symbol"]=="wheel_drive" and x["status"]=="RESOLVED" for x in models))
    def test_virtual_profile_explicitly_excludes_physical_modules(self):
        self.virtual();r=self.report()
        self.assertEqual(r["review_status"],"SCOPED_CLEAR")
        self.assertEqual(r["runtime_policy_status"],"NOT_APPLICABLE")
        self.assertEqual(r["description_commitment"]["status"],"NOT_APPLICABLE")
        self.assertEqual(r["runtime_policy_rows"],[])
    def test_excluded_physical_component_present_not_waiver(self):
        self.virtual();self.runtime();self.seal()
        r=self.report()
        self.assertEqual(r["runtime_policy_scope"],"NOT_APPLICABLE_PRESENT")
        self.assertEqual(r["runtime_policy_status"],"BLOCKED")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_missing_classification_is_not_not_applicable(self):
        self.virtual()
        p=json.loads(self.policy);p["components"]=[x for x in p["components"] if x["path"]!=sc.RUNTIME]
        r=self.report(policy=sc.encoded(p))
        self.assertEqual(r["runtime_policy_scope"],"OUT_OF_SCOPE")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_unresolved_identity_is_not_guessed(self):
        self.hardware()
        t=self.get(sc.TOPOLOGY);t["joint_actuator_mapping_map"]["mapping_0"]["target_joint_ref_str"]="Azimuth"
        self.put(sc.TOPOLOGY,t);self.seal();r=self.report()
        g=next(x for x in r["reference_groups"] if x["rule_id"]=="ACTUATION_TARGET_JOINT")
        self.assertEqual(g["disposition"],"IDENTITY_REVIEW")
        self.assertEqual(g["target_symbol"],"Azimuth")
        self.assertEqual(g["occurrences"],1)
    def test_legacy_digest_matching_bytes_still_unqualified(self):
        self.hardware(calibration=True)
        r=self.report()
        c=r["description_commitment"]
        self.assertEqual(c["declared_sha256"],c["observed_raw_description_sha256"])
        self.assertEqual(c["status"],"UNQUALIFIED")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_explicit_raw_description_match_no_physical_binding(self):
        self.hardware(calibration=True)
        r=self.report(RAW)
        self.assertEqual(r["description_commitment"]["status"],"MATCH")
        self.assertEqual(r["review_status"],"SCOPED_CLEAR")
        self.assertFalse(r["description_commitment"]["profile_model_hash_bound"])
    def test_explicit_raw_digest_mismatch_after_nominal_revision(self):
        self.hardware(calibration=True)
        desc=self.spec/sc.DESCRIPTION;desc.write_bytes(desc.read_bytes()+b"\n// new nominal revision\n")
        self.seal()
        r=self.report(RAW)
        self.assertEqual(r["source_conformance"]["source_assessment"]["integrity_status"],"MATCH")
        self.assertEqual(r["description_commitment"]["status"],"MISMATCH")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_placeholder_never_becomes_verified(self):
        self.hardware(calibration=True)
        c=self.get(sc.CALIBRATION);c["meta_group"]["target_description_hash_str"]=sc.EMPTY_DIGEST
        self.put(sc.CALIBRATION,c);self.seal()
        for profile in (LEGACY,RAW):
            with self.subTest(profile=profile):self.assertEqual(self.report(profile)["description_commitment"]["status"],"PLACEHOLDER")
    def test_wrong_description_target_blocks_digest_comparison(self):
        self.hardware(calibration=True)
        c=self.get(sc.CALIBRATION);c["meta_group"]["target_description_ref_str"]=sc.LIBRARY
        self.put(sc.CALIBRATION,c);self.seal()
        self.assertEqual(self.report(RAW)["description_commitment"]["status"],"BLOCKED")
    def test_policy_conflict_no_permission(self):
        self.hardware();self.runtime(False,False);self.seal()
        r=self.report()
        self.assertEqual(r["runtime_policy_rows"][0]["declared_failure_constraint"],"BLOCK_REQUIRED")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_stricter_local_and_nonblocking_not_allow(self):
        self.hardware()
        for local,expected in ((True,"BLOCK_REQUIRED"),(False,"NO_BLOCK_FROM_THIS_RULE")):
            self.runtime(True,local);self.seal()
            r=self.report()
            self.assertEqual(r["runtime_policy_rows"][0]["declared_failure_constraint"],expected)
            self.assertFalse(r["runtime_policy_rows"][0]["grants_authority"])
    def test_unknown_severity_indeterminate(self):
        self.hardware()
        rt=self.get(sc.RUNTIME);rt["severity_policies_map"]={}
        self.put(sc.RUNTIME,rt);self.seal()
        r=self.report()
        self.assertEqual(r["runtime_policy_rows"][0]["declared_failure_constraint"],"INDETERMINATE")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_duplicate_check_ids_both_indeterminate(self):
        self.hardware()
        rt=self.get(sc.RUNTIME);rt["pre_flight_checks_list"].append(deepcopy(rt["pre_flight_checks_list"][0]))
        self.put(sc.RUNTIME,rt);self.seal()
        r=self.report()
        self.assertEqual([x["declared_failure_constraint"] for x in r["runtime_policy_rows"]],
                         ["INDETERMINATE","INDETERMINATE"])
    def test_malformed_and_empty_policy_not_clear(self):
        self.hardware()
        self.runtime(False,1);self.seal()
        self.assertEqual(self.report()["runtime_policy_status"],"BLOCKED")
        rt=self.get(sc.RUNTIME);rt["pre_flight_checks_list"]=[]
        self.put(sc.RUNTIME,rt);self.seal()
        self.assertEqual(self.report()["review_status"],"REVIEW_REQUIRED")
    def test_stale_root_diagnostic_never_clear(self):
        self.hardware()
        d=self.spec/sc.DESCRIPTION;d.write_bytes(d.read_bytes()+b"\n// stale\n")
        r=self.report()
        self.assertEqual(r["source_conformance"]["source_assessment"]["integrity_status"],"MISMATCH")
        self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
    def test_snapshot_byte_binding_rejects_interphase_change(self):
        self.hardware()
        actual=sc.assess_conformance
        def changed(bundle,policy):
            r=actual(bundle,policy)
            d=Path(bundle)/sc.DESCRIPTION;d.write_bytes(d.read_bytes()+b" ")
            return r
        with patch("consistency.sc.assess_conformance",side_effect=changed):
            r=self.report()
        self.assertEqual(r["evaluation_status"],"BLOCKED")
        self.assertFalse(r["snapshot_binding_verified"])
    def test_read_only_and_original_snapshot_failure_preserved(self):
        self.hardware()
        before={p.relative_to(self.bundle):p.read_bytes() for p in self.bundle.rglob("*") if p.is_file()}
        self.assertEqual(self.report(),self.report())
        self.assertEqual(before,{p.relative_to(self.bundle):p.read_bytes() for p in self.bundle.rglob("*") if p.is_file()})
        (self.spec/"link.jsonc").symlink_to(self.spec/sc.MANIFEST)
        r=self.report()
        self.assertEqual(r["evaluation_status"],"BLOCKED")
        self.assertEqual(r["source_conformance"]["source_assessment"]["input_status"],"SNAPSHOT_REJECTED")
    def test_unknown_digest_profile_rejected(self):
        self.hardware()
        with self.assertRaisesRegex(sc.ConformanceError,"UNSUPPORTED_DESCRIPTION_DIGEST_PROFILE"):
            self.report("unknown")
    def test_schema_rejects_inconsistent_policy_and_grants(self):
        self.hardware();r=self.report()
        bad=deepcopy(r);bad["runtime_policy_rows"][0]["declared_failure_constraint"]="NO_BLOCK_FROM_THIS_RULE"
        self.assertFalse(VALIDATOR.is_valid(bad))
        bad=deepcopy(r);bad["actuation_enabled"]=True
        self.assertFalse(VALIDATOR.is_valid(bad))
    def test_cli_review_required_and_scoped_clear(self):
        self.hardware(calibration=True)
        p=Path(self.tmp.name)/"policy.json";p.write_bytes(self.policy)
        cmd=[sys.executable,str(ROOT/"consistency.py"),"--bundle",str(self.bundle),"--profile",str(p)]
        first=subprocess.run(cmd,capture_output=True,timeout=20)
        self.assertEqual(first.returncode,2,first.stderr.decode())
        self.assertEqual(json.loads(first.stdout)["review_status"],"REVIEW_REQUIRED")
        second=subprocess.run(cmd+["--description-digest-profile",RAW],capture_output=True,timeout=20)
        self.assertEqual(second.returncode,0,second.stderr.decode())
        self.assertEqual(json.loads(second.stdout)["review_status"],"SCOPED_CLEAR")

if __name__=="__main__":
    unittest.main(verbosity=2)
