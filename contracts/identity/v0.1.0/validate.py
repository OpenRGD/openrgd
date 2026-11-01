"""Offline candidate shape checks only. Never resolve/issue identity or grants."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
MAX_BYTES, MAX_NODES, MAX_DEPTH = 131072, 4096, 32

class ContractError(ValueError):
    """Stable public code, not raw private record text."""

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError('DUPLICATE_KEY')
        result[key] = value
    return result

def _reject_constant(value):
    raise ContractError('NONFINITE')

def _parse_int(value):
    if len(value) > 32:
        raise ContractError('NUMBER_LIMIT')
    return int(value)

def bounded(value):
    stack, nodes = [(value, 0)], 0
    while stack:
        item, depth = stack.pop(); nodes += 1
        if depth > MAX_DEPTH or nodes > MAX_NODES:
            raise ContractError('STRUCTURE_LIMIT')
        if isinstance(item, dict):
            if any(not isinstance(k, str) for k in item):
                raise ContractError('NON_JSON_KEY')
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
        elif isinstance(item, float) and not math.isfinite(item):
            raise ContractError('NONFINITE')
        elif item is not None and not isinstance(item, (str, int, float, bool)):
            raise ContractError('NON_JSON_VALUE')
    try:
        if len(json.dumps(value, allow_nan=False).encode('utf-8')) > MAX_BYTES:
            raise ContractError('SIZE_LIMIT')
    except ContractError:
        raise
    except (ValueError, OverflowError, RecursionError, UnicodeError):
        raise ContractError('INVALID_JSON_VALUE') from None

def read_json(path):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ContractError('SIZE_LIMIT')
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_constant=_reject_constant, parse_int=_parse_int)
        bounded(value)
        return value
    except ContractError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise ContractError('JSON_READ_FAILED') from None

SCHEMA = read_json(ROOT / 'schemas/identity.schema.json')
Draft202012Validator.check_schema(SCHEMA)
NAMES = tuple(x['$ref'].rsplit('/', 1)[1] for x in SCHEMA['oneOf'])
VALIDATORS = {name: Draft202012Validator({
    '$schema': SCHEMA['$schema'], '$defs': SCHEMA['$defs'],
    '$ref': '#/$defs/' + name}) for name in NAMES}

def validate(record):
    bounded(record)
    if (not isinstance(record, dict) or not isinstance(record.get('record_type'), str)
            or record['record_type'] not in VALIDATORS):
        raise ContractError('UNKNOWN_RECORD')
    if next(VALIDATORS[record['record_type']].iter_errors(record), None) is not None:
        raise ContractError('SCHEMA_VIOLATION')
    if record['record_type'] == 'RoleLease' and record['valid_until_ms'] <= record['valid_from_ms']:
        raise ContractError('INVALID_LEASE_INTERVAL')
    if record['record_type'] == 'LifeIdentity' and record['predecessor_life_id'] == record['life_id']:
        raise ContractError('SELF_FORK')
    return record

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', nargs='?')
    args = parser.parse_args()
    try:
        status = read_json(ROOT / 'STATUS.json')
        if status.get('maturity') != 'candidate' or any(status.get(k) is not False for k in
                ('normative', 'accepted', 'runtime_implemented', 'stable_release_allowed')):
            raise ContractError('MATURITY_GUARD')
        if args.record:
            validate(read_json(args.record))
        print(json.dumps({'status': 'SHAPE_VALID' if args.record else 'CANDIDATE_SCHEMAS_VALID',
                          'types': len(NAMES), 'identity_verified': False,
                          'authorization_verified': False, 'runtime_executed': False}))
        return 0
    except ContractError as exc:
        print(json.dumps({'status': 'REJECTED', 'code': str(exc)}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
