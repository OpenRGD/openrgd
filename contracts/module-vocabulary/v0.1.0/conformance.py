"""EXT-01A vocabulary/legacy compatibility tests only, never authority or installer."""
from __future__ import annotations
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from rgd_registry import core as legacy

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "schemas/module-vocabulary.schema.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
DEFS = SCHEMA["$defs"]
REGISTRY = Path(os.environ["REGISTRY_CHECKOUT"])
CAL = Path(os.environ["CAL_CHECKOUT"])

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def validator(name):
    return Draft202012Validator({"$schema": SCHEMA["$schema"], "$defs": DEFS,
                                 "$ref": "#/$defs/" + name})

def values(name):
    return [item["const"] for item in DEFS[name]["oneOf"]]

class TaxonomyTests(unittest.TestCase):
    def test_status_is_candidate(self):
        s = read(ROOT / "STATUS.json")
        self.assertEqual(s["maturity"], "candidate")
        for key in ("accepted","normative","stable_release_allowed","runtime_implemented"):
            self.assertIs(s[key], False)

    def test_each_term_has_unique_name_and_definition(self):
        for name, definition in DEFS.items():
            if "oneOf" not in definition:
                continue
            terms = definition["oneOf"]
            self.assertEqual(len(terms),len({t["const"] for t in terms}))
            for term in terms:
                with self.subTest(name=name,term=term["const"]):
                    self.assertTrue(term["description"].strip())
                    validator(name).validate(term["const"])

    def test_id_profile(self):
        v=validator("ModuleId")
        for value in ("org.openrgd.calibration","com.example.robotics.camera","org.example.multi-axis"):
            with self.subTest(value=value):v.validate(value)
        for value in ("openrgd","org.openrgd","org.openrgd..camera","Org.openrgd.camera",
                      "org.openrgd.camera-","org.openrgd.-camera","org.openrgd.cam_era",
                      "org.openrgd.cam/era","org.openrgd.camera\n","org.openrgd.càmera",
                      "org.openrgd.camera@1.0.0","org.openrgd."+"a"*201):
            with self.subTest(value=value):self.assertFalse(v.is_valid(value))

    def test_release_version_profile(self):
        v=validator("ReleaseVersion")
        for value in ("0.2.0","1.0.0","1.2.3-alpha.1","0.1.0-dev.0","1.0.0-0",
                      "1.0.0-01a"):
            with self.subTest(value=value):v.validate(value)
        for value in ("latest","main","v1.0.0","01.2.3","1.02.3","1.2.03","1.2",
                      "1.2.3+build","1.2.3-01","1.2.3-","1.2.3-alpha..1","0.1.0a5",
                      "1.2.3\n","1.2.3-α"):
            with self.subTest(value=value):self.assertFalse(v.is_valid(value))

    def test_release_key_not_publication_or_grant(self):
        v=validator("ModuleReleaseKey")
        k={"module_id":"org.example.test","module_version":"1.0.0"}
        v.validate(k)
        for field in ("approved","trusted","grants_authority","robot_id","life_id","artifact_digest"):
            with self.subTest(field=field):self.assertFalse(v.is_valid({**k,field:True}))

    def test_functional_roles_are_facets(self):
        v=validator("ModuleClassification")
        record={"functional_roles":["acquisition","observability"]}
        v.validate(record)
        for other in ([],["acquisition","acquisition"],["rust"],["container"],["authorized"],["unknown"]):
            with self.subTest(other=other):self.assertFalse(v.is_valid({"functional_roles":other}))
        self.assertFalse(v.is_valid({**record,"permissions_granted":True}))

    def test_execution_cross_product(self):
        # Expected compatibility table is independent from schema if/then clauses.
        allowed={"native_binary":{"on_demand","supervised_service"},
                 "native_library":{"host_loaded"},
                 "interpreted_module":{"on_demand","supervised_service","host_loaded"},
                 "device_firmware":{"device_managed"},"none":{"data_only"}}
        v=validator("ExecutionClassification")
        for form in values("ExecutionForm"):
            for mode in values("ActivationMode"):
                with self.subTest(form=form,mode=mode):
                    self.assertEqual(v.is_valid({"execution_form":form,"activation_mode":mode}),
                                     mode in allowed[form])
        self.assertFalse(v.is_valid({"execution_form":"oci_image","activation_mode":"supervised_service"}))
        self.assertFalse(v.is_valid({"execution_form":"native_binary","activation_mode":"on_demand","auto_start":True}))

    def test_artifact_and_execution_are_independent(self):
        validator("ArtifactKind").validate("python_wheel")
        validator("ArtifactKind").validate("oci_image")
        self.assertFalse(validator("ExecutionForm").is_valid("python_wheel"))
        self.assertFalse(validator("ArtifactKind").is_valid("supervised_service"))

    def test_maturity_publication_channel_separate(self):
        validator("ContractMaturity").validate("candidate")
        validator("PublicationState").validate("published")
        validator("ReleaseChannel").validate("preview")
        self.assertFalse(validator("ContractMaturity").is_valid("published"))
        self.assertFalse(validator("PublicationState").is_valid("accepted"))
        self.assertFalse(validator("ContractMaturity").is_valid("stable"))

    def test_host_state_dimensions_separate(self):
        validator("InstallationState").validate("present")
        validator("IntegrityState").validate("verified_local")
        validator("ActivationState").validate("disabled")
        validator("ExecutionState").validate("stopped")
        validator("HealthState").validate("unknown")
        for name in ("CompatibilityState","InstallationState","IntegrityState","ActivationState",
                     "ExecutionState","HealthState"):
            with self.subTest(name=name):
                self.assertFalse(validator(name).is_valid("authorized"))
                self.assertFalse(validator(name).is_valid("calibrated"))
        self.assertFalse(validator("HealthState").is_valid("running"))
        self.assertFalse(validator("ActivationState").is_valid("healthy"))

class LegacyTests(unittest.TestCase):
    def test_actual_pinned_legacy_catalog_and_manifest(self):
        # Catalog metadata discovery only. No installation, hardware or code loading.
        with patch.object(legacy,"REGISTRY_ROOT",REGISTRY/"registry"):
            items=legacy.catalog()
        self.assertEqual(len(items),1)
        d=items[0]
        schema=read(REGISTRY/"registry/schemas/module.v0.1.schema.json")
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(d)
        p=read(CAL/"module.openrgd.json")
        self.assertEqual(d["id"],p["module_id"])
        self.assertEqual(d["version"],p["module_version"])
        self.assertEqual(d["source"]["commit_sha"],"81700401e2fa6d370a86b6c1f5a48802bc5f1fc7")
        self.assertEqual(set(d["capabilities"]),set(p["capabilities"]))
        self.assertEqual(d["permissions_required"],[])
        self.assertTrue(d["safety"]["non_actuating"])
        self.assertFalse(d["safety"]["automatic_motion_on_load"])
        self.assertEqual(d["distribution"]["kind"],"pinned_git_cargo")
        self.assertEqual(d["integration"]["read_only_command"],"inspect")
        self.assertEqual(p["runtime"],"rust-library")
        self.assertEqual(p["registry_status"],"proposal-only")
        validator("ModuleReleaseKey").validate({"module_id":d["id"],"module_version":d["version"]})
        validator("ModuleClassification").validate({"functional_roles":["calibration"]})
        validator("ExecutionClassification").validate({"execution_form":"native_binary","activation_mode":"on_demand"})
        # Existing closed schema has not been relaxed by the candidate.
        self.assertFalse(Draft202012Validator(schema).is_valid({**d,"functional_roles":["calibration"]}))

if __name__ == "__main__":
    unittest.main(verbosity=2)
