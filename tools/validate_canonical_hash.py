#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from openrgd.core.canonical import INTEGRITY_PROFILE, compute_integrity
ROOT=Path(__file__).resolve().parents[1]
def main()->int:
    try: result=compute_integrity(ROOT/'spec')
    except Exception as exc: print(f'FAIL: {exc}',file=sys.stderr); return 1
    if result.profile!=INTEGRITY_PROFILE or not result.matches:
        print('FAIL: canonical source root mismatch\n'+json.dumps(result.as_dict(),indent=2,sort_keys=True),file=sys.stderr); return 1
    print(f'PASS: canonical source root {result.computed}; {result.files_count} source files')
    return 0
if __name__=='__main__': raise SystemExit(main())
