#!/usr/bin/env python3
"""Reject obvious secret material and generated debris from tracked files."""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
TOKEN_PATTERNS=[re.compile(r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
SECRET_NAMES={'.env','id_rsa','id_ed25519'}
def main()->int:
    result=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
    errors=[]
    for raw in result.stdout.split(b'\0'):
        if not raw: continue
        path=raw.decode(); pure=PurePosixPath(path)
        if pure.name in SECRET_NAMES or pure.suffix.lower() in {'.key','.p12','.pfx','.pem'}: errors.append(f'secret-bearing filename: {path}')
        if '__pycache__' in pure.parts or pure.suffix.lower() in {'.pyc','.pyo'} or any(p.endswith('.egg-info') for p in pure.parts): errors.append(f'generated Python debris: {path}')
        file=ROOT/path
        if file.is_file() and file.stat().st_size<2_000_000 and pure.suffix.lower() not in {'.png','.ico','.exe','.zip','.rar'}:
            try: text=file.read_text(encoding='utf-8')
            except UnicodeDecodeError: continue
            if any(pattern.search(text) for pattern in TOKEN_PATTERNS): errors.append(f'possible secret material: {path}')
    if errors:
        for e in errors: print('FAIL:',e,file=sys.stderr)
        return 1
    print('PASS: tracked files contain no obvious secret material or generated Python debris')
    return 0
if __name__=='__main__': raise SystemExit(main())
