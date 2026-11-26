"""Test-only wheel producer: build a real wheel from a deliberately inert fixture.

No real module is installed, published or imported. Source claim is illustrative.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys

from proposal import HIST, parse, digest, project_command_facade, propose, encode_proposal

def build_fixture(root):
    root=Path(root)
    source=root/"producer"
    pkg=source/"openrgd_trust_probe"
    pkg.mkdir(parents=True)
    # A test would fail if the provider were ever imported.
    (pkg/"__init__.py").write_text('raise RuntimeError("test-only provider must not be imported")\n',encoding="utf-8")
    (source/"pyproject.toml").write_text('''[build-system]
requires = ["setuptools==80.9.0", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"
[project]
name = "openrgd-trust-probe"
version = "0.1.0"
description = "Test-only publication fixture"
[project.entry-points."rgd.commands"]
rgd-trust-probe = "openrgd_trust_probe:attach"
[tool.setuptools]
packages = ["openrgd_trust_probe"]
[tool.setuptools.package-data]
openrgd_trust_probe = ["module.openrgd.json", "extensions/*.json", "openrgd_commands/*.json"]
''',encoding="utf-8")
    ext=parse((HIST/"extensions/v0.1.0/examples/manifests/motion.json").read_bytes())
    ext.update(extension_id="org.example.trust-probe.cli",extension_version="0.1.0",
               description="Synthetic declaration for artifact inspection only")
    ext["implementation"]={"kind":"python_package","name":"openrgd-trust-probe",
                           "version":"0.1.0","evidence_status":"illustrative"}
    ext["provides"]=[];ext["requires"]=[]
    ext["permissions_requested"]=[]
    ext["authority"]={"requested_effects":[],"grants_authority":False}
    ext["cli"].update(entry_point_name="rgd-trust-probe",
                      entry_point_target="openrgd_trust_probe:attach",namespace="trust-probe")
    ext_path="extensions/probe.json"
    facade_path="openrgd_commands/rgd-trust-probe.json"
    ext_raw=encode_proposal(ext)
    facade_raw=encode_proposal(project_command_facade(ext_raw))
    descriptors={ext_path:ext_raw,facade_path:facade_raw}
    m={"schema_version":"openrgd.module-manifest.v0.1-candidate",
       "module_id":"org.example.trust-probe","module_version":"0.1.0",
       "display_name":"Test-only wheel probe","functional_roles":["observability"],
       "extension_descriptors":[{"path":ext_path,"sha256":digest(ext_raw)}],
       "command_facades":[{"descriptor":{"path":facade_path,"sha256":digest(facade_raw)},
                           "extension_descriptor_path":ext_path,"artifact_slot_id":"wheel"}],
       "artifact_slots":[{"slot_id":"wheel","artifact_kind":"python_wheel",
                          "media_type":"application/zip","platform_profile":"py3-none-any",
                          "package_name":"openrgd-trust-probe","package_version":"0.1.0",
                          "extension_descriptor_paths":[ext_path]}],
       "dependencies":[],"grants_authority":False}
    manifest=encode_proposal(m)
    (pkg/"module.openrgd.json").write_bytes(manifest)
    for path,data in descriptors.items():
        target=pkg/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # No build isolation or fetching dependencies. All builder dependencies are
    # supplied by the test environment. This is fixture generation, not a verifier.
    out=root/"dist"
    result=subprocess.run([sys.executable,"-m","build","--wheel","--no-isolation",
                           "--outdir",str(out),str(source)],capture_output=True,text=True,
                          timeout=90,check=False)
    if result.returncode:
        raise RuntimeError("fixture build failed:\n"+result.stdout[-5000:]+"\n"+result.stderr[-5000:])
    wheels=list(out.glob("*.whl"))
    if len(wheels)!=1:
        raise RuntimeError("fixture did not produce exactly one wheel")
    w=wheels[0]
    return {"manifest_raw":manifest,"descriptor_bytes":descriptors,"artifact_bytes":{"wheel":w.read_bytes()},
            "source_claim":encode_proposal({"repository_uri":"https://example.invalid/synthetic/trust-probe",
                                            "git_commit":"a"*40}),"filename":w.name}

def proposal_for(inputs):
    return encode_proposal(propose(inputs["manifest_raw"],inputs["descriptor_bytes"],
                                  inputs["artifact_bytes"],inputs["source_claim"]))
