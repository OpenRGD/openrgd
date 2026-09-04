from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(path): return subprocess.run([sys.executable,str(ROOT/path)],cwd=ROOT,capture_output=True,text=True)
def test_public_repository_validator_passes():
    r=run('tools/validate_repository.py'); assert r.returncode==0,r.stdout+r.stderr
def test_artifact_validator_passes():
    r=run('tools/validate_artifacts.py'); assert r.returncode==0,r.stdout+r.stderr
def test_hash_validator_passes():
    r=run('tools/validate_canonical_hash.py'); assert r.returncode==0,r.stdout+r.stderr
def test_runtime_boundary_passes():
    r=run('tools/validate_runtime_boundary.py'); assert r.returncode==0,r.stdout+r.stderr
