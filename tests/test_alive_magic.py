from __future__ import annotations
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'example/minimal-arm/openrgd_minimal_arm.urdf'
def test_alive_runs_the_golden_loop(tmp_path:Path):
    project=tmp_path/'robot'
    r=subprocess.run(['rgd','--quiet','alive',str(FIXTURE),'--out',str(project)],cwd=tmp_path,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    assert (project/'spec/manifest.jsonc').is_file()
    assert (project/'spec/openrgd_unified_spec.json').is_file()
    assert (project/'artifacts/grounding_context.json').is_file()
    assert (project/'export/ros2/export_manifest.json').is_file()
    grounding=json.loads((project/'artifacts/grounding_context.json').read_text(encoding='utf-8'))
    assert grounding['physical_execution']['authorized'] is False
