"""EXT-01B offline publication proposal; NO install, import, registry mutation or grants.

The caller supplies bytes. Paths are keys, not filesystem or network locators.
Legacy descriptor validation here is SHAPE ONLY; the recovered full static
validator and actual artifact/publisher verification remain independent gates.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re
from pathlib import Path
from typing import Mapping
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

ROOT = Path(__file__).resolve().parent
HIST = ROOT.parents[2] / "docs/history/extension-architecture/somatic-alignment-review/contracts"
VOCAB = ROOT.parent.parent / "module-vocabulary/v0.1.0/schemas/module-vocabulary.schema.json"
MAX_METADATA = 65536
MAX_ARTIFACT = 1048576
MAX_TOTAL = 4194304
MAX_NODES = 10000
MAX_DEPTH = 32

class ProposalError(ValueError):
    """Fixed diagnostic code; never an approval."""

def digest(raw):
    return "sha256:" + sha256(raw).hexdigest()

def pairs(items):
    result = {}
    for k, v in items:
        if k in result:
            raise ProposalError("DUPLICATE_JSON_KEY")
        result[k] = v
    return result

def no_number(_):
    raise ProposalError("NON_INTEGER_NUMBER")

def bounded_int(s):
    if len(s) > 16:
        raise ProposalError("NUMBER_LIMIT")
    return int(s)

def parse(raw):
    if type(raw) is not bytes or len(raw) > MAX_METADATA:
        raise ProposalError("METADATA_BYTES_LIMIT")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=no_number, parse_float=no_number,
                           parse_int=bounded_int)
        n, stack = 0, [(value, 0)]
        while stack:
            v, depth = stack.pop()
            n += 1
            if n > MAX_NODES or depth > MAX_DEPTH:
                raise ProposalError("STRUCTURE_LIMIT")
            if isinstance(v, dict):
                stack.extend((x, depth+1) for x in v.values())
            elif isinstance(v, list):
                stack.extend((x, depth+1) for x in v)
            elif isinstance(v, str):
                v.encode("utf-8")  # reject unpaired surrogate escapes
        return value
    except ProposalError:
        raise
    except (ValueError, RecursionError, UnicodeError):
        raise ProposalError("INVALID_JSON") from None

def no_retrieval(uri):
    raise NoSuchResource(ref=uri)

SCHEMAS = [ROOT/"schemas/module-publication.schema.json", VOCAB,
           HIST/"extensions/v0.1.0/schemas/extension-manifest.schema.json",
           HIST/"extensions/v0.1.0/schemas/composition.schema.json",
           HIST/"command-plugin/v0.1.0/schemas/command-plugin.schema.json"]
DOCS = [parse(p.read_bytes()) for p in SCHEMAS]
for doc in DOCS:
    Draft202012Validator.check_schema(doc)
REGISTRY = Registry(retrieve=no_retrieval).with_resources(
    (doc["$id"], Resource.from_contents(doc)) for doc in DOCS)
PUB = DOCS[0]["$id"]
EXT = DOCS[2]["$id"]
CLI = DOCS[4]["$id"]

def validate(selector, value, code):
    v = Draft202012Validator({"$ref": selector}, registry=REGISTRY)
    if not v.is_valid(value):
        raise ProposalError(code)

def plain_bytes_map(value, max_entries, limit):
    if type(value) is not dict or len(value) > max_entries:
        raise ProposalError("INPUT_SET_LIMIT")
    total = 0
    for k, b in value.items():
        if type(k) is not str or type(b) is not bytes or not b or len(b) > limit:
            raise ProposalError("INPUT_BYTES_LIMIT")
        total += len(b)
        if total > MAX_TOTAL:
            raise ProposalError("TOTAL_BYTES_LIMIT")
    return value

def safe_path(path):
    # No filesystem lookup. Reject aliases and platform-specific paths.
    if any(s in ("", ".", "..") for s in path.split("/")) or "\\" in path:
        raise ProposalError("UNSAFE_DESCRIPTOR_PATH")

def inspect_manifest(manifest_raw: bytes, descriptor_bytes: dict[str, bytes]):
    """Return parsed declarations after bounded shape and linkage checks."""
    m = parse(manifest_raw)
    validate(PUB+"#/$defs/ModuleManifest", m, "MANIFEST_SHAPE")
    supplied = plain_bytes_map(descriptor_bytes, 64, MAX_METADATA)
    declared = list(m["extension_descriptors"]) + [x["descriptor"] for x in m["command_facades"]]
    paths = [r["path"] for r in declared]
    if len(paths) != len(set(paths)) or set(paths) != set(supplied):
        raise ProposalError("DESCRIPTOR_SET_MISMATCH")
    for ref in declared:
        path = ref["path"]
        safe_path(path)
        if digest(supplied[path]) != ref["sha256"]:
            raise ProposalError("DESCRIPTOR_DIGEST_MISMATCH")
    exts, identities = {}, set()
    for ref in m["extension_descriptors"]:
        path = ref["path"]
        ext = parse(supplied[path])
        validate(EXT, ext, "EXTENSION_SHAPE")
        identity = (ext["extension_id"], ext["extension_version"])
        if identity in identities:
            raise ProposalError("DUPLICATE_EXTENSION_IDENTITY")
        identities.add(identity)
        exts[path] = ext
    slots = {}
    covered = set()
    for slot in m["artifact_slots"]:
        sid = slot["slot_id"]
        if sid in slots:
            raise ProposalError("DUPLICATE_ARTIFACT_SLOT")
        slots[sid] = slot
        for path in slot["extension_descriptor_paths"]:
            if path not in exts:
                raise ProposalError("UNKNOWN_EXTENSION_BINDING")
            covered.add(path)
    if covered != set(exts):
        raise ProposalError("UNBOUND_EXTENSION")
    seen_namespaces, seen_entries, facades = set(), set(), set()
    for binding in m["command_facades"]:
        path, sid = binding["extension_descriptor_path"], binding["artifact_slot_id"]
        facade = parse(supplied[binding["descriptor"]["path"]])
        validate(CLI, facade, "CLI_DESCRIPTOR_SHAPE")
        ext, slot = exts.get(path), slots.get(sid)
        if not ext or not slot or path not in slot["extension_descriptor_paths"]:
            raise ProposalError("CLI_BINDING_MISMATCH")
        if ((facade["extension_id"], facade["extension_version"]) !=
            (ext["extension_id"], ext["extension_version"]) or
            facade["cli"] != ext.get("cli")):
            raise ProposalError("CLI_EXTENSION_MISMATCH")
        if (slot["artifact_kind"] != "python_wheel" or
            facade["distribution"] != {"name":slot["package_name"], "version":slot["package_version"]} or
            ext["implementation"]["kind"] != "python_package" or
            ext["implementation"]["name"] != slot["package_name"] or
            ext["implementation"]["version"] != slot["package_version"]):
            raise ProposalError("CLI_ARTIFACT_MISMATCH")
        ns, entry = facade["cli"]["namespace"], facade["cli"]["entry_point_name"]
        if path in facades or ns in seen_namespaces or entry in seen_entries:
            raise ProposalError("CLI_DUPLICATE_BINDING")
        facades.add(path); seen_namespaces.add(ns); seen_entries.add(entry)
    if facades != {p for p,x in exts.items() if "cli" in x}:
        raise ProposalError("CLI_FACADE_SET_MISMATCH")
    deps = [(d["module_id"], d["module_version"]) for d in m["dependencies"]]
    if len({d[0] for d in deps}) != len(deps) or any(d[0]==m["module_id"] for d in deps):
        raise ProposalError("DEPENDENCY_DECLARATION_CONFLICT")
    # No semantic/authority validation of old manifests or graph resolution
    # performed here. No import/attach, package parser or source fetch.
    return m

def propose(manifest_raw, descriptor_bytes, artifact_bytes, source_claim):
    """Commit exact supplied bytes, NOT Git provenance or artifact correctness."""
    m = inspect_manifest(manifest_raw, descriptor_bytes)
    supplied = plain_bytes_map(artifact_bytes, 32, MAX_ARTIFACT)
    expected = {s["slot_id"] for s in m["artifact_slots"]}
    if expected != set(supplied):
        raise ProposalError("ARTIFACT_SET_MISMATCH")
    # Source claim is parsed from bytes like all other external input.
    source = parse(source_claim)
    validate(PUB+"#/$defs/SourceClaim", source, "SOURCE_CLAIM_SHAPE")
    result = {
        "schema_version":"openrgd.module-release-proposal.v0.1-candidate",
        "module_id":m["module_id"], "module_version":m["module_version"],
        "manifest_sha256":digest(manifest_raw), "source_claim":source,
        "artifact_commitments":[{"slot_id":s,"sha256":digest(supplied[s]),"size_bytes":len(supplied[s])}
                                for s in sorted(supplied)],
        "publication_status":"review_required", "publisher_verified":False,
        "source_commit_verified":False, "artifact_format_verified":False,
        "installable":False, "grants_authority":False,
    }
    validate(PUB+"#/$defs/ReleaseProposal",result,"PROPOSAL_SHAPE")
    return result

def compare_same_key(existing_raw, candidate_raw):
    """Offline conflict characterization, not a trusted registry transaction."""
    a,b=parse(existing_raw),parse(candidate_raw)
    for v in (a,b):
        validate(PUB+"#/$defs/ReleaseProposal",v,"PROPOSAL_SHAPE")
        ids=[x["slot_id"] for x in v["artifact_commitments"]]
        if len(ids)!=len(set(ids)) or ids!=sorted(ids):
            raise ProposalError("NONCANONICAL_COMMITMENT_SET")
    if (a["module_id"],a["module_version"]) != (b["module_id"],b["module_version"]):
        return "DISTINCT_RELEASE_KEY"
    if a != b:
        raise ProposalError("RELEASE_KEY_CONTENT_CONFLICT")
    return "SAME_PROPOSAL"

def encode_proposal(proposal):
    """Deterministic local serialization; NOT a signing or canonical JCS profile."""
    return (json.dumps(proposal,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode("utf-8")
