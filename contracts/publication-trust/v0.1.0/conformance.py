"""Artifact verification: actual built wheel, mutated archive controls, no imports."""
from copy import deepcopy
import base64
import csv
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

from proposal import parse, encode_proposal, digest
from wheel_inspection import inspect_wheel, review_target, InspectionError, read_archive, ROOT
from trust_fixture import build_fixture, proposal_for

def pack(files, record_path=None, recompute=False):
    files=dict(files)
    if recompute:
        lines=StringIO(newline="")
        writer=csv.writer(lines,lineterminator="\n")
        for name,data in sorted(files.items()):
            if name==record_path:
                continue
            h=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
            writer.writerow([name,"sha256="+h,str(len(data))])
        writer.writerow([record_path,"",""])
        files[record_path]=lines.getvalue().encode()
    out=BytesIO()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    return out.getvalue()

class WheelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.built=build_fixture(cls.tmp.name)
    def setUp(self):
        self.inputs=deepcopy(self.built)
        self.files=read_archive(self.inputs["artifact_bytes"]["wheel"])
        self.dist=next(n.split("/")[0] for n in self.files if n.endswith(".dist-info/RECORD"))
        self.record=self.dist+"/RECORD"
    def check(self,proposal=None):
        return inspect_wheel(**self.inputs,submitted_proposal_raw=proposal if proposal is not None else proposal_for(self.inputs))
    def replace_archive(self,recompute=False):
        self.inputs["artifact_bytes"]["wheel"]=pack(self.files,self.record,recompute)
    def test_status_candidate(self):
        s=parse((ROOT/"STATUS.json").read_bytes())
        for k in ("normative","accepted","runtime_implemented","publication_implemented","stable_release_allowed"):
            self.assertIs(s[k],False)
    def test_real_built_wheel_inspection_and_review_binding(self):
        r=self.check()
        self.assertEqual(r["wheel_format"],"VERIFIED_RESTRICTED_PROFILE")
        self.assertEqual(r["artifact_sha256"],digest(self.inputs["artifact_bytes"]["wheel"]))
        self.assertEqual(r["proposal_sha256"],digest(proposal_for(self.inputs)))
        self.assertEqual(r["record_integrity"],"VERIFIED_EXACT_SHA256")
        self.assertEqual(r["embedded_metadata"],"MATCHED_EXACT_BYTES")
        for k in ("code_imported","source_provenance_verified","build_provenance_verified","runtime_compatibility_verified","installable","grants_authority"):
            self.assertIs(r[k],False)
        self.assertNotIn("openrgd_trust_probe",sys.modules)
        target=review_target(r,"org.example")
        self.assertEqual(target["inspection_sha256"],digest(encode_proposal(r)))
        self.assertFalse(target["publication_committed"])
    def test_no_network_process_or_provider_import_during_inspection(self):
        with patch.object(socket,"socket",side_effect=AssertionError("network")),patch.object(subprocess,"Popen",side_effect=AssertionError("process")):
            self.check()
        self.assertNotIn("openrgd_trust_probe",sys.modules)
    def test_changed_bytes_after_proposal(self):
        prior=proposal_for(self.inputs)
        self.files["openrgd_trust_probe/__init__.py"]+=b"# edit"
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"PROPOSAL_COMMITMENT_MISMATCH"):self.check(prior)
    def test_record_detects_changed_file_even_under_new_proposal(self):
        self.files["openrgd_trust_probe/__init__.py"]+=b"# edit"
        self.replace_archive()
        with self.assertRaisesRegex(InspectionError,"WHEEL_RECORD_MISMATCH"):self.check()
    def test_record_missing_entry(self):
        self.files["openrgd_trust_probe/extra.txt"]=b"unrecorded"
        self.replace_archive()
        with self.assertRaisesRegex(InspectionError,"WHEEL_RECORD_COVERAGE"):self.check()
    def test_record_duplicate_entry(self):
        self.files[self.record]+=self.files[self.record].splitlines(keepends=True)[0]
        self.replace_archive()
        with self.assertRaisesRegex(InspectionError,"WHEEL_RECORD_COVERAGE"):self.check()
    def test_filename_tag_or_identity_mismatch(self):
        for name in ("other-0.1.0-py3-none-any.whl","openrgd_trust_probe-0.1.0-py2-none-any.whl"):
            self.inputs["filename"]=name
            with self.subTest(name=name),self.assertRaisesRegex(InspectionError,"WHEEL_FILENAME_MISMATCH"):self.check()
    def test_package_metadata_mismatch_with_recomputed_record(self):
        p=self.dist+"/METADATA"
        self.files[p]=self.files[p].replace(b"Version: 0.1.0",b"Version: 0.2.0")
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_PACKAGE_MISMATCH"):self.check()
    def test_wheel_metadata_tag_mismatch(self):
        p=self.dist+"/WHEEL"
        self.files[p]=self.files[p].replace(b"py3-none-any",b"py2-none-any")
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_TAG_MISMATCH"):self.check()
    def test_exact_embedded_manifest_mismatch(self):
        self.files["openrgd_trust_probe/module.openrgd.json"]+=b" "
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_MANIFEST_MISMATCH"):self.check()
    def test_exact_embedded_descriptor_mismatch(self):
        self.files["openrgd_trust_probe/extensions/probe.json"]+=b" "
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_DESCRIPTOR_MISMATCH"):self.check()
    def test_entry_point_metadata_mismatch(self):
        p=self.dist+"/entry_points.txt"
        self.files[p]=self.files[p].replace(b":attach",b":different")
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_ENTRY_POINT_MISMATCH"):self.check()
    def test_extra_entrypoint_group_not_admitted(self):
        p=self.dist+"/entry_points.txt"
        self.files[p]+=b"\n[console_scripts]\nextra = openrgd_trust_probe:attach\n"
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"WHEEL_ENTRY_POINT_MISMATCH"):self.check()
    def test_traversal_rejected(self):
        self.files["../outside.txt"]=b"x"
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"UNSAFE_WHEEL_PATH"):self.check()
    def test_casefold_collision(self):
        self.files["openrgd_trust_probe/EXTENSIONS/probe.json"]=b"x"
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"DUPLICATE_WHEEL_PATH"):self.check()
    def test_symlink_rejected(self):
        out=BytesIO()
        with zipfile.ZipFile(out,"w") as z:
            info=zipfile.ZipInfo("x")
            info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16
            z.writestr(info,b"target")
        with self.assertRaisesRegex(InspectionError,"UNSUPPORTED_WHEEL_ENTRY"):read_archive(out.getvalue())
    def test_startup_hook_file_rejected(self):
        self.files["openrgd_trust_probe/evil.pth"]=b"x"
        self.replace_archive(True)
        with self.assertRaisesRegex(InspectionError,"UNSUPPORTED_WHEEL_CONTENT"):self.check()
    def test_bounded_expanded_size(self):
        files={"a"+str(i):b"x"*1048576 for i in range(5)}
        with self.assertRaisesRegex(InspectionError,"WHEEL_UNPACKED_LIMIT"):read_archive(pack(files))
    def test_namespace_boundary(self):
        r=self.check()
        with self.assertRaisesRegex(InspectionError,"NAMESPACE_SCOPE_MISMATCH"):review_target(r,"org.exam")
        with self.assertRaises(InspectionError):review_target(r,"org.example.trust")
        t=review_target(r,"org.example","WITHDRAWN")
        self.assertEqual(t["disposition"],"WITHDRAWN")

if __name__=="__main__":
    unittest.main(verbosity=2)
