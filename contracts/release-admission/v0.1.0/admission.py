"""EXT-01B.4 shared candidate catalog projection / consumer contract.

No signature verification here: authenticate catalog bytes externally before
use. No DB, Git, provider code, installation, publication, or authority.
"""
from __future__ import annotations
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Resource
from proposal import parse,digest,encode_proposal,validate,PUB,ProposalError
from ledger_contract import SCHEMA as LEDGER_SCHEMA, decode
from provenance import REGISTRY as PROV_REGISTRY, SCHEMA as PROV_SCHEMA, checked as prov_checked
from wheel_inspection import check_shape

ROOT=Path(__file__).resolve().parent
SCHEMA=parse((ROOT/"schemas/release-admission.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
REGISTRY=PROV_REGISTRY.with_resources((s["$id"],Resource.from_contents(s)) for s in (LEDGER_SCHEMA,SCHEMA))

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

def project_admission(*,manifest_raw,proposal_raw,review_raw,receipt_raw,authority_raw):
    """Bind existing evidence bytes from a TRUSTED ledger/writer.

    Not an authenticator of an arbitrary context. The registry must select its
    own audited ledger and separately authorize/sign the catalog projection.
    """
    try:
        m,p,c,review=(parse(x) for x in (manifest_raw,proposal_raw,authority_raw,review_raw))
        validate(PUB+"#/$defs/ModuleManifest",m,"MANIFEST_SHAPE")
        validate(PUB+"#/$defs/ReleaseProposal",p,"PROPOSAL_SHAPE")
        check_shape("RegistryReviewTarget",review)
        receipt=decode("ReleaseLedgerReceipt",receipt_raw)
        need(receipt["operation"]=="RESERVE_CANDIDATE" and receipt["state_after"]=="RESERVED_CANDIDATE",
             "NOT_RESERVATION_RECEIPT")
        need(key(m)==key(p)==key(receipt)==key(review),"RELEASE_KEY_MISMATCH")
        need(p["manifest_sha256"]==digest(manifest_raw),"MANIFEST_COMMITMENT_MISMATCH")
        need(receipt["proposal_sha256"]==review["proposal_sha256"]==digest(proposal_raw)
             and receipt["evidence_sha256"]==digest(review_raw)
             and receipt["authority_context_sha256"]==digest(authority_raw),"RECEIPT_COMMITMENT_MISMATCH")
        need(review["disposition"]=="REVIEWED_CANDIDATE" and m["module_id"].startswith(review["publisher_namespace"]+"."),
             "REVIEW_TARGET_MISMATCH")
        need(c["profile"]=="TUF_AND_BUILD_PROVENANCE_REVIEW_CANDIDATE"
             and c["builder_key_separation_verified"] is True,"PROVENANCE_CONTEXT_REQUIRED")
        need(c["request_sha256"]==receipt["request_sha256"] and
             c["review_target_sha256"]==digest(review_raw),"CONTEXT_BINDING_MISMATCH")
        for k in ("publication_committed","installable","grants_authority"):
            need(c[k] is False,"CONTEXT_AUTHORITY_MISMATCH")
        tuf=c["tuf_review_context"]
        need(tuf["profile"]=="TUF_OFFLINE_REVIEW_CANDIDATE"
             and tuf["request_sha256"]==receipt["request_sha256"]
             and tuf["review_target_sha256"]==digest(review_raw),"TUF_CONTEXT_MISMATCH")
        prov=prov_checked("ProvenanceReview",c["provenance_review"])
        need(key(prov)==key(p) and prov["proposal_sha256"]==digest(proposal_raw)
             and prov["inspection_sha256"]==review["inspection_sha256"]
             and prov["policy_sha256"]==c["builder_policy_sha256"]
             and prov["attestation_sha256"]==c["attestation_sha256"]
             and c["provenance_review_sha256"]==digest(encode_proposal(prov))
             and {k:prov[k] for k in ("repository_uri","git_commit")}==p["source_claim"],
             "PROVENANCE_BINDING_MISMATCH")
        need(len(m["artifact_slots"])==len(p["artifact_commitments"])==1,"UNSUPPORTED_ADMISSION_PROFILE")
        slot=m["artifact_slots"][0];art=p["artifact_commitments"][0]
        need(slot["slot_id"]==art["slot_id"] and art["sha256"]==prov["artifact_sha256"],
             "ARTIFACT_BINDING_MISMATCH")
        deps=m["dependencies"]
        need(len({x["module_id"] for x in deps})==len(deps) and
             all(x["module_id"]!=m["module_id"] for x in deps),"DEPENDENCY_DECLARATION_CONFLICT")
        return checked("AdmissionRecord",{
            "schema_version":"openrgd.release-admission-preview.v0.1-candidate",
            "catalog_id":receipt["catalog_id"],"ledger_id":receipt["ledger_id"],
            "module_id":m["module_id"],"module_version":m["module_version"],
            "admission_profile":"VERIFIED_WHEEL_REVIEW_PREVIEW",
            "proposal_sha256":digest(proposal_raw),"manifest_sha256":digest(manifest_raw),
            "registry_review_sha256":digest(review_raw),"reservation_receipt_sha256":digest(receipt_raw),
            "authority_context_sha256":digest(authority_raw),"provenance_review_sha256":c["provenance_review_sha256"],
            "builder_policy_sha256":c["builder_policy_sha256"],"attestation_sha256":c["attestation_sha256"],
            "inspection_sha256":review["inspection_sha256"],"display_name":m["display_name"],
            "functional_roles":m["functional_roles"],"dependencies":deps,
            "artifact":{"slot_id":art["slot_id"],"artifact_kind":slot["artifact_kind"],
                        "platform_profile":slot["platform_profile"],"media_type":slot["media_type"],
                        "filename":prov["artifact_filename"],"sha256":art["sha256"],"size_bytes":art["size_bytes"]},
            "reservation_event_sequence":receipt["event_sequence"],"dependency_resolution_verified":False,
            "host_compatibility_verified":False,"runtime_evaluated":False,"publication_committed":False,
            "installable":False,"grants_authority":False})
    except AdmissionError:raise
    except (ValueError,TypeError,KeyError,IndexError) as e:
        raise AdmissionError("ADMISSION_EVIDENCE_REJECTED") from e

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
    for k,p in old.items():
        q=new[k]
        need(p["admission"]==q["admission"],"IMMUTABLE_ADMISSION_CONFLICT")
        if p==q:continue
        need(q["release_revision"]>p["release_revision"] and q["state_event_sequence"]>p["state_event_sequence"],
             "CATALOG_DISPOSITION_ROLLBACK")
        allowed={"RESERVED_CANDIDATE":{"WITHDRAWN","REVOKED"},"WITHDRAWN":{"REVOKED"},"REVOKED":set()}
        need(q["state"] in allowed[p["state"]],"CATALOG_TERMINAL_STATE")
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
