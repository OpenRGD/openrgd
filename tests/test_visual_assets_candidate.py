"""Hermetic, synthetic tests for NON-NORMATIVE visual ZIP manifest validator."""
import hashlib
import json
from pathlib import Path
import stat
import struct
import tempfile
import unittest
import warnings
import zipfile

from sys import path as import_path
import_path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_visual_asset_bundle as subject


def tiny_glb(uri=None):
    obj = {"asset": {"version": "2.0"}, "scenes": [{"nodes": []}], "scene": 0}
    if uri is not None:
        obj["buffers"] = [{"uri": uri, "byteLength": 0}]
    data = json.dumps(obj, separators=(",", ":")).encode()
    data += b" " * ((4 - len(data) % 4) % 4)
    length = 20 + len(data)
    return b"glTF" + struct.pack("<II", 2, length) + struct.pack("<I", len(data)) + b"JSON" + data


def manifest(blob, *, sha=None):
    return {
        "schema_version": subject.SCHEMA_VERSION,
        "evidence_class": "UPSTREAM_MODEL_REFERENCE_UNVERIFIED",
        "source_profile_ref": "synthetic-demo-not-Paky01",
        "coordinate_frame": {"up_axis": "Z_UP", "forward_axis": "X_FORWARD",
                             "linear_unit": "m", "angular_unit": "rad"},
        "attribution": [{"id": "test", "name": "synthetic-only",
                         "license": "TEST_FIXTURE", "source": "https://example.org"}],
        "assets": [{
            "asset_id": "torso_render", "link_id": "base", "role": "visual_runtime",
            "path": "assets/visual/torso_render.glb", "media_format": "glb",
            "sha256": sha or "sha256:" + hashlib.sha256(blob).hexdigest(),
            "size_bytes": len(blob),
            "origin_xyz_m": [0, 0, 0], "origin_rpy_rad": [0, 0, 0],
            "mesh_scale_xyz": [1, 1, 1], "provenance": "UPSTREAM_SOURCE",
            "license_id": "TEST_FIXTURE", "attribution_ref": "test",
        }],
    }


def make_zip(target, m, mesh, *, wrapper="", asset_name=None, with_source=True, symlink=False):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as f:
        if with_source:
            f.writestr(wrapper + "spec/01_foundation/description.jsonc", "{}")
        f.writestr(wrapper + "assets/visual/manifest.json", json.dumps(m))
        name = asset_name or wrapper + "assets/visual/torso_render.glb"
        if symlink:
            item = zipfile.ZipInfo(name)
            item.create_system = 3
            item.external_attr = (stat.S_IFLNK | 0o777) << 16
            f.writestr(item, "link-target")
        else:
            f.writestr(name, mesh)


class VisualCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.zip = Path(self.temp.name) / "sample.rgd"
        self.mesh = tiny_glb()

    def test_valid_local_bundle_reports_only_descriptive_evidence(self):
        make_zip(self.zip, manifest(self.mesh), self.mesh)
        result = subject.inspect(self.zip)
        self.assertEqual(result["asset_count"], 1)
        self.assertIn("not_canonical", result["status"])
        self.assertFalse(result["physical_calibration_verified"])
        self.assertFalse(result["actuation_enabled"])
        self.assertTrue(result["manifest_sha256"].startswith("sha256:"))

    def test_one_wrapper_directory_is_allowed(self):
        make_zip(self.zip, manifest(self.mesh), self.mesh, wrapper="Robot/")
        self.assertEqual(subject.inspect(self.zip)["asset_bytes"], len(self.mesh))

    def test_rejects_missing_source(self):
        make_zip(self.zip, manifest(self.mesh), self.mesh, with_source=False)
        with self.assertRaisesRegex(subject.VisualManifestError, "description.jsonc"):
            subject.inspect(self.zip)

    def test_rejects_wrong_digest(self):
        make_zip(self.zip, manifest(self.mesh, sha="sha256:" + "0" * 64), self.mesh)
        with self.assertRaisesRegex(subject.VisualManifestError, "SHA mismatch"):
            subject.inspect(self.zip)

    def test_rejects_path_traversal_archive_entry(self):
        make_zip(self.zip, manifest(self.mesh), self.mesh, asset_name="../bad.glb")
        with self.assertRaisesRegex(subject.VisualManifestError, "unsafe ZIP entry"):
            subject.inspect(self.zip)

    def test_rejects_symlink(self):
        make_zip(self.zip, manifest(self.mesh), self.mesh, symlink=True)
        with self.assertRaisesRegex(subject.VisualManifestError, "unsafe ZIP entry"):
            subject.inspect(self.zip)

    def test_rejects_external_glb_uri(self):
        mesh = tiny_glb("https://example.org/not-allowed.bin")
        make_zip(self.zip, manifest(mesh), mesh)
        with self.assertRaisesRegex(subject.VisualManifestError, "resource URI"):
            subject.inspect(self.zip)

    def test_rejects_nonfinite_and_missing_transform(self):
        m = manifest(self.mesh)
        m["assets"][0]["origin_xyz_m"] = [0, 0, float("nan")]
        with self.assertRaisesRegex(subject.VisualManifestError, "non-finite"):
            subject.parse_manifest(json.dumps(m).encode())
        del m["assets"][0]["origin_xyz_m"]
        with self.assertRaisesRegex(subject.VisualManifestError, "origin_xyz_m"):
            subject.parse_manifest(json.dumps(m).encode())

    def test_rejects_malformed_member_types(self):
        m = manifest(self.mesh)
        m["assets"][0]["role"] = []
        with self.assertRaises(subject.VisualManifestError):
            subject.parse_manifest(json.dumps(m).encode())
        m = manifest(self.mesh)
        m["evidence_class"] = {}
        with self.assertRaises(subject.VisualManifestError):
            subject.parse_manifest(json.dumps(m).encode())

    def test_rejects_url_path_and_duplicate_ids(self):
        m = manifest(self.mesh)
        m["assets"][0]["path"] = "https://example.org/render.glb"
        with self.assertRaisesRegex(subject.VisualManifestError, "local path"):
            subject.parse_manifest(json.dumps(m).encode())
        m = manifest(self.mesh)
        m["assets"].append(dict(m["assets"][0]))
        with self.assertRaisesRegex(subject.VisualManifestError, "asset_id"):
            subject.parse_manifest(json.dumps(m).encode())

    def test_rejects_duplicate_json_field(self):
        raw = b'{"schema_version":"rgd.visual-assets.v0.1-candidate","schema_version":"evil"}'
        with self.assertRaisesRegex(subject.VisualManifestError, "duplicate JSON"):
            subject.parse_manifest(raw)

    def test_rejects_duplicate_zip_entry(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.zip, "w", zipfile.ZIP_DEFLATED) as f:
                f.writestr("assets/visual/manifest.json", json.dumps(manifest(self.mesh)))
                f.writestr("assets/visual/manifest.json", json.dumps(manifest(self.mesh)))
                f.writestr("spec/01_foundation/description.jsonc", "{}")
                f.writestr("assets/visual/torso_render.glb", self.mesh)
        with self.assertRaisesRegex(subject.VisualManifestError, "duplicate ZIP"):
            subject.inspect(self.zip)


if __name__ == "__main__":
    unittest.main()
