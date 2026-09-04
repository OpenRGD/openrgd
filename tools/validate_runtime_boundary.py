#!/usr/bin/env python3
"""Ensure the canonical CLI does not silently become a hardware runtime."""
from __future__ import annotations
import ast, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMAND=ROOT/'src/openrgd/commands/run.py'
FORBIDDEN={'rclpy','viam','serial','can'}
def main()->int:
    tree=ast.parse(COMMAND.read_text(encoding='utf-8'))
    imports=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): imports.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module: imports.add(node.module.split('.')[0])
    bad=sorted(imports&FORBIDDEN)
    if bad: print('FAIL: canonical runtime command imports hardware middleware: '+', '.join(bad),file=sys.stderr); return 1
    if (ROOT/'src/openrgd/runtime').exists(): print('FAIL: physical runtime package unexpectedly present',file=sys.stderr); return 1
    print('PASS: canonical runtime boundary remains non-actuating')
    return 0
if __name__=='__main__': raise SystemExit(main())
