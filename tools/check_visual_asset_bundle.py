#!/usr/bin/env python3
"""Offline, non-actuating validation for candidate RGD visual asset ZIP bundles.

NOT a replacement for "rgd check", and NOT a standard/canonical verifier.
This tool never extracts files, loads mesh parsers, opens devices or fetches URLs.
It validates the manifest, bounded ZIP structure, per-file hashes and attribution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys
import zipfile

SCHEMA_VERSION = "rgd.visual-assets.v0.1-candidate"
MANIFEST_PATH = "assets/visual/manifest.json"
MAX_ZIP_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 128 * 1024 * 1024
MAX_BLOB_BYTES = 32 * 1024 * 1024
MAX_ZIP_ENTRIES = 256
MAX_ASSETS = 128
BUFFER = 1024 * 1024
FLAT_PATH = re.compile(r"^assets/(visual|collision|cad)/[A-Za-z0-9_-]+\.(glb|stl|usd|usda|step|stp)$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,119}$")
ROLE_FORMAT = {
    "visual_runtime": {"glb", "stl"},
    "visual_source": {"glb", "stl", "usd", "usda", "step", "stp"},
    "collision_preview": {"glb", "stl", "usd", "usda"},
}
EVIDENCE = {"UPSTREAM_MODEL_REFERENCE_UNVERIFIED", "AS_BUILT_OVERLAY_OPERATOR_REPORTED_UNVERIFIED"}
PROVENANCE = {"UPSTREAM_SOURCE", "CONVERTED_FROM_UPSTREAM", "AS_BUILT_OPERATOR_EDIT_UNVERIFIED"}


class VisualManifestError(ValueError):
    """A descriptive, fail-closed validation result."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VisualManifestError(message)


def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    data: dict = {}
    for k, v in pairs:
        require(k not in data, f"duplicate JSON field: {k}")
        data[k] = v
    return data


def parse_manifest(raw: bytes) -> dict:
    require(len(raw) <= 1024 * 1024, "visual manifest exceeds 1 MiB")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                          parse_constant=lambda token: (_ for _ in ()).throw(
                              VisualManifestError("non-finite JSON value: " + token)))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VisualManifestError("manifest is not strict UTF-8 JSON: " + str(exc)) from exc
    require(type(data) is dict, "manifest must be a JSON object")
    require(data.get("schema_version") == SCHEMA_VERSION, "unsupported visual manifest version")
    require(type(data.get("evidence_class")) is str and data["evidence_class"] in EVIDENCE,
            "missing/unverified evidence class")
    require(type(data.get("source_profile_ref")) is str and 0 < len(data["source_profile_ref"]) <= 200,
            "source_profile_ref required")
    frame = data.get("coordinate_frame")
    require(type(frame) is dict, "coordinate_frame object required")
    require(frame.get("linear_unit") == "m" and frame.get("angular_unit") == "rad",
            "all asset transforms must be in SI metres/radians")
    require(type(frame.get("up_axis")) is str and frame["up_axis"] in {"Z_UP", "Y_UP"},
            "invalid model up axis")
    require(type(frame.get("forward_axis")) is str and frame["forward_axis"] in {"X_FORWARD", "Z_FORWARD"},
            "invalid model forward axis")
    items = data.get("assets")
    require(type(items) is list and len(items) <= MAX_ASSETS, "asset list too large")
    require(all(type(x) is dict for x in items), "each asset must be an object")
    attribution = data.get("attribution", [])
    require(type(attribution) is list and len(attribution) <= 20, "invalid attribution list")
    credits: set[str] = set()
    for credit in attribution:
        require(type(credit) is dict, "invalid attribution entry")
        key = credit.get("id")
        require(type(key) is str and ID.fullmatch(key) is not None and key not in credits,
                "duplicate/invalid attribution id")
        credits.add(key)
        for field in ("name", "license", "source"):
            require(type(credit.get(field)) is str and bool(credit[field]),
                    "missing attribution " + field)
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, asset in enumerate(items):
        asset_id = asset.get("asset_id")
        require(type(asset_id) is str and ID.fullmatch(asset_id) is not None
                and asset_id not in seen_ids, f"invalid/duplicate asset_id at #{index}")
        seen_ids.add(asset_id)
        link_id = asset.get("link_id")
        require(type(link_id) is str and ID.fullmatch(link_id) is not None,
                f"{asset_id}: invalid link id")
        path = asset.get("path")
        require(type(path) is str and FLAT_PATH.fullmatch(path) is not None
                and path not in seen_paths, f"{asset_id}: invalid/duplicate local path")
        seen_paths.add(path)
        require(not path.startswith("/") and "\\" not in path and ".." not in path,
                f"{asset_id}: illegal path")
        fmt = asset.get("media_format")
        role = asset.get("role")
        require(type(role) is str and type(fmt) is str and role in ROLE_FORMAT and fmt in ROLE_FORMAT[role],
                f"{asset_id}: unsupported role/format")
        require(path.endswith("." + fmt), f"{asset_id}: format/path extension mismatch")
        require(type(asset.get("provenance")) is str and asset["provenance"] in PROVENANCE,
                f"{asset_id}: provenance required")
        require(type(asset.get("license_id")) is str and bool(asset["license_id"]),
                f"{asset_id}: license required")
        if "attribution_ref" in asset:
            require(asset["attribution_ref"] in credits, f"{asset_id}: missing attribution reference")
        sha = asset.get("sha256")
        require(type(sha) is str and SHA256.fullmatch(sha) is not None,
                f"{asset_id}: sha256 invalid")
        size = asset.get("size_bytes")
        require(type(size) is int and 0 < size <= MAX_BLOB_BYTES,
                f"{asset_id}: declared size out of range")
        for name in ("origin_xyz_m", "origin_rpy_rad", "mesh_scale_xyz"):
            vector = asset.get(name)
            require(type(vector) is list and len(vector) == 3 and all(
                type(v) in (int, float) and math.isfinite(v) for v in vector
            ), f"{asset_id}: invalid or non-finite {name}")
            if name == "mesh_scale_xyz":
                require(all(v > 0 for v in vector), f"{asset_id}: mesh scale must be positive")
    for asset in items:
        if "derived_from_asset_id" in asset:
            require(asset["derived_from_asset_id"] in seen_ids, "dangling derived_from_asset_id")
            require(asset["derived_from_asset_id"] != asset["asset_id"], "self-referential asset")
    return data


def safe_zip_entry(z: zipfile.ZipInfo) -> bool:
    name = z.filename
    if not name or name.startswith("/") or "\\" in name or "\x00" in name:
        return False
    if any(part in ("", ".", "..") for part in name.rstrip("/").split("/")):
        return False
    if not z.is_dir() and z.file_size > MAX_BLOB_BYTES:
        return False
    if stat.S_IFMT(z.external_attr >> 16) == stat.S_IFLNK:
        return False
    return True


def archive_root(names: list[str]) -> str:
    candidates = [name[: -len(MANIFEST_PATH)] for name in names if name.endswith(MANIFEST_PATH)]
    require(len(candidates) == 1, "exactly one assets/visual/manifest.json is required")
    prefix = candidates[0]
    require(prefix == "" or (prefix.endswith("/") and "/" not in prefix[:-1]),
            "manifest must be under ZIP root or one wrapper directory")
    return prefix


def check_glb_json(bundle: zipfile.ZipFile, entry: zipfile.ZipInfo) -> None:
    """Validate GLB v2 header and JSON chunk; reject external resource URIs."""
    with bundle.open(entry) as src:
        header = src.read(20)
        require(len(header) == 20 and header[:4] == b"glTF" and
                struct.unpack("<I", header[4:8])[0] == 2 and
                struct.unpack("<I", header[8:12])[0] == entry.file_size,
                "GLB header/declared size invalid")
        json_bytes = struct.unpack("<I", header[12:16])[0]
        require(header[16:20] == b"JSON" and json_bytes > 0 and
                json_bytes <= 2 * 1024 * 1024 and
                20 + json_bytes <= entry.file_size,
                "GLB JSON chunk invalid or oversized")
        raw = src.read(json_bytes)
        require(len(raw) == json_bytes, "GLB JSON chunk truncated")
        try:
            root = json.loads(raw.decode("utf-8").rstrip("\\x00 \\n\\r\\t"),
                              object_pairs_hook=no_duplicates)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise VisualManifestError("GLB JSON invalid: " + str(exc)) from exc
        require(type(root) is dict and type(root.get("asset")) is dict and
                root["asset"].get("version") == "2.0", "GLB asset.version != 2.0")
        # Content-addressed glTF package only. External fetch is not allowed,
        # even if the browser would ordinarily resolve an image or buffer URI.
        for field in ("images", "buffers", "shaders"):
            items = root.get(field, [])
            require(type(items) is list and len(items) <= 512, "invalid GLB " + field)
            for item in items:
                require(type(item) is dict and item.get("uri") is None,
                        "GLB contains external or data: resource URI in " + field)


def inspect(path: Path) -> dict:
    require(path.is_file() and path.stat().st_size <= MAX_ZIP_BYTES, "archive missing or exceeds 64 MiB")
    with zipfile.ZipFile(path, "r") as bundle:
        infos = bundle.infolist()
        require(len(infos) <= MAX_ZIP_ENTRIES, "too many ZIP entries")
        names: set[str] = set()
        total = 0
        for entry in infos:
            require(safe_zip_entry(entry), "unsafe ZIP entry " + entry.filename)
            require(entry.filename not in names, "duplicate ZIP path " + entry.filename)
            names.add(entry.filename)
            total += entry.file_size
            require(total <= MAX_UNCOMPRESSED_BYTES, "total inflated bytes exceed 128 MiB")
            require(entry.compress_type in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED),
                    "unsupported ZIP compression")
        root = archive_root(list(names))
        mpath = root + MANIFEST_PATH
        info = bundle.getinfo(mpath)
        require(info.file_size <= 1024 * 1024, "manifest too large")
        manifest = parse_manifest(bundle.read(info))
        # This is additional evidence checking only, not "rgd check" or schema conformance.
        require(root + "spec/01_foundation/description.jsonc" in names,
                "source profile spec/01_foundation/description.jsonc missing")
        digest_manifest = hashlib.sha256(bundle.read(mpath)).hexdigest()
        count = 0
        num_bytes = 0
        for asset in manifest["assets"]:
            name = root + asset["path"]
            require(name in names, f"{asset['asset_id']}: blob not in RGD archive")
            entry = bundle.getinfo(name)
            require(entry.file_size == asset["size_bytes"], f"{asset['asset_id']}: size mismatch")
            h = hashlib.sha256()
            seen = 0
            leading = b""
            with bundle.open(entry) as src:
                while True:
                    chunk = src.read(BUFFER)
                    if not chunk:
                        break
                    if not leading:
                        leading = chunk[:16]
                    seen += len(chunk)
                    require(seen <= MAX_BLOB_BYTES, f"{asset['asset_id']}: blob over budget")
                    h.update(chunk)
            require("sha256:" + h.hexdigest() == asset["sha256"], f"{asset['asset_id']}: SHA mismatch")
            if asset["media_format"] == "glb":
                check_glb_json(bundle, entry)
            count += 1
            num_bytes += seen
        return {
            "schema_version": manifest["schema_version"],
            "status": "candidate_archive_structure_checked_not_canonical_or_as_built_certified",
            "asset_count": count,
            "asset_bytes": num_bytes,
            "manifest_sha256": "sha256:" + digest_manifest,
            "source_profile_ref": manifest["source_profile_ref"],
            "physical_calibration_verified": False,
            "actuation_enabled": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="ZIP-packaged RGD source profile with optional candidate visual assets")
    args = parser.parse_args()
    try:
        result = inspect(args.archive)
    except (VisualManifestError, OSError, zipfile.BadZipFile, KeyError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
