from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_public_hygiene_validator_passes():
    r=subprocess.run([sys.executable,str(ROOT/'tools/validate_hygiene.py')],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
def test_env_is_ignored():
    text=(ROOT/'.gitignore').read_text(encoding='utf-8')
    assert '\n.env\n' in '\n'+text
