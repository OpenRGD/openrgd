"""EXT-01B.4 shared candidate catalog consumer contract.

No signature verification here: authenticate catalog bytes externally before
use. No DB, Git, provider code, installation, publication, or authority.
"""
from __future__ import annotations
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Resource
from proposal import parse,digest,encode_proposal,validate,PUB,ProposalError
from ledger_contract import SCHEMA as LEDGER_SCHEMA, SCHEMA_REGISTRY as LEDGER_REGISTRY

ROOT=Path(__file__).resolve().parent
SCHEMA=parse((ROOT/"schemas/release-admission.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
REGISTRY=LEDGER_REGISTRY.with_resource(SCHEMA["$id"],Resource.from_contents(SCHEMA))

class AdmissionError(ValueError):
    """Fixed candidate rejection, not authorization."""

def need(ok,code):
    if not ok:raise AdmissionError(code)

def checked(kind,value):
    v=Draft202012Validator({"$ref":SCHEMA["$id"]+"#/$defs/"+kind},registry=REGISTRY)
    need(v.is_valid(value),"ADMISSION_SHAPE")
    return value

def key(value):
    return value["module_id"],value["module_version"]

def validate_catalog(raw,catalog_id,ledger_id):
    """Shape + consistency only; raw must be authenticated separately."""
    try:c=checked("CatalogPreview",parse(raw))
    except ProposalError as e:raise AdmissionError("CATALOG_JSON") from e
    need((c["catalog_id"],c["ledger_id"])==(catalog_id,ledger_id),"CATALOG_SCOPE_MISMATCH")
    cp=c["checkpoint"]
    need((cp["catalog_id"],cp["ledger_id"])==(catalog_id,ledger_id),"CHECKPOINT_SCOPE_MISMATCH")
    keys=[key(e["admission"]) for e in c["entries"]]
    need(keys==sorted(set(keys)),"CATALOG_KEYS_INVALID")
    sequences=set()
    for entry in c["entries"]:
        a=entry["admission"]
        need((a["catalog_id"],a["ledger_id"])==(catalog_id,ledger_id),"ENTRY_SCOPE_MISMATCH")
        rs=a["reservation_event_sequence"];es=entry["state_event_sequence"];rev=entry["release_revision"]
        need(rs<=es<=cp["event_sequence"],"ENTRY_CHECKPOINT_MISMATCH")
        need(rs not in sequences and (rs==es or es not in sequences),"EVENT_SEQUENCE_COLLISION")
        sequences.update((rs,es))
        state=entry["state"]
        if state=="RESERVED_CANDIDATE":
            need(rev==1 and es==rs and entry["state_receipt_sha256"]==a["reservation_receipt_sha256"],
                 "RESERVATION_STATE_MISMATCH")
        else:
            need(es>rs and rev in ((2,) if state=="WITHDRAWN" else (2,3)),
                 "DISPOSITION_STATE_MISMATCH")
        if es==cp["event_sequence"]:
            need(entry["state_receipt_sha256"]==cp["event_sha256"],"CHECKPOINT_HEAD_MISMATCH")
        deps=a["dependencies"]
        need(len({x["module_id"] for x in deps})==len(deps) and all(x["module_id"]!=a["module_id"] for x in deps),
             "DEPENDENCY_DECLARATION_CONFLICT")
    # Dedicated full preview: each reservation/control event is represented
    # by its latest revision, even when intermediate receipts are not included.
    need(sum(e["release_revision"] for e in c["entries"])==cp["event_sequence"],
         "CATALOG_EVENT_COVERAGE_MISMATCH")
    return c

def check_successor(prior,current):
    """Retained authenticated view monotonicity, NOT ledger-chain verification."""
    need((prior["catalog_id"],prior["ledger_id"])==(current["catalog_id"],current["ledger_id"]),
         "CATALOG_SCOPE_MISMATCH")
    a,b=prior["checkpoint"],current["checkpoint"]
    need(a["legacy_catalog_sha256"]==b["legacy_catalog_sha256"],"LEGACY_BASELINE_CHANGED")
    need(b["event_sequence"]>=a["event_sequence"],"CATALOG_CHECKPOINT_ROLLBACK")
    if b["event_sequence"]==a["event_sequence"]:
        need(prior==current,"CATALOG_SAME_CHECKPOINT_CONFLICT")
    old={key(e["admission"]):e for e in prior["entries"]}
    new={key(e["admission"]):e for e in current["entries"]}
    need(set(old)<=set(new),"CATALOG_ENTRY_DISAPPEARED")
    for k in set(new)-set(old):
        need(new[k]["admission"]["reservation_event_sequence"]>a["event_sequence"],
             "CATALOG_BACKDATED_ENTRY")
    for k,p in old.items():
        q=new[k]
        need(p["admission"]==q["admission"],"IMMUTABLE_ADMISSION_CONFLICT")
        if p==q:continue
        need(q["release_revision"]>p["release_revision"] and q["state_event_sequence"]>p["state_event_sequence"],
             "CATALOG_DISPOSITION_ROLLBACK")
        allowed={"RESERVED_CANDIDATE":{"WITHDRAWN","REVOKED"},"WITHDRAWN":{"REVOKED"},"REVOKED":set()}
        need(q["state"] in allowed[p["state"]],"CATALOG_TERMINAL_STATE")
        need(q["state_event_sequence"]>a["event_sequence"],"CATALOG_BACKDATED_DISPOSITION")
    return current

def select_preview(catalog,module_id,module_version):
    """Exact preview key only, no resolution, fallback or install action."""
    for e in catalog["entries"]:
        if key(e["admission"])==(module_id,module_version):
            need(e["state"]=="RESERVED_CANDIDATE","RELEASE_NOT_SELECTABLE")
            return e["admission"]
    raise AdmissionError("RELEASE_NOT_FOUND")

def verify_preview_artifact(admission,raw):
    checked("AdmissionRecord",admission)
    a=admission["artifact"]
    need(type(raw) is bytes and len(raw)==a["size_bytes"] and digest(raw)==a["sha256"],
         "ARTIFACT_BYTES_MISMATCH")
    return {"artifact_sha256":a["sha256"],"bytes_match":True,"installable":False,"grants_authority":False}
