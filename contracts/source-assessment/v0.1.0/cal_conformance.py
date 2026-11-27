"""Actual CAL-021-B sidecar and Rust binary against identical stable fixtures.

This tests independent private copies of unchanged inputs, not live snapshot
sharing or production CAL integration. All new outputs remain candidate.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from assessment import ROOT, assess_source
from openrgd.core import canonical

CORE=Path(os.environ["CAL_TEST_CORE"]).resolve()
CAL=Path(os.environ["CAL_CHECKOUT"]).resolve()
BIN=Path(os.environ["CAL_TEST_BINARY"]).resolve()
BHL=(ROOT/"fixtures/bhl-genesis-required-paths.json").read_bytes()
CAL_SCHEMA=json.loads((CAL/"contracts/canonical-identity.v0.1-candidate.schema.json").read_bytes())
CAL_VALIDATOR=Draft202012Validator(CAL_SCHEMA)

class CALInterop(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle=Path(self.tmp.name)/"fixture";self.bundle.mkdir()
        self.spec=self.bundle/"spec";shutil.copytree(CORE/"spec",self.spec)
    def compare(self,expected_core,expected_cal,cal_exit):
        before={p.relative_to(self.spec):p.read_bytes() for p in self.spec.rglob("*") if p.is_file()}
        core=assess_source(self.bundle,BHL)
        run=subprocess.run([sys.executable,"-I","-B",str(CAL/"tools/canonical_identity/verify.py"),
                            "--bundle",str(self.bundle),"--core-checkout",str(CORE),"--cal-binary",str(BIN)],
                           capture_output=True,timeout=90)
        self.assertEqual(run.returncode,cal_exit,run.stderr.decode())
        cal=json.loads(run.stdout);CAL_VALIDATOR.validate(cal)
        self.assertEqual(core["integrity_status"],expected_core)
        self.assertEqual(cal["integrity_status"],expected_cal)
        self.assertEqual(core["computed_source_tree_sha256"],cal["computed_source_tree_sha256"])
        self.assertEqual(core["declared_source_tree_sha256"],cal["declared_source_tree_sha256"])
        self.assertEqual(len(core["source_index"]["files"]),cal["indexed_file_count"])
        self.assertEqual(cal["report_binding_status"],"source_index_match")
        entries={x["path"]:x["raw_sha256"] for x in core["raw_file_commitments"]}
        for source in cal["calibration_report"]["source_digests"]:
            self.assertEqual(entries[source["path"].removeprefix("spec/")],source["raw_file_sha256"])
        for k in ("canonical_schema_validated","robot_binding_verified","profile_model_hash_bound","physical_calibration_certified","actuation_enabled"):
            self.assertIs(cal[k],False);self.assertIs(core[k],False)
        self.assertEqual(cal["bundle_completeness"],"not_assessed")
        self.assertEqual(before,{p.relative_to(self.spec):p.read_bytes() for p in self.spec.rglob("*") if p.is_file()})
        return core
    def test_full_reference_actual_cal_binding(self):
        r=self.compare("MATCH","source_tree_hash_match",0)
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
    def test_stale_root_actual_cal_index_binding(self):
        p=self.spec/"00_core/kernel.jsonc"
        p.write_bytes(p.read_bytes()+b"\n// test-only change outside CAL inputs\n")
        r=self.compare("MISMATCH","source_tree_hash_mismatch",2)
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_PRESENT")
    def test_self_consistent_partial_not_complete(self):
        for p in list(self.spec.rglob("*")):
            if p.is_file() and p.relative_to(self.spec).as_posix() not in ("manifest.jsonc","01_foundation/description.jsonc"):
                p.unlink()
        canonical.update_manifest_integrity(self.spec)
        r=self.compare("MATCH","source_tree_hash_match",0)
        self.assertEqual(r["required_paths_status"],"REQUIRED_PATHS_MISSING")

if __name__=="__main__":
    unittest.main(verbosity=2)
