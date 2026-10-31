"""Offline candidate-shape validator; never a grant, runtime, scheduler or verifier."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent
TYPES = (
    "KernelDescriptor", "KernelEvent", "CognitiveGoalCandidate",
    "GoalAdmissionDecision", "AgendaTransition", "EffectRequest", "EffectGateDecision",
)
MAX_BYTES = 65536


class ContractError(ValueError):
    """Stable redacted code; do not expose untrusted payloads in diagnostics."""


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("DUPLICATE_KEY")
        result[key] = value
    return result


def _constant(_value):
    raise ContractError("NONFINITE_JSON")


def read_json(path: Path):
    """Read local input only, with a bounded read; no URI fetching."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(1048577)
        if len(raw) > 1048576:
            raise ContractError("FILE_TOO_LARGE")
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise ContractError("INVALID_JSON") from None


def _bounded(value):
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > 24 or count > 4096:
            raise ContractError("STRUCTURE_LIMIT")
        if isinstance(item, dict):
            if any(not isinstance(k, str) for k in item):
                raise ContractError("NON_JSON_KEY")
            pending.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            pending.extend((v, depth + 1) for v in item)
        elif isinstance(item, float) and not math.isfinite(item):
            raise ContractError("NONFINITE_JSON")
        elif item is not None and not isinstance(item, (str, bool, int, float)):
            raise ContractError("NON_JSON_VALUE")
    try:
        size = len(json.dumps(value, allow_nan=False, ensure_ascii=True).encode("utf-8"))
    except (ValueError, TypeError, OverflowError):
        raise ContractError("INVALID_JSON") from None
    if size > MAX_BYTES:
        raise ContractError("RECORD_TOO_LARGE")


def _no_retrieval(uri):
    raise ContractError("EXTERNAL_SCHEMA_REF_DISABLED")


def validators():
    schema = read_json(ROOT / "schemas/kernel-goal-effect.schema.json")
    Draft202012Validator.check_schema(schema)
    registry = Registry(retrieve=_no_retrieval).with_resource(
        schema["$id"], Resource.from_contents(schema)
    )
    return {
        name: Draft202012Validator(
            {"$ref": schema["$id"] + "#/$defs/" + name}, registry=registry
        )
        for name in TYPES
    }


_VALIDATORS = None


def validate(kind: str, record: dict):
    """Validate shape only. Caller must authenticate producers and verify policy."""
    global _VALIDATORS
    if kind not in TYPES:
        raise ContractError("UNKNOWN_CONTRACT")
    _bounded(record)
    if _VALIDATORS is None:
        _VALIDATORS = validators()
    if not _VALIDATORS[kind].is_valid(record):
        raise ContractError("SCHEMA_VIOLATION:" + kind)
    return record


def mutated(record: dict, changes: dict):
    """Fixture-only dot-path replacement; never executes payload expressions."""
    output = deepcopy(record)
    for path, value in changes.items():
        keys = path.split(".")
        target = output
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
    return output


def check_fixtures():
    positive = read_json(ROOT / "fixtures/positive.json")
    negative = read_json(ROOT / "fixtures/negative.json")
    if positive.get("fixture_only") is not True or negative.get("fixture_only") is not True:
        raise ContractError("FIXTURE_FLAG_REQUIRED")
    records = positive["records"]
    for item in records.values():
        validate(item["type"], item["record"])
    for case in negative["cases"]:
        source = records[case["base"]]
        candidate = mutated(source["record"], case["set"])
        try:
            validate(source["type"], candidate)
        except ContractError:
            continue
        raise ContractError("NEGATIVE_FIXTURE_ACCEPTED:" + case["id"])
    return len(records), len(negative["cases"])


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        if not args:
            counts = check_fixtures()
            print(json.dumps({"status": "CANDIDATE_FIXTURES_VALID", "positive": counts[0],
                              "negative": counts[1], "normative": False,
                              "authorization_verified": False, "runtime_executed": False}))
        elif len(args) == 2:
            validate(args[0], read_json(Path(args[1])))
            print(json.dumps({"status": "SHAPE_VALID_ONLY", "normative": False,
                              "authorization_verified": False, "runtime_executed": False}))
        else:
            raise ContractError("USAGE: validate.py [TYPE LOCAL_JSON_FILE]")
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
