#!/usr/bin/env python3
"""Check the public OpenRGD source, strict JSON mirror and packaged seed."""
from __future__ import annotations
import json, sys
from pathlib import Path
from openrgd.core.canonical import discover_source_paths
from openrgd.core.utils import strip_jsonc
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/'spec'; STANDARD=ROOT/'standard'; SEED=ROOT/'src/openrgd/seeds/default/spec'

def parsed(path:Path): return json.loads(strip_jsonc(path.read_text(encoding='utf-8')),strict=False)
def main()->int:
    errors=[]; sources=discover_source_paths(SPEC)
    for src in sources:
        rel=src.relative_to(SPEC); seed=SEED/rel
        if not seed.is_file(): errors.append(f'missing seed: {rel}')
        elif seed.read_bytes()!=src.read_bytes(): errors.append(f'seed differs: {rel}')
        target=STANDARD/(rel.with_suffix('.json') if src.suffix=='.jsonc' else rel)
        if not target.is_file(): errors.append(f'missing standard mirror: {target.relative_to(STANDARD)}')
        else:
            try:
                same=parsed(src)==json.loads(target.read_text(encoding='utf-8')) if src.suffix=='.jsonc' else src.read_bytes()==target.read_bytes()
            except Exception as exc: errors.append(f'unreadable mirror {rel}: {exc}'); same=True
            if not same: errors.append(f'standard mirror differs: {rel}')
    if errors:
        for e in errors: print('FAIL:',e,file=sys.stderr)
        return 1
    print(f'PASS: {len(sources)} canonical source files mirrored and packaged')
    return 0
if __name__=='__main__': raise SystemExit(main())
