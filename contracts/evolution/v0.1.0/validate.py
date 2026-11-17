"""OpenRGD EVOL-0.1 candidate: offline shape + local revision-chain conformance.

NOT a maintenance authority, identity/Life issuer, Chronon writer, calibration
authority or robot device driver. Hash comparison means content consistency only.
No keys, signatures, timestamps or robot identity are authenticated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
MAX_BYTES = 131072
MAX_NODES = 5000
MAX_DEPTH = 32
HASH_DOMAIN = b"OPENRGD-EVOL-0.1-CANDIDATE-SORTED-JSON\0"

class ContractError(ValueError):
    """Constant error code only; caller data must not escape to logs."""


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ContractError("DUPLICATE_KEY")
        out[key] = value
    return out


def _reject_constant(_):
    raise ContractError("NONFINITE")


def _bounded_int(raw):
    if len(raw) > 32:
        raise ContractError("NUMBER_LIMIT")
    return int(raw)


def bounded(value):
    seen = set()
    stack = [(value, 0)]
    count = 0
    while stack:
        obj, depth = stack.pop()
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise ContractError("STRUCTURE_LIMIT")
        if isinstance(obj, (dict, list)):
            if id(obj) in seen:
                raise ContractError("SHARED_OR_CYCLIC_VALUE")
            seen.add(id(obj))
            if isinstance(obj, dict):
                if not all(type(k) is str for k in obj):
                    raise ContractError("INVALID_KEY")
                stack.extend((v, depth + 1) for v in obj.values())
            else:
                stack.extend((v, depth + 1) for v in obj)
        elif isinstance(obj, float) and not math.isfinite(obj):
            raise ContractError("NONFINITE")
        elif obj is not None and type(obj) not in (str, int, float, bool):
            raise ContractError("INVALID_VALUE")
    try:
        if len(json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")) > MAX_BYTES:
            raise ContractError("SIZE_LIMIT")
    except ContractError:
        raise
    except (ValueError, OverflowError, RecursionError, UnicodeError):
        raise ContractError("INVALID_JSON_VALUE") from None


def read_json(path):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ContractError("SIZE_LIMIT")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=_bounded_int, parse_constant=_reject_constant)
        bounded(value)
        return value
    except ContractError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise ContractError("JSON_READ_FAILED") from None


SCHEMA = read_json(HERE / "schemas/evolution.schema.json")
Draft202012Validator.check_schema(SCHEMA)
KINDS = ("HardwareMutationEvent", "AsBuiltRevision")
VALIDATORS = {
    kind: Draft202012Validator({
        "$schema": SCHEMA["$schema"], "$defs": SCHEMA["$defs"],
        "$ref": "#/$defs/" + kind
    }) for kind in KINDS
}


def digest(record):
    """TEMPORARY local candidate comparison hash, NOT accepted RGD canonical hash/JCS.

    sorted-key compact UTF-8 JSON excluding only record_digest. The final
    wire canonicalization/signature scheme is an explicit governance blocker.
    """
    value = dict(record)
    value.pop("record_digest", None)
    bounded(value)
    try:
        serialized = json.dumps(value, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError):
        raise ContractError("INVALID_HASH_INPUT") from None
    return "sha256:" + hashlib.sha256(HASH_DOMAIN + serialized).hexdigest()


def physical_slot(slot):
    """Content carrying installed topology, not source-evidence annotation changes."""
    return (
        slot["state"], slot["component_model_ref"], slot["hardware_serial_claim"],
        slot["condition_claim"], tuple(slot["mount_xyz_m"] or []),
        tuple(slot["mount_rpy_rad"] or []),
        tuple(slot["link_refs"]), tuple(slot["joint_refs"]), tuple(slot["sensor_refs"])
    )



def check_change_kind(kind, before, after, affected_sensors):
    """Avoid giving a misleading hardware-change label to a different delta.

    It remains an unauthenticated operator claim, not actual hardware proof.
    Multi-purpose replacements should use OTHER_PHYSICAL_MODIFICATION and
    independent reviewed evidence instead of a false precise single kind.
    """
    before_state = before["state"] if before is not None else None
    if kind == "INSTALL_COMPONENT":
        if before_state == "INSTALLED_REPORTED" or after["state"] != "INSTALLED_REPORTED":
            raise ContractError("CHANGE_KIND_MISMATCH")
    elif kind == "REMOVE_COMPONENT":
        if before_state != "INSTALLED_REPORTED" or after["state"] != "REMOVED_REPORTED":
            raise ContractError("CHANGE_KIND_MISMATCH")
    elif kind == "REPLACE_COMPONENT":
        if before_state != "INSTALLED_REPORTED" or after["state"] != "INSTALLED_REPORTED" or \
           (before["component_model_ref"], before["hardware_serial_claim"]) == \
           (after["component_model_ref"], after["hardware_serial_claim"]):
            raise ContractError("CHANGE_KIND_MISMATCH")
    elif kind == "RELOCATE_SENSOR":
        if before_state != "INSTALLED_REPORTED" or after["state"] != "INSTALLED_REPORTED" or \
           not affected_sensors or \
           (before["component_model_ref"], before["hardware_serial_claim"]) != \
           (after["component_model_ref"], after["hardware_serial_claim"]) or \
           (before["mount_xyz_m"], before["mount_rpy_rad"]) == \
           (after["mount_xyz_m"], after["mount_rpy_rad"]):
            raise ContractError("CHANGE_KIND_MISMATCH")
    elif kind == "REPAIR_COMPONENT":
        if before_state != "INSTALLED_REPORTED" or after["state"] != "INSTALLED_REPORTED" or \
           (before["component_model_ref"], before["hardware_serial_claim"]) != \
           (after["component_model_ref"], after["hardware_serial_claim"]) or \
           before["condition_claim"] == "REPAIRED_REPORTED" or \
           after["condition_claim"] != "REPAIRED_REPORTED":
            raise ContractError("CHANGE_KIND_MISMATCH")
    elif kind == "PERMANENT_DEFORMATION":
        if before_state != "INSTALLED_REPORTED" or after["state"] != "INSTALLED_REPORTED" or \
           (before["component_model_ref"], before["hardware_serial_claim"]) != \
           (after["component_model_ref"], after["hardware_serial_claim"]) or \
           before["condition_claim"] == "MODIFIED_REPORTED" or \
           after["condition_claim"] != "MODIFIED_REPORTED":
            raise ContractError("CHANGE_KIND_MISMATCH")


def slots_by_id(revision):
    items = revision["component_slots"]
    result = {}
    for slot in items:
        key = slot["slot_id"]
        if key in result:
            raise ContractError("DUPLICATE_SLOT")
        if slot["state"] == "UNKNOWN":
            if slot["component_model_ref"] is not None or slot["hardware_serial_claim"] is not None:
                raise ContractError("UNKNOWN_SLOT_HAS_HARDWARE")
        if slot["state"] == "REMOVED_REPORTED":
            if slot["component_model_ref"] is not None or slot["hardware_serial_claim"] is not None:
                raise ContractError("REMOVED_SLOT_HAS_HARDWARE")
        result[key] = slot
    return result


def validate(record):
    bounded(record)
    if not isinstance(record, dict) or type(record.get("record_type")) is not str:
        raise ContractError("UNKNOWN_RECORD")
    kind = record["record_type"]
    if kind not in VALIDATORS:
        raise ContractError("UNKNOWN_RECORD")
    if next(VALIDATORS[kind].iter_errors(record), None) is not None:
        raise ContractError("SCHEMA_VIOLATION")
    if record["record_digest"] != digest(record):
        raise ContractError("DIGEST_MISMATCH")
    if record["claimed_event_time"]["token"] is None and record["claimed_event_time"]["clock_domain"] is not None:
        raise ContractError("INVALID_CLAIMED_TIME")
    if kind == "AsBuiltRevision":
        slots = slots_by_id(record)
        serial_keys = set()
        for slot in slots.values():
            if slot["hardware_serial_claim"] is not None:
                key = (slot["component_model_ref"], slot["hardware_serial_claim"])
                if key in serial_keys:
                    raise ContractError("DUPLICATE_SERIAL_CLAIM")
                serial_keys.add(key)
        if record["revision_number"] == 0 and record["calibration_status"] != "UNKNOWN":
            raise ContractError("INVALID_GENESIS_CALIBRATION")
    else:
        seen_slots = set()
        changed_targets = {"links": set(), "joints": set(), "sensors": set()}
        for change in record["slot_changes"]:
            key = change["slot_id"]
            if key in seen_slots:
                raise ContractError("DUPLICATE_SLOT_CHANGE")
            seen_slots.add(key)
            before, after = change["before"], change["after"]
            if after["slot_id"] != key or (before is not None and before["slot_id"] != key):
                raise ContractError("SLOT_ID_MISMATCH")
            if before is None and after["state"] != "INSTALLED_REPORTED":
                raise ContractError("NEW_SLOT_NOT_INSTALLED")
            if before is not None and physical_slot(before) == physical_slot(after):
                raise ContractError("VISUAL_OR_EVIDENCE_ONLY_MUTATION")
            check_change_kind(record["change_kind"], before, after, record["affected_sensors"])
            for label, field in (("links", "link_refs"), ("joints", "joint_refs"),
                                 ("sensors", "sensor_refs")):
                if before is not None:
                    changed_targets[label].update(before[field])
                changed_targets[label].update(after[field])
        if not changed_targets["links"].issubset(set(record["affected_links"])) or \
           not changed_targets["joints"].issubset(set(record["affected_joints"])) or \
           not changed_targets["sensors"].issubset(set(record["affected_sensors"])):
            raise ContractError("IMPACT_UNDERDECLARED")
        if record["assertion_stage"] == "INSTALLED_REPORTED_UNVERIFIED":
            if record["actor_claim_ref"] is None:
                raise ContractError("INSTALLED_ACTOR_CLAIM_REQUIRED")
            if record["before_revision_ref"] == record["after_revision_ref"] or \
               record["before_revision_digest"] == record["after_revision_digest"]:
                raise ContractError("REUSED_REVISION")
    return record


def validate_transition(before, event, after):
    """Offline chain/claim consistency, NEVER physical truth or writer authority."""
    for obj in (before, event, after):
        validate(obj)
    if before["record_type"] != "AsBuiltRevision" or \
       event["record_type"] != "HardwareMutationEvent" or \
       after["record_type"] != "AsBuiltRevision":
        raise ContractError("INVALID_TRANSITION_TYPES")
    if event["assertion_stage"] != "INSTALLED_REPORTED_UNVERIFIED":
        raise ContractError("PROPOSAL_NOT_INSTALLATION")
    if not (before["robot_instance_ref"] == event["robot_instance_ref"] ==
            after["robot_instance_ref"]) or \
       not (before["physical_enrollment_ref"] == event["physical_enrollment_ref"] ==
            after["physical_enrollment_ref"]):
        raise ContractError("ROBOT_CONTEXT_MISMATCH")
    if event["before_revision_ref"] != before["record_id"] or \
       event["before_revision_digest"] != before["record_digest"] or \
       event["after_revision_ref"] != after["record_id"] or \
       event["after_revision_digest"] != after["record_digest"] or \
       after["previous_revision_ref"] != before["record_id"] or \
       after["previous_revision_digest"] != before["record_digest"] or \
       after["triggering_mutation_ref"] != event["record_id"]:
        raise ContractError("BROKEN_REVISION_LINK")
    if after["revision_number"] != before["revision_number"] + 1:
        raise ContractError("NONSEQUENTIAL_REVISION")
    if before["design_source_root"] != event["design_source_root_before"] or \
       after["design_source_root"] != event["design_source_root_after"] or \
       before["visual_manifest_sha256"] != event["visual_manifest_before"] or \
       after["visual_manifest_sha256"] != event["visual_manifest_after"]:
        raise ContractError("SOURCE_VISUAL_REVISION_MISMATCH")
    if after["calibration_status"] != "REVIEW_REQUIRED" or \
       after["calibration_revision_claim"] is not None or \
       not after["safety_review_required"]:
        raise ContractError("CALIBRATION_NOT_INVALIDATED")
    old_calibration = before["calibration_revision_claim"]
    if old_calibration is not None and old_calibration not in event["invalidated_calibration_refs"]:
        raise ContractError("STALE_CALIBRATION_NOT_INVALIDATED")
    if not set(event["evidence_refs"]).issubset(set(after["evidence_refs"])):
        raise ContractError("MISSING_MUTATION_EVIDENCE")
    old = slots_by_id(before)
    new = slots_by_id(after)
    # A removed slot MUST remain as an explicit REMOVED_REPORTED claim; do not
    # erase the historical slot identity from the new instance snapshot.
    if not set(old).issubset(set(new)):
        raise ContractError("REMOVED_SLOT_LOST")
    actual = {
        key for key in new
        if key not in old or physical_slot(new[key]) != physical_slot(old[key])
    }
    declared = {change["slot_id"] for change in event["slot_changes"]}
    if not actual or actual != declared:
        raise ContractError("UNDECLARED_OR_VISUAL_ONLY_DELTA")
    for change in event["slot_changes"]:
        key = change["slot_id"]
        if change["before"] != old.get(key) or change["after"] != new[key]:
            raise ContractError("DELTA_DOES_NOT_MATCH_SNAPSHOTS")
    return {
        "status": "CONSISTENT_UNVERIFIED",
        "robot_instance_ref": before["robot_instance_ref"],
        "revision_number": after["revision_number"],
        "physical_truth_verified": False, "history_written": False,
        "life_verified": False, "authorization_granted": False
    }


def validate_chain(revisions, events):
    if not isinstance(revisions, list) or not revisions:
        raise ContractError("EMPTY_CHAIN")
    if not isinstance(events, list) or len(events) != len(revisions) - 1:
        raise ContractError("CHAIN_LENGTH_MISMATCH")
    ids = [obj.get("record_id") for obj in revisions + events]
    if len(ids) != len(set(ids)):
        raise ContractError("DUPLICATE_RECORD_ID")
    if revisions[0]["revision_number"] != 0:
        raise ContractError("NO_GENESIS_REVISION")
    validate(revisions[0])
    for index, event in enumerate(events):
        validate_transition(revisions[index], event, revisions[index + 1])
    return {"status": "CANDIDATE_CHAIN_CONSISTENT", "revisions": len(revisions),
            "history_written": False, "identity_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="*", help="0/1 file: schema/self-check; 3 files: BEFORE EVENT AFTER")
    opts = parser.parse_args()
    try:
        status = read_json(HERE / "STATUS.json")
        if status.get("maturity") != "candidate" or any(status.get(k) is not False for k in (
            "normative", "accepted", "runtime_implemented", "mutation_authority_implemented",
            "life_identity_issuer_implemented", "history_writer_implemented"
        )):
            raise ContractError("MATURITY_GUARD")
        if len(opts.records) == 0:
            result = {"status": "CANDIDATE_SCHEMAS_VALID", "types": len(KINDS),
                      "physical_truth_verified": False, "history_written": False}
        elif len(opts.records) == 1:
            item = validate(read_json(opts.records[0]))
            result = {"status": "SHAPE_AND_DIGEST_VALID_CANDIDATE",
                      "type": item["record_type"], "physical_truth_verified": False}
        elif len(opts.records) == 3:
            result = validate_transition(*(read_json(x) for x in opts.records))
        else:
            raise ContractError("INVALID_ARGUMENT_COUNT")
        print(json.dumps(result, sort_keys=True))
        return 0
    except ContractError as exc:
        print(json.dumps({"status":"REJECTED","code":str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
