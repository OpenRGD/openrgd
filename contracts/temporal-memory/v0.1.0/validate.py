"""CORE-D candidate JSON shape validation; NOT an authority, issuer or history writer."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
MAX_BYTES, MAX_NODES, MAX_DEPTH = 131072, 4096, 32
UINT64_MAX = 18446744073709551615

class ContractError(ValueError):
    """Redacted fixed error code, not source/private payload."""

def pairs(items):
    out = {}
    for k, v in items:
        if k in out:
            raise ContractError("DUPLICATE_KEY")
        out[k] = v
    return out

def bad_constant(_):
    raise ContractError("NONFINITE")

def int_value(s):
    if len(s) > 32:
        raise ContractError("NUMBER_LIMIT")
    return int(s)

def bounded(value):
    stack, seen, n = [(value, 0)], set(), 0
    while stack:
        item, depth = stack.pop()
        n += 1
        if n > MAX_NODES or depth > MAX_DEPTH:
            raise ContractError("STRUCTURE_LIMIT")
        if isinstance(item, (dict, list)):
            if id(item) in seen:
                raise ContractError("SHARED_OR_CYCLIC_CONTAINER")
            seen.add(id(item))
            if isinstance(item, dict):
                if any(not isinstance(k, str) for k in item):
                    raise ContractError("NON_JSON_KEY")
                stack.extend((v, depth + 1) for v in item.values())
            else:
                stack.extend((v, depth + 1) for v in item)
        elif isinstance(item, float) and not math.isfinite(item):
            raise ContractError("NONFINITE")
        elif item is not None and not isinstance(item, (str, int, float, bool)):
            raise ContractError("NON_JSON_VALUE")
    try:
        if len(json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf8")) > MAX_BYTES:
            raise ContractError("SIZE_LIMIT")
    except ContractError:
        raise
    except (ValueError, OverflowError, RecursionError, UnicodeError):
        raise ContractError("INVALID_JSON") from None

def read_json(path):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ContractError("SIZE_LIMIT")
        value = json.loads(raw.decode("utf8"), object_pairs_hook=pairs,
                           parse_constant=bad_constant, parse_int=int_value)
        bounded(value)
        return value
    except ContractError:
        raise
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise ContractError("JSON_READ_FAILED") from None

SCHEMA = read_json(ROOT / "schemas/temporal-memory.schema.json")
Draft202012Validator.check_schema(SCHEMA)
KINDS = tuple(x["$ref"].rsplit("/", 1)[-1] for x in SCHEMA["oneOf"])
VALIDATORS = {name: Draft202012Validator({
    "$schema": SCHEMA["$schema"], "$defs": SCHEMA["$defs"],
    "$ref": "#/$defs/" + name
}) for name in KINDS}

def validate(value):
    bounded(value)
    if not isinstance(value, dict) or not isinstance(value.get("record_type"), str) or value["record_type"] not in VALIDATORS:
        raise ContractError("UNKNOWN_RECORD")
    kind = value["record_type"]
    if next(VALIDATORS[kind].iter_errors(value), None) is not None:
        raise ContractError("SCHEMA_VIOLATION")
    if kind == "HistoricalTimeAssertion" and value["timestamp_format"] == "LEGACY_POSIX_SECONDS":
        try:
            if not Decimal(value["claimed_time_token"]).is_finite():
                raise ContractError("INVALID_LEGACY_TIMESTAMP")
        except (InvalidOperation, ValueError):
            raise ContractError("INVALID_LEGACY_TIMESTAMP") from None
    if kind == "ImportAnchorEvidence" and int(value["anchor_handle_uint64_dec"]) > UINT64_MAX:
        raise ContractError("ANCHOR_HANDLE_OVERFLOW")
    if kind == "MemoryAnnotation" and value["supersedes_annotation_ref"] == value["record_id"]:
        raise ContractError("SELF_SUPERSEDES")
    if kind == "SalienceHint" and value["previous_hint_ref"] == value["record_id"]:
        raise ContractError("SELF_SUPERSEDES")
    if kind == "HistoryCommitReceipt" and value["receipt_status"] == "NOT_CONFIRMED" and value["reporter_class"] != "REQUESTER_OBSERVATION":
        raise ContractError("NONCONFIRMATION_IS_REQUESTER_OBSERVATION")
    if kind == "EvidenceAvailability" and value["reported_state"] in ("ERASED", "REDACTED") and value["proof_ref"] is None:
        raise ContractError("REDACTION_PROOF_REFERENCE_REQUIRED")
    return value

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("record", nargs="?")
    args = ap.parse_args()
    try:
        status = read_json(ROOT / "STATUS.json")
        if status.get("maturity") != "candidate" or any(status.get(k) is not False for k in (
            "normative", "accepted", "runtime_implemented", "stable_release_allowed"
        )):
            raise ContractError("MATURITY_GUARD")
        if args.record:
            validate(read_json(args.record))
        print(json.dumps({"status": "SHAPE_VALID" if args.record else "CANDIDATE_SCHEMAS_VALID",
                          "types": len(KINDS), "life_verified": False,
                          "chronograf_verified": False, "history_written": False,
                          "permissions_granted": False}))
        return 0
    except ContractError as error:
        print(json.dumps({"status": "REJECTED", "code": str(error)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
