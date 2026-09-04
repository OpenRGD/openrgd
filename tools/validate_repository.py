#!/usr/bin/env python3
"""Validate the friendly public OpenRGD repository surface."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main()->int:
    required=['README.md','ONBOARDING.md','ENTHUSIAST.md','CLI_GUIDE.md','GUIDE_IMPORT.md','GUIDE_EXPORT.md','GUIDE_DOCKER.md','PLUGIN_GUIDE.md','STRUCTURE.md','LAYOUT.md','CONTRIBUTING.md','GOVERNANCE.md','SECURITY.md','spec','src/openrgd','example','tests']
    missing=[p for p in required if not (ROOT/p).exists()]
    forbidden=['docs/reconciliation','docs/history','governance']
    leaked=[p for p in forbidden if (ROOT/p).exists()]
    if missing or leaked:
        if missing: print('FAIL: missing public surface: '+', '.join(missing),file=sys.stderr)
        if leaked: print('FAIL: internal reconstruction material is public: '+', '.join(leaked),file=sys.stderr)
        return 1
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    for phrase in ['Bring a Robot Alive','rgd alive','Contribute']:
        if phrase not in readme:
            print(f'FAIL: README lost friendly entry point: {phrase}',file=sys.stderr); return 1
    print('PASS: friendly public repository surface')
    return 0
if __name__=='__main__': raise SystemExit(main())
