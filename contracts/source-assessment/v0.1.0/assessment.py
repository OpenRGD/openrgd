"""CORE-CAL-01A candidate, read-only source assessment.

V1 root/index computation is delegated to the exact existing Core implementation.
The strict parser is a conservative admission/check profile, NOT a new hasher.
Requires a trusted interpreter, checkout and stable operator-controlled input tree.
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
import sys
import tempfile

from openrgd.core import canonical

ROOT = Path(__file__).resolve().parent
CORE_REF = "afe1a831b950a4e6560f0285a0103fc4eaa343b7"
CORE_BLOBS = {
    "canonical.py": "543f4da4754aa74a952aadd0c3a04724d77d0eab",
    "utils.py": "ed9ed2279b8a75362096a311e608b7e07bdef73d",
    "config.py": "9896ebe283844e4390fb163be52f63e0ae3dc11a",
    "visuals.py": "453098cb538bf6c2b19d7fde92cb2b16ee9ea6e0",
}
PROFILE = "OPENRGD_SOURCE_TREE_SHA256_V1"
MAX_ENTRIES = 256
MAX_FILE = 4 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_POLICY = 65536
MAX_DEPTH = 64
MAX_NODES = 100000
HASH = re.compile(r"sha256:[a-f0-9]{64}")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
PROFILE_ID = re.compile(r"(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.)+[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
SEGMENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")
SOURCE_PATH = re.compile(r"(?:[A-Za-z0-9_][A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:jsonc|md)")

class AssessmentError(ValueError):
    """Fixed diagnostic code, no local paths or untrusted payload in text."""

class RequirementsError(ValueError):
    """Invalid external policy, not a source assessment result."""

def need(ok, code):
    if not ok:
        raise AssessmentError(code)

def sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def read_regular(path, limit):
    path=Path(path)
    need(stat.S_ISREG(path.lstat().st_mode),"UNSAFE_SOURCE_ENTRY")
    flags=os.O_RDONLY | getattr(os,"O_NOFOLLOW",0) | getattr(os,"O_NONBLOCK",0) | getattr(os,"O_BINARY",0)
    with os.fdopen(os.open(path,flags),"rb") as f:
        meta=os.fstat(f.fileno())
        need(stat.S_ISREG(meta.st_mode),"UNSAFE_SOURCE_ENTRY")
        need(meta.st_size<=limit,"SOURCE_BYTE_LIMIT")
        raw=f.read(limit+1)
    need(len(raw)<=limit,"SOURCE_BYTE_LIMIT")
    return raw

def safe_relative(path):
    if not isinstance(path,str) or len(path)>240:
        return False
    for part in path.split("/"):
        if not SEGMENT.fullmatch(part) or part.endswith("."):
            return False
        if re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])",part.split(".")[0]):
            return False
    return True

def source_path(path):
    return safe_relative(path) and SOURCE_PATH.fullmatch(path) is not None

def snapshot_spec(bundle, target):
    bundle=Path(bundle).absolute()
    if not bundle.exists() and not bundle.is_symlink():
        raise AssessmentError("SOURCE_TREE_UNAVAILABLE")
    need(stat.S_ISDIR(bundle.lstat().st_mode),"UNSAFE_SOURCE_ENTRY")
    source=bundle if bundle.name=="spec" else bundle/"spec"
    if not source.exists() and not source.is_symlink():
        raise AssessmentError("SOURCE_TREE_UNAVAILABLE")
    need(stat.S_ISDIR(source.lstat().st_mode),"UNSAFE_SOURCE_ENTRY")
    destination=Path(target)/"spec"
    destination.mkdir(parents=True)
    seen=set()
    count=total=0
    def fail_walk(error):
        raise error
    for directory,dirs,files in os.walk(source,followlinks=False,onerror=fail_walk):
        parent=Path(directory)
        for name in sorted(dirs+files):
            count+=1
            need(count<=MAX_ENTRIES,"SOURCE_ENTRY_LIMIT")
            path=parent/name
            rel=path.relative_to(source).as_posix()
            need(safe_relative(rel) and rel.casefold() not in seen,"UNSAFE_SOURCE_ENTRY")
            seen.add(rel.casefold())
            out=destination/rel
            mode=path.lstat().st_mode
            if stat.S_ISDIR(mode):
                out.mkdir()
            elif stat.S_ISREG(mode):
                raw=read_regular(path,min(MAX_FILE,MAX_TOTAL-total))
                total+=len(raw)
                out.write_bytes(raw)
            else:
                raise AssessmentError("UNSAFE_SOURCE_ENTRY")
    return destination

def check_core_pin():
    need(canonical.INTEGRITY_PROFILE==PROFILE,"CORE_PIN_MISMATCH")
    parent=Path(canonical.__file__).parent
    try:
        for name,expected in CORE_BLOBS.items():
            need(git_blob(read_regular(parent/name,MAX_FILE))==expected,"CORE_PIN_MISMATCH")
    except OSError as e:
        raise AssessmentError("CORE_PIN_MISMATCH") from e

def uncomment(text):
    """Replace comments with whitespace, without joining JSON tokens.

    Preserve all character offsets and CR/LF. JSON itself checks escapes,
    strings and punctuation. This is NOT used for V1 hashing.
    """
    out=list(text)
    i=0
    in_string=False
    while i<len(text):
        ch=text[i]
        if in_string:
            if ch=="\\":
                i+=2
                continue
            if ch=='"':
                in_string=False
            i+=1
            continue
        if ch=='"':
            in_string=True;i+=1
            continue
        if text.startswith("//",i):
            end=i+2
            while end<len(text) and text[end] not in "\r\n":
                end+=1
        elif text.startswith("/*",i):
            close=text.find("*/",i+2)
            need(close!=-1,"JSONC_UNTERMINATED_COMMENT")
            end=close+2
        else:
            i+=1
            continue
        for j in range(i,end):
            if text[j] not in "\r\n":
                out[j]=" "
        i=end
    return "".join(out)

def unique(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,"JSONC_DUPLICATE_KEY")
        result[key]=value
    return result

def finite_float(raw):
    v=float(raw)
    need(math.isfinite(v),"JSONC_NONFINITE_NUMBER")
    return v

def bounded_int(raw):
    need(len(raw)<=64,"JSONC_STRUCTURE_LIMIT")
    return int(raw)

def no_constant(_):
    raise AssessmentError("JSONC_NONFINITE_NUMBER")

def decode_text(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeError as e:
        raise AssessmentError("INVALID_UTF8") from e

def parse_object(text):
    try:
        value=json.loads(text,object_pairs_hook=unique,parse_float=finite_float,
                         parse_int=bounded_int,parse_constant=no_constant,strict=True)
        need(isinstance(value,dict),"JSONC_OBJECT_REQUIRED")
        stack=[(value,0)]
        nodes=0
        while stack:
            v,depth=stack.pop()
            nodes+=1
            need(nodes<=MAX_NODES and depth<=MAX_DEPTH,"JSONC_STRUCTURE_LIMIT")
            if isinstance(v,dict):
                for k,x in v.items():
                    k.encode("utf-8")
                    stack.append((x,depth+1))
            elif isinstance(v,list):
                stack.extend((x,depth+1) for x in v)
            elif isinstance(v,str):
                v.encode("utf-8")
        return value
    except AssessmentError:
        raise
    except (json.JSONDecodeError,UnicodeError,ValueError,RecursionError,OverflowError) as e:
        raise AssessmentError("JSONC_INVALID") from e

def parse_conservative(raw):
    """Check strict subset and agreement with the pinned legacy interpretation."""
    text=decode_text(raw)
    clean=uncomment(text)
    obj=parse_object(clean)
    try:
        legacy=json.loads(canonical.strip_jsonc(text),strict=False,
                          object_pairs_hook=unique,parse_float=finite_float,
                          parse_int=bounded_int,parse_constant=no_constant)
        need(json.dumps(legacy,sort_keys=True,allow_nan=False,ensure_ascii=True)==
             json.dumps(obj,sort_keys=True,allow_nan=False,ensure_ascii=True),
             "LEGACY_PARSER_DISAGREEMENT")
    except (ValueError,TypeError,RecursionError,OverflowError) as e:
        raise AssessmentError("LEGACY_PARSER_DISAGREEMENT") from e
    return text,clean,obj

def key_count(value,key):
    count=0
    stack=[value]
    while stack:
        item=stack.pop()
        if isinstance(item,dict):
            count+=int(key in item)
            stack.extend(item.values())
        elif isinstance(item,list):
            stack.extend(item)
    return count

def valid_version(value):
    return isinstance(value,str) and len(value)<=64 and VERSION.fullmatch(value) is not None

def manifest_preflight(raw):
    text,clean,manifest=parse_conservative(raw)
    meta=manifest.get("meta_group")
    need(isinstance(meta,dict),"MANIFEST_META_INVALID")
    # Use exactly the pinned V1 regexes only to characterize their match. Do
    # not normalize or compute the V1 hash here.
    for field,pattern in (("integrity_hash_str",canonical._INTEGRITY_FIELD_RE),
                          ("integrity_profile_str",canonical._PROFILE_FIELD_RE)):
        matches=list(pattern.finditer(text))
        need(text.count('"'+field+'"')==1 and key_count(manifest,field)==1
             and len(matches)==1,"MANIFEST_SELF_FIELD_AMBIGUOUS")
        match=matches[0]
        need(text[match.start():match.end()]==clean[match.start():match.end()]
             and field in meta and match.group("value")==meta[field],
             "MANIFEST_SELF_FIELD_AMBIGUOUS")
    declared=meta["integrity_hash_str"]
    profile=meta["integrity_profile_str"]
    need(isinstance(declared,str) and HASH.fullmatch(declared),"MANIFEST_DIGEST_INVALID")
    need(isinstance(profile,str) and bool(profile),"MANIFEST_PROFILE_INVALID")
    version=meta.get("rgd_standard_version_semver_str")
    return declared,profile,version if valid_version(version) else None

def parse_requirements(raw):
    if raw is None:
        return None
    try:
        need(type(raw) is bytes and 0<len(raw)<=MAX_POLICY,"REQUIREMENTS_LIMIT")
        p=parse_object(decode_text(raw))
        need(set(p)=={"schema_version","profile_id","profile_version","standard_version","required_paths"},
             "REQUIREMENTS_SHAPE")
        need(p["schema_version"]=="openrgd.required-source-profile.v0.1-candidate" and
             isinstance(p["profile_id"],str) and len(p["profile_id"])<=160 and
             PROFILE_ID.fullmatch(p["profile_id"]) and valid_version(p["profile_version"]) and
             valid_version(p["standard_version"]),"REQUIREMENTS_SHAPE")
        paths=p["required_paths"]
        need(isinstance(paths,list) and 0<len(paths)<=MAX_ENTRIES and all(source_path(x) for x in paths),
             "REQUIREMENTS_PATHS")
        need(len(paths)==len(set(paths)) and len(paths)==len({x.casefold() for x in paths}),
             "REQUIREMENTS_PATHS")
        return p
    except AssessmentError as e:
        raise RequirementsError("INVALID_REQUIRED_SOURCE_PROFILE") from e

def base_report(requirements, raw):
    return {
        "schema_version":"openrgd.source-assessment.v0.1-candidate",
        "assessment_profile":"OPENRGD_SOURCE_ASSESSMENT_V0.1_CANDIDATE",
        "core_reference_commit":CORE_REF,"core_toolchain_version":"0.1.1",
        "core_source_files_pin_checked":False,"integrity_profile":PROFILE,
        "input_status":"SOURCE_TREE_UNAVAILABLE","manifest_status":"NOT_ASSESSED",
        "integrity_status":"NOT_ASSESSED","indexed_jsonc_syntax_status":"NOT_ASSESSED",
        "declared_standard_version":None,"declared_source_tree_sha256":None,
        "computed_source_tree_sha256":None,"source_index":None,"raw_file_commitments":[],
        "requirements_profile":None if requirements is None else {
            "profile_id":requirements["profile_id"],"profile_version":requirements["profile_version"],
            "standard_version":requirements["standard_version"],"profile_sha256":sha(raw),
            "required_path_count":len(requirements["required_paths"])},
        "required_paths_status":"NOT_ASSESSED","missing_required_paths":[],"diagnostics":[],
        "canonical_schema_validated":False,"semantic_consistency_validated":False,
        "kernel_selection_assessed":False,"publisher_verified":False,"robot_binding_verified":False,
        "profile_model_hash_bound":False,"physical_calibration_certified":False,
        "actuation_enabled":False,"grants_authority":False,
    }

def diag(report,code,path=None):
    report["diagnostics"].append({"code":code,"path":path})

def assess_source(bundle, required_profile_raw=None):
    """Read-only bounded assessment. No output or changes to supplied paths."""
    requirements=parse_requirements(required_profile_raw)
    r=base_report(requirements,required_profile_raw)
    with tempfile.TemporaryDirectory(prefix="rgd-source-assessment-") as tmp:
        try:
            spec=snapshot_spec(bundle,tmp)
            r["input_status"]="SNAPSHOT_CREATED"
        except (AssessmentError,OSError) as e:
            code=str(e) if isinstance(e,AssessmentError) else "SOURCE_READ_FAILED"
            r["input_status"]="SOURCE_TREE_UNAVAILABLE" if code=="SOURCE_TREE_UNAVAILABLE" else "SNAPSHOT_REJECTED"
            diag(r,code)
            return r
        try:
            check_core_pin()
            r["core_source_files_pin_checked"]=True
        except AssessmentError:
            diag(r,"CORE_PIN_MISMATCH")
            r["integrity_status"]="VERIFICATION_FAILED"
            return r
        if not (spec/"manifest.jsonc").is_file():
            r["manifest_status"]="REJECTED"
            diag(r,"MANIFEST_MISSING","manifest.jsonc")
            return r
        try:
            declared,profile,version=manifest_preflight(read_regular(spec/"manifest.jsonc",MAX_FILE))
            r["declared_source_tree_sha256"]=declared
            r["declared_standard_version"]=version
            if profile!=PROFILE:
                r["manifest_status"]="UNSUPPORTED_PROFILE"
                diag(r,"UNSUPPORTED_INTEGRITY_PROFILE","manifest.jsonc")
                return r
            r["manifest_status"]="PASS"
        except (AssessmentError,OSError) as e:
            r["manifest_status"]="REJECTED"
            diag(r,str(e) if isinstance(e,AssessmentError) else "SOURCE_READ_FAILED","manifest.jsonc")
            return r
        # Only the pinned Core computes the canonical source-tree root.
        try:
            result=canonical.compute_integrity(spec)
            need(result.profile==PROFILE and result.declared==declared and
                 isinstance(result.computed,str) and HASH.fullmatch(result.computed) and
                 result.matches==(result.computed==declared),"CORE_RESULT_INCONSISTENT")
            raw_entries=[]
            indexed=set()
            need(len(result.index["files"])==result.files_count and 0<result.files_count<=MAX_ENTRIES,
                 "CORE_RESULT_INCONSISTENT")
            for entry in result.index["files"]:
                rel=entry["path"]
                need(source_path(rel) and rel not in indexed,"CORE_RESULT_INCONSISTENT")
                indexed.add(rel)
                raw=read_regular(spec/rel,MAX_FILE)
                d=sha(raw)
                if rel!="manifest.jsonc":
                    need(d.removeprefix("sha256:")==entry["sha256"] and len(raw)==entry["size_bytes"],
                         "CORE_RESULT_INCONSISTENT")
                raw_entries.append({"path":rel,"raw_sha256":d,"size_bytes":len(raw)})
            need("manifest.jsonc" in indexed and [x["path"] for x in raw_entries]==sorted(indexed),
                 "CORE_RESULT_INCONSISTENT")
        except (AssessmentError,canonical.CanonicalIntegrityError,OSError,ValueError,TypeError,KeyError,AttributeError,RecursionError) as e:
            r["integrity_status"]="VERIFICATION_FAILED"
            diag(r,str(e) if isinstance(e,AssessmentError) else "CORE_VERIFICATION_FAILED")
            return r
        r.update(integrity_status="MATCH" if result.matches else "MISMATCH",
                 computed_source_tree_sha256=result.computed,source_index=result.index,
                 raw_file_commitments=raw_entries,indexed_jsonc_syntax_status="PASS")
        if not result.matches:
            diag(r,"SOURCE_ROOT_MISMATCH")
        # Syntax and presence checks remain independent of root matching.
        for rel in sorted(indexed):
            if not rel.endswith(".jsonc") or rel=="manifest.jsonc":
                continue
            try:
                parse_conservative(read_regular(spec/rel,MAX_FILE))
            except (AssessmentError,OSError) as e:
                r["indexed_jsonc_syntax_status"]="FAIL"
                diag(r,str(e) if isinstance(e,AssessmentError) else "SOURCE_READ_FAILED",rel)
        if requirements is not None:
            if version!=requirements["standard_version"]:
                r["required_paths_status"]="PROFILE_VERSION_MISMATCH"
                diag(r,"REQUIRED_PROFILE_VERSION_MISMATCH")
            else:
                missing=sorted(set(requirements["required_paths"])-indexed)
                r["missing_required_paths"]=missing
                r["required_paths_status"]="REQUIRED_PATHS_MISSING" if missing else "REQUIRED_PATHS_PRESENT"
                if missing:
                    diag(r,"REQUIRED_PATHS_MISSING")
        return r

def passes_requested_checks(report):
    return (report["integrity_status"]=="MATCH" and
            report["indexed_jsonc_syntax_status"]=="PASS" and
            (report["requirements_profile"] is None or
             report["required_paths_status"]=="REQUIRED_PATHS_PRESENT"))

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle",type=Path,required=True)
    ap.add_argument("--required-profile",type=Path)
    args=ap.parse_args(argv)
    try:
        raw=None if args.required_profile is None else read_regular(args.required_profile,MAX_POLICY)
        r=assess_source(args.bundle,raw)
    except (RequirementsError,AssessmentError,OSError):
        print("INVALID_REQUIRED_SOURCE_PROFILE",file=sys.stderr)
        return 2
    print(json.dumps(r,ensure_ascii=True,allow_nan=False,sort_keys=True))
    return 0 if passes_requested_checks(r) else 2

if __name__=="__main__":
    raise SystemExit(main())
