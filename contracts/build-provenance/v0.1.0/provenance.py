"""EXT-01B.3D restricted offline provenance verifier.

Trusted local Git object store and independently provisioned builder policy.
Never executes producer/build code, downloads, installs or grants authority.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from jsonschema import Draft202012Validator
from referencing import Resource
from securesystemslib.dsse import Envelope
from securesystemslib.signer import SSlibKey
from securesystemslib.exceptions import VerificationError
from proposal import parse, digest, encode_proposal, ProposalError
from wheel_inspection import inspect_wheel, read_archive, InspectionError, SCHEMA_REGISTRY

ROOT=Path(__file__).resolve().parent
SCHEMA=parse((ROOT/"schemas/build-provenance.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
REGISTRY=SCHEMA_REGISTRY.with_resource(SCHEMA["$id"],Resource.from_contents(SCHEMA))
BUILD_TYPE="https://openrgd.org/build-types/pure-python-wheel-review/v0.1-candidate"
STATEMENT_TYPE="https://in-toto.io/Statement/v1"
PREDICATE_TYPE="https://slsa.dev/provenance/v1"
PAYLOAD_TYPE="application/vnd.in-toto+json"
MAX_FILES=128
MAX_FILE=65536
MAX_TOTAL=1048576
HEX40=re.compile(r"[a-f0-9]{40}")
SEGMENT=re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")
INVOCATION=re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")

class ProvenanceError(ValueError):
    """Fixed diagnostic, never a permission."""

def need(ok,code):
    if not ok:raise ProvenanceError(code)

def checked(kind,value):
    v=Draft202012Validator({"$ref":SCHEMA["$id"]+"#/$defs/"+kind},registry=REGISTRY)
    need(v.is_valid(value),"PROVENANCE_SCHEMA")
    return value

def policy_from_bytes(raw):
    try:
        return checked("BuilderPolicy",parse(raw))
    except ProposalError as e:
        raise ProvenanceError("BUILDER_POLICY_INVALID") from e

def git_object_hash(kind,data):
    return hashlib.sha1(kind.encode()+b" "+str(len(data)).encode()+b"\0"+data).hexdigest()

def git_read(repo,*args,limit=65536):
    # Trusted operator-provisioned local FULL object store. No remote URL from
    # submitted metadata; no worktree checkout, hooks, filters or source script.
    # Do not inherit GIT_DIR, GIT_OBJECT_DIRECTORY, config or alternates env.
    env={"PATH":os.defpath,"LANG":"C","GIT_CONFIG_NOSYSTEM":"1",
         "GIT_CONFIG_GLOBAL":os.devnull,"GIT_TERMINAL_PROMPT":"0",
         "GIT_OPTIONAL_LOCKS":"0","GIT_NO_LAZY_FETCH":"1",
         "GIT_ALLOW_PROTOCOL":"","GIT_CONFIG_COUNT":"0"}
    try:
        # Output is spooled to private files (no unbounded RAM capture); trusted
        # repository and command timeout are assumptions, not hostile disk quota.
        with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
            result=subprocess.run(["git","--no-replace-objects","-C",str(repo),*args],
                    env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=15,check=False)
            need(result.returncode==0,"GIT_OBJECT_UNAVAILABLE")
            out.seek(0);raw=out.read(limit+1)
            need(len(raw)<=limit,"GIT_OUTPUT_LIMIT")
            return raw
    except (OSError,subprocess.TimeoutExpired) as e:
        raise ProvenanceError("GIT_READ_FAILED") from e

def safe_path(name):
    return (isinstance(name,str) and len(name)<=240 and
            all(SEGMENT.fullmatch(p) and not p.endswith(".")
                and p.split(".")[0].casefold() not in
                {"con","prn","aux","nul",*(f"com{i}" for i in range(1,10)),*(f"lpt{i}" for i in range(1,10))}
                for p in name.split("/")))

def source_inventory(repo,commit,package_root):
    """Read exact commit tree's regular blobs; return bytes and SHA256 inventory.

    No claim of remote ownership or actual build execution. Local repository
    identity is a trusted external mapping; caller policy pins SHA256 inventory.
    """
    repo=Path(repo).absolute()
    need(repo.is_dir() and not repo.is_symlink(),"TRUSTED_LOCAL_REPOSITORY_REQUIRED")
    need(isinstance(commit,str) and HEX40.fullmatch(commit),"COMMIT_ID_REQUIRED")
    need(isinstance(package_root,str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,99}",package_root),
         "PACKAGE_ROOT_INVALID")
    need(git_read(repo,"rev-parse","--show-object-format")==b"sha1\n","UNSUPPORTED_GIT_OBJECT_FORMAT")
    need(git_read(repo,"cat-file","-t",commit)==b"commit\n","COMMIT_OBJECT_REQUIRED")
    raw=git_read(repo,"cat-file","commit",commit)
    need(git_object_hash("commit",raw)==commit,"COMMIT_OBJECT_MISMATCH")
    listing=git_read(repo,"ls-tree","-r","-z","--full-tree",commit,limit=65536)
    need(listing.endswith(b"\0"),"GIT_TREE_INVALID")
    rows=listing[:-1].split(b"\0")
    need(2<=len(rows)<=MAX_FILES,"SOURCE_ENTRY_LIMIT")
    files={};seen=set();total=0
    try:
        for item in rows:
            meta,name=item.split(b"\t",1)
            mode,kind,oid=meta.decode("ascii").split(" ")
            path=name.decode("ascii")
            need(mode=="100644" and kind=="blob" and HEX40.fullmatch(oid),"UNSUPPORTED_GIT_ENTRY")
            need(safe_path(path) and path.casefold() not in seen,"SOURCE_PATH_INVALID")
            need(path=="pyproject.toml" or path.startswith(package_root+"/"),"SOURCE_LAYOUT_UNSUPPORTED")
            seen.add(path.casefold())
            size=git_read(repo,"cat-file","-s",oid,limit=32)
            need(re.fullmatch(rb"[0-9]+\n",size) is not None,"GIT_BLOB_SIZE_INVALID")
            n=int(size)
            need(n<=MAX_FILE and total+n<=MAX_TOTAL,"SOURCE_BYTES_LIMIT")
            data=git_read(repo,"cat-file","blob",oid,limit=MAX_FILE)
            need(len(data)==n and git_object_hash("blob",data)==oid,"GIT_BLOB_MISMATCH")
            files[path]=data;total+=n
    except (UnicodeError,ValueError) as e:
        if isinstance(e,ProvenanceError):raise
        raise ProvenanceError("GIT_TREE_INVALID") from e
    need("pyproject.toml" in files and package_root+"/__init__.py" in files,
         "SOURCE_LAYOUT_UNSUPPORTED")
    entries=[{"path":path,"sha256":digest(files[path]),"size_bytes":len(files[path])}
             for path in sorted(files)]
    return files,entries,digest(encode_proposal(entries))

def expected_statement(policy,filename,artifact_sha256,invocation_id):
    """BuildType-specific expected parameters and materials, not a signer."""
    uri="git+"+policy["repository_uri"]+"@"+policy["git_commit"]
    return {"_type":STATEMENT_TYPE,
            "subject":[{"name":filename,"digest":{"sha256":artifact_sha256.removeprefix("sha256:")}}],
            "predicateType":PREDICATE_TYPE,
            "predicate":{"buildDefinition":{
                "buildType":BUILD_TYPE,
                "externalParameters":{"repository":policy["repository_uri"],"commit":policy["git_commit"],
                                      "packageRoot":policy["package_root"]},
                "internalParameters":{},
                "resolvedDependencies":[{"uri":uri,"digest":{"gitCommit":policy["git_commit"],
                        "sha256":policy["source_tree_sha256"].removeprefix("sha256:")}},
                    {"uri":uri+"#pyproject.toml","digest":{"sha256":policy["recipe_sha256"].removeprefix("sha256:")}}]},
                "runDetails":{"builder":{"id":policy["builder_id"]},"metadata":{"invocationId":invocation_id}}}}

def verify_envelope(raw,policy):
    try:
        env=parse(raw)
        need(type(env) is dict and set(env)=={"payloadType","payload","signatures"} and
             env["payloadType"]==PAYLOAD_TYPE,"DSSE_ENVELOPE_PROFILE")
        sigs=env["signatures"]
        need(type(sigs) is list and len(sigs)==1 and type(sigs[0]) is dict and
             set(sigs[0])=={"keyid","sig"} and sigs[0]["keyid"]==policy["builder_keyid"],
             "BUILDER_SIGNATURE_PROFILE")
        for value,size in ((env["payload"],49152),(sigs[0]["sig"],64)):
            need(type(value) is str,"DSSE_BASE64_INVALID")
            decoded=base64.b64decode(value,validate=True)
            need(0<len(decoded)<=size and base64.b64encode(decoded).decode()==value,"DSSE_BASE64_INVALID")
        need(len(base64.b64decode(sigs[0]["sig"]))==64,"BUILDER_SIGNATURE_PROFILE")
        key=SSlibKey.from_dict(policy["builder_keyid"],{"keytype":"ed25519","scheme":"ed25519",
                                  "keyval":{"public":policy["builder_public_key"]}})
        envelope=Envelope.from_dict(deepcopy(env))
        envelope.verify([key],1)
        return parse(envelope.payload),envelope.payload
    except ProvenanceError:
        raise
    except (ProposalError,VerificationError,ValueError,TypeError,KeyError) as e:
        raise ProvenanceError("BUILDER_ATTESTATION_REJECTED") from e

def verify_provenance(*,manifest_raw,descriptor_bytes,artifact_bytes,source_claim,
                      submitted_proposal_raw,filename,attestation_raw,policy_raw,local_repository):
    p=policy_from_bytes(policy_raw)
    try:
        inspection=inspect_wheel(manifest_raw,descriptor_bytes,artifact_bytes,source_claim,
                                 submitted_proposal_raw,filename)
        src=parse(source_claim)
        need(src=={"repository_uri":p["repository_uri"],"git_commit":p["git_commit"]},
             "SOURCE_POLICY_MISMATCH")
        need(all(inspection[k]==p[k] for k in ("module_id","module_version")),"RELEASE_POLICY_MISMATCH")
    except (ProposalError,InspectionError) as e:
        raise ProvenanceError("PROPOSAL_OR_WHEEL_REJECTED") from e
    statement,payload=verify_envelope(attestation_raw,p)
    try:
        invocation=statement["predicate"]["runDetails"]["metadata"]["invocationId"]
        need(type(invocation) is str and INVOCATION.fullmatch(invocation),"INVOCATION_ID_INVALID")
        need(statement==expected_statement(p,filename,inspection["artifact_sha256"],invocation),
             "ATTESTATION_BINDING_MISMATCH")
    except (KeyError,TypeError) as e:
        raise ProvenanceError("ATTESTATION_BINDING_MISMATCH") from e
    files,entries,tree_sha=source_inventory(local_repository,p["git_commit"],p["package_root"])
    need(tree_sha==p["source_tree_sha256"],"SOURCE_INVENTORY_MISMATCH")
    need(digest(files["pyproject.toml"])==p["recipe_sha256"],"BUILD_RECIPE_MISMATCH")
    prefix=p["package_root"]+"/"
    need(files.get(prefix+"module.openrgd.json")==manifest_raw,"COMMITTED_MANIFEST_MISMATCH")
    for path,raw in descriptor_bytes.items():
        need(files.get(prefix+path)==raw,"COMMITTED_DESCRIPTOR_MISMATCH")
    # Existing wheel verifier validates the restricted format and metadata.
    # This extra check verifies actual package contents, not just its manifest.
    wheel=read_archive(artifact_bytes[inspection["slot_id"]])
    source_package={path:raw for path,raw in files.items() if path.startswith(prefix)}
    wheel_package={path:raw for path,raw in wheel.items() if path.startswith(prefix)}
    need(wheel_package==source_package,"WHEEL_COMMITTED_PACKAGE_MISMATCH")
    return checked("ProvenanceReview",{
        "schema_version":"openrgd.build-provenance-review.v0.1-candidate",
        "module_id":p["module_id"],"module_version":p["module_version"],
        "policy_sha256":digest(policy_raw),"proposal_sha256":digest(submitted_proposal_raw),
        "attestation_sha256":digest(attestation_raw),"statement_sha256":digest(payload),
        "inspection_sha256":digest(encode_proposal(inspection)),
        "repository_uri":p["repository_uri"],"git_commit":p["git_commit"],
        "source_tree_sha256":tree_sha,"recipe_sha256":p["recipe_sha256"],
        "artifact_filename":filename,"artifact_sha256":inspection["artifact_sha256"],
        "builder_id":p["builder_id"],"builder_public_key_sha256":digest(bytes.fromhex(p["builder_public_key"])),
        "source_entries":entries,"source_commit_membership_verified":True,"builder_signature_verified":True,
        "builder_policy_matched":True,"wheel_package_bytes_matched":True,
        "build_execution_independently_verified":False,"dependency_materials_complete":False,
        "reproducible_build_verified":False,"slsa_level_verified":False,"publisher_verified":False,
        "publication_committed":False,"installable":False,"grants_authority":False})
