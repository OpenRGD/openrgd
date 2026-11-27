"""Shared EXT-01B.3C schema and transition rules. No database or authority."""
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Resource
from proposal import parse, digest, encode_proposal, ProposalError, PUB, REGISTRY, validate

ROOT=Path(__file__).resolve().parent
SCHEMA=parse((ROOT/"schemas/release-ledger.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
SCHEMA_REGISTRY=REGISTRY.with_resource(SCHEMA["$id"],Resource.from_contents(SCHEMA))

class LedgerContractError(ValueError):
    """Candidate contract rejection."""

def checked(kind, value):
    validator=Draft202012Validator({"$ref":SCHEMA["$id"]+"#/$defs/"+kind},registry=SCHEMA_REGISTRY)
    if not validator.is_valid(value):
        raise LedgerContractError("LEDGER_SHAPE")
    return value

def decode(kind, raw):
    try:
        return checked(kind,parse(raw))
    except ProposalError as e:
        raise LedgerContractError("LEDGER_JSON") from e

def transition(request, prior):
    """Return revision/state from a validated request and last receipt (or None).

    This is only a state machine; the owner must compare content, verify
    authority, enforce uniqueness and commit atomically.
    """
    checked("ReleaseLedgerRequest",request)
    op=request["operation"]
    if prior is None:
        if op!="RESERVE_CANDIDATE":
            raise LedgerContractError("RELEASE_UNKNOWN")
        return 1,"RESERVED_CANDIDATE"
    checked("ReleaseLedgerReceipt",prior)
    if any(prior[k]!=request[k] for k in ("catalog_id","ledger_id","module_id","module_version")):
        raise LedgerContractError("RELEASE_SCOPE_MISMATCH")
    if prior["proposal_sha256"]!=request["proposal_sha256"]:
        raise LedgerContractError("RELEASE_KEY_CONTENT_CONFLICT")
    if op=="RESERVE_CANDIDATE":
        raise LedgerContractError("RELEASE_ALREADY_RESERVED")
    if prior["release_revision"]!=request["expected_revision"]:
        raise LedgerContractError("STALE_RELEASE_REVISION")
    if prior["state_after"]=="REVOKED" or (prior["state_after"]=="WITHDRAWN" and op!="REVOKE"):
        raise LedgerContractError("TERMINAL_RELEASE_STATE")
    return prior["release_revision"]+1,{"WITHDRAW":"WITHDRAWN","REVOKE":"REVOKED"}[op]

def validate_evidence(request,proposal_raw,evidence_raw):
    """Shape and exact bytes only; NOT authentication."""
    try:
        p=parse(proposal_raw)
        validate(PUB+"#/$defs/ReleaseProposal",p,"PROPOSAL_SHAPE")
        evidence=parse(evidence_raw)
    except ProposalError as e:
        raise LedgerContractError("LEDGER_EVIDENCE_INVALID") from e
    if digest(proposal_raw)!=request["proposal_sha256"] or digest(evidence_raw)!=request["evidence_sha256"]:
        raise LedgerContractError("LEDGER_COMMITMENT_MISMATCH")
    if any(p[k]!=request[k] for k in ("module_id","module_version")):
        raise LedgerContractError("PROPOSAL_KEY_MISMATCH")
    if request["operation"]=="RESERVE_CANDIDATE":
        # Reuse the previous trust target schema through the actual wheel
        # inspection package. No duplicate review schema or trust inference.
        from wheel_inspection import check_shape, InspectionError
        try:
            check_shape("RegistryReviewTarget",evidence)
        except InspectionError as e:
            raise LedgerContractError("REVIEW_TARGET_SHAPE") from e
        if (evidence["disposition"]!="REVIEWED_CANDIDATE" or
            any(evidence[k]!=request[k] for k in ("module_id","module_version","proposal_sha256")) or
            not request["module_id"].startswith(evidence["publisher_namespace"]+".")):
            raise LedgerContractError("REVIEW_TARGET_BINDING_MISMATCH")
    else:
        checked("ReleaseDispositionNotice",evidence)
        for k in ("catalog_id","ledger_id","module_id","module_version","request_id",
                  "operation","expected_revision","proposal_sha256","reason_code"):
            if evidence[k]!=request[k]:
                raise LedgerContractError("DISPOSITION_NOTICE_BINDING_MISMATCH")
    return evidence

def make_receipt(request, request_raw, authority_raw, seq, previous, prior):
    rev,state=transition(request,prior)
    if type(authority_raw) is not bytes or not authority_raw or len(authority_raw)>65536:
        raise LedgerContractError("AUTHORITY_CONTEXT_LIMIT")
    result={k:request[k] for k in ("catalog_id","ledger_id","module_id","module_version",
        "request_id","operation","reason_code","proposal_sha256","evidence_sha256")}
    result.update(schema_version="openrgd.release-ledger-receipt.v0.1-candidate",
                  request_sha256=digest(request_raw),authority_context_sha256=digest(authority_raw),
                  event_sequence=seq,previous_event_sha256=previous,
                  release_revision=rev,state_after=state,
                  committed_to_candidate_ledger=True,publication_committed=False,
                  installable=False,grants_authority=False)
    return checked("ReleaseLedgerReceipt",result)
