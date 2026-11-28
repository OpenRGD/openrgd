"""Registry-side projection of trusted, audited candidate reservation evidence."""
from catalog_contract import checked, need, key, AdmissionError
from proposal import parse,digest,encode_proposal,validate,PUB
from ledger_contract import decode
from provenance import checked as prov_checked
from wheel_inspection import check_shape

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

