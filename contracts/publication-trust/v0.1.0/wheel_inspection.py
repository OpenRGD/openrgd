"""Bounded, offline inspection of a narrow pure-Python wheel review profile.

Uses the exact EXT-01B candidate proposal and existing descriptors. Never extracts,
imports, installs, runs a provider, resolves dependencies or verifies build origin.
"""
from __future__ import annotations

import base64
import configparser
import csv
from email import policy
from email.parser import BytesParser
import hashlib
from io import BytesIO, StringIO
from pathlib import Path
import re
import stat
import zipfile

from jsonschema import Draft202012Validator
from packaging.tags import Tag, parse_tag
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version
from referencing import Resource
from proposal import (ProposalError, REGISTRY, parse, digest, propose,
                      inspect_manifest, encode_proposal)

MAX_FILES = 256
MAX_UNPACKED = 4 * 1024 * 1024
MAX_FILE = 1024 * 1024
ROOT = Path(__file__).resolve().parent
SCHEMA = parse((ROOT/"schemas/publication-trust.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
SCHEMA_REGISTRY = REGISTRY.with_resource(SCHEMA["$id"], Resource.from_contents(SCHEMA))
EXPECTED_TAGS = {Tag("py3", "none", "any")}
SEGMENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")

class InspectionError(ValueError):
    """Fixed, scoped diagnostic; never a permission."""

def need(condition, code):
    if not condition:
        raise InspectionError(code)

def check_shape(kind, value):
    validator = Draft202012Validator({"$ref":SCHEMA["$id"]+"#/$defs/"+kind},
                                     registry=SCHEMA_REGISTRY)
    need(validator.is_valid(value), "TRUST_EVIDENCE_SHAPE")

def read_archive(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_FILE, "WHEEL_BYTES_LIMIT")
    try:
        with zipfile.ZipFile(BytesIO(raw)) as z:
            entries = z.infolist()
            need(0 < len(entries) <= MAX_FILES, "WHEEL_ENTRY_LIMIT")
            files, folded = {}, set()
            total = 0
            for info in entries:
                name = info.filename
                parts = name.split("/")
                need(name == info.orig_filename and len(name) <= 240
                     and all(SEGMENT.fullmatch(p) and not p.endswith(".") for p in parts),
                     "UNSAFE_WHEEL_PATH")
                need(not any(p.casefold() in ("con","prn","aux","nul","com1","lpt1") for p in parts),
                     "UNSAFE_WHEEL_PATH")
                need(name.casefold() not in folded, "DUPLICATE_WHEEL_PATH")
                mode = (info.external_attr >> 16) & 0xffff
                need(not info.is_dir() and stat.S_IFMT(mode) in (0, stat.S_IFREG)
                     and not (info.flag_bits & 1), "UNSUPPORTED_WHEEL_ENTRY")
                need(info.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED)
                     and info.file_size <= MAX_FILE, "WHEEL_ENTRY_LIMIT")
                total += info.file_size
                need(total <= MAX_UNPACKED, "WHEEL_UNPACKED_LIMIT")
                # This is a deliberately narrow wheel profile, not a general installer.
                need(not any(p.endswith(".data") for p in parts)
                     and not name.lower().endswith((".pth",".pyc",".pyo",".so",".pyd",".dll",".dylib",".exe",".jws",".p7s")),
                     "UNSUPPORTED_WHEEL_CONTENT")
                with z.open(info) as f:
                    data = f.read(MAX_FILE+1)
                    need(len(data)==info.file_size and len(data)<=MAX_FILE,"WHEEL_SIZE_MISMATCH")
                    need(f.read(1)==b"","WHEEL_SIZE_MISMATCH")
                folded.add(name.casefold())
                files[name]=data
            for name in folded:
                parts=name.split("/")
                need(not any("/".join(parts[:i]) in folded for i in range(1,len(parts))),
                     "WHEEL_PATH_PREFIX_CONFLICT")
            return files
    except InspectionError:
        raise
    except (OSError, ValueError, RuntimeError, EOFError, NotImplementedError, zipfile.BadZipFile):
        raise InspectionError("INVALID_WHEEL_ARCHIVE") from None

def read_headers(raw):
    need(len(raw)<=65536,"WHEEL_HEADER_LIMIT")
    result=BytesParser(policy=policy.default).parsebytes(raw)
    need(not result.defects, "WHEEL_METADATA_INVALID")
    return result

def field(headers, key):
    vals=headers.get_all(key,[])
    need(len(vals)==1 and not vals[0].defects, "WHEEL_METADATA_FIELD")
    return str(vals[0])

def check_record(files, record_path):
    need(record_path in files, "WHEEL_RECORD_MISSING")
    try:
        csv_rows=csv.reader(StringIO(files[record_path].decode("utf-8"), newline=""),strict=True)
        seen=set()
        for row in csv_rows:
            need(len(row)==3 and len(seen)<MAX_FILES,"WHEEL_RECORD_INVALID")
            name,h,size=row
            need(name in files and name not in seen,"WHEEL_RECORD_COVERAGE")
            seen.add(name)
            if name==record_path:
                need(h==size=="","WHEEL_RECORD_SELF_HASH")
                continue
            expected=base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode("ascii").rstrip("=")
            need(h=="sha256="+expected and size==str(len(files[name])),"WHEEL_RECORD_MISMATCH")
        need(seen==set(files),"WHEEL_RECORD_COVERAGE")
    except InspectionError:
        raise
    except (UnicodeError,csv.Error):
        raise InspectionError("WHEEL_RECORD_INVALID") from None

def inspect_wheel(manifest_raw, descriptor_bytes, artifact_bytes, source_claim,
                  submitted_proposal_raw, filename):
    """Recompute the old proposal, then inspect exactly one wheel, no execution."""
    try:
        m=inspect_manifest(manifest_raw,descriptor_bytes)
        expected=propose(manifest_raw,descriptor_bytes,artifact_bytes,source_claim)
        need(encode_proposal(parse(submitted_proposal_raw))==encode_proposal(expected),
             "PROPOSAL_COMMITMENT_MISMATCH")
    except ProposalError as e:
        raise InspectionError("PUBLICATION_INPUT_REJECTED") from e
    need(len(m["artifact_slots"])==1 and len(m["command_facades"])==1,
         "UNSUPPORTED_ARTIFACT_PROFILE")
    slot=m["artifact_slots"][0]
    need(slot["artifact_kind"]=="python_wheel" and slot["platform_profile"]=="py3-none-any"
         and slot["media_type"]=="application/zip","UNSUPPORTED_ARTIFACT_PROFILE")
    need(type(filename) is str and len(filename)<=240 and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.whl",filename),
         "INVALID_WHEEL_FILENAME")
    try:
        package,version,build,tags=parse_wheel_filename(filename)
        expected_name=canonicalize_name(slot["package_name"],validate=True)
        expected_version=Version(slot["package_version"])
    except ValueError:
        raise InspectionError("INVALID_WHEEL_IDENTITY") from None
    need(package==expected_name and version==expected_version and not build and tags==EXPECTED_TAGS,
         "WHEEL_FILENAME_MISMATCH")
    raw=artifact_bytes[slot["slot_id"]]
    files=read_archive(raw)
    info_dirs={n.split("/")[0] for n in files if n.split("/")[0].endswith(".dist-info")}
    need(len(info_dirs)==1,"WHEEL_DIST_INFO_MISMATCH")
    dist=next(iter(info_dirs))
    need(dist==filename.rsplit("-",3)[0]+".dist-info","WHEEL_DIST_INFO_MISMATCH")
    for name in ("METADATA","WHEEL","RECORD","entry_points.txt"):
        need(dist+"/"+name in files,"WHEEL_METADATA_MISSING")
    check_record(files,dist+"/RECORD")
    meta=read_headers(files[dist+"/METADATA"])
    wheel=read_headers(files[dist+"/WHEEL"])
    try:
        need(canonicalize_name(field(meta,"Name"),validate=True)==expected_name
             and Version(field(meta,"Version"))==expected_version,"WHEEL_PACKAGE_MISMATCH")
        wheel_tags=set()
        for value in wheel.get_all("Tag",[]):
            wheel_tags.update(parse_tag(str(value)))
        need(wheel_tags==EXPECTED_TAGS,"WHEEL_TAG_MISMATCH")
    except ValueError as e:
        if isinstance(e,InspectionError):
            raise
        raise InspectionError("WHEEL_METADATA_INVALID") from None
    need(field(wheel,"Wheel-Version")=="1.0" and field(wheel,"Root-Is-Purelib").lower()=="true"
         and not wheel.get_all("Build"),"WHEEL_PROFILE_MISMATCH")
    # Bind the archive's actual facade to the already validated descriptor.
    facade_path=m["command_facades"][0]["descriptor"]["path"]
    facade=parse(descriptor_bytes[facade_path])
    cli=facade["cli"]
    module=cli["entry_point_target"].split(":")[0]
    import_root=module.split(".")[0]
    need(facade_path=="openrgd_commands/"+cli["entry_point_name"]+".json","WHEEL_FACADE_LAYOUT")
    try:
        ep=configparser.ConfigParser(interpolation=None,strict=True,default_section="__reserved__")
        ep.optionxform=str
        ep.read_string(files[dist+"/entry_points.txt"].decode("utf-8"))
        need(not ep.defaults() and ep.sections()==["rgd.commands"]
             and dict(ep.items("rgd.commands",raw=True))=={cli["entry_point_name"]:cli["entry_point_target"]},
             "WHEEL_ENTRY_POINT_MISMATCH")
    except (UnicodeError,configparser.Error):
        raise InspectionError("WHEEL_ENTRY_POINT_INVALID") from None
    # This profile supports only a single import root and its metadata. No other
    # top-level package, .data scheme, or namespace package is admitted here.
    need(import_root+"/__init__.py" in files and
         (module.replace(".","/")+".py" in files or module.replace(".","/")+"/__init__.py" in files),
         "WHEEL_ENTRY_POINT_MODULE_MISSING")
    need(all(n.startswith(import_root+"/") or n.startswith(dist+"/") for n in files),
         "WHEEL_EXTRA_ROOT")
    need(files.get(import_root+"/module.openrgd.json")==manifest_raw,"WHEEL_MANIFEST_MISMATCH")
    for path,data in descriptor_bytes.items():
        need(files.get(import_root+"/"+path)==data,"WHEEL_DESCRIPTOR_MISMATCH")
    declared_facades={import_root+"/"+facade_path}
    need({n for n in files if n.startswith(import_root+"/openrgd_commands/") and n.endswith(".json")}
         ==declared_facades,"WHEEL_UNDECLARED_FACADE")
    report={
        "schema_version":"openrgd.wheel-inspection.v0.1-candidate",
        "module_id":m["module_id"],"module_version":m["module_version"],
        "proposal_sha256":digest(submitted_proposal_raw),"slot_id":slot["slot_id"],
        "artifact_filename":filename,"artifact_sha256":digest(raw),"artifact_size_bytes":len(raw),
        "inspection_profile":"pure-python-wheel-cli-v0.1-candidate",
        "file_count":len(files),"record_integrity":"VERIFIED_EXACT_SHA256",
        "embedded_metadata":"MATCHED_EXACT_BYTES","entry_point_metadata":"MATCHED_DECLARATION",
        "wheel_format":"VERIFIED_RESTRICTED_PROFILE","code_imported":False,
        "source_provenance_verified":False,"build_provenance_verified":False,
        "runtime_compatibility_verified":False,"extension_semantics_verified":False,
        "dependency_resolution_verified":False,"installable":False,"grants_authority":False,
    }
    check_shape("WheelInspection",report)
    return report

def review_target(report, namespace, disposition="REVIEWED_CANDIDATE"):
    """Make unsigned target bytes for the independent registry role's review."""
    check_shape("WheelInspection",report)
    result={"schema_version":"openrgd.registry-review-target.v0.1-candidate",
            "module_id":report["module_id"],"module_version":report["module_version"],
            "publisher_namespace":namespace,"proposal_sha256":report["proposal_sha256"],
            "inspection_sha256":digest(encode_proposal(report)),
            "disposition":disposition,"publication_committed":False,
            "installable":False,"grants_authority":False}
    check_shape("RegistryReviewTarget",result)
    need(result["module_id"].startswith(namespace+"."),"NAMESPACE_SCOPE_MISMATCH")
    return result
