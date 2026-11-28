"""Trusted test harness: real commit -> fresh materialization -> actual wheel.

The previous fixture generator provides source declarations once; its first
wheel is discarded. This fixture is not a production builder or attester.
"""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

from securesystemslib.dsse import Envelope
from securesystemslib.signer import CryptoSigner
from proposal import parse, digest, encode_proposal
from trust_fixture import build_fixture, proposal_for
from provenance import source_inventory, BUILD_TYPE, PAYLOAD_TYPE

PACKAGE="openrgd_trust_probe"
URI="https://example.invalid/synthetic/trust-probe"
BUILDER="https://example.invalid/builders/offline-wheel"

def run(args,cwd):
    r=subprocess.run(args,cwd=cwd,capture_output=True,timeout=90,check=False)
    if r.returncode:raise RuntimeError("fixture command failed: "+r.stderr[-4000:].decode(errors="replace"))
    return r.stdout

def build_source_fixture(root):
    root=Path(root)
    inputs=build_fixture(root/"declarations")
    old=root/"declarations/producer"
    repo=root/"repository";repo.mkdir()
    shutil.copyfile(old/"pyproject.toml",repo/"pyproject.toml")
    shutil.copytree(old/PACKAGE,repo/PACKAGE)
    run(["git","init","--object-format=sha1"],repo)
    run(["git","add","--","pyproject.toml",PACKAGE],repo)
    run(["git","-c","user.name=Test Builder","-c","user.email=builder@example.invalid",
         "commit","--no-gpg-sign","-m","Synthetic source before build"],repo)
    commit=run(["git","rev-parse","HEAD"],repo).decode().strip()
    files,entries,tree=source_inventory(repo,commit,PACKAGE)
    build=root/"fresh-build";build.mkdir()
    for path,data in files.items():
        dest=build/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    out=root/"actual-dist"
    run([sys.executable,"-m","build","--wheel","--no-isolation","--outdir",str(out),str(build)],build)
    wheels=list(out.glob("*.whl"))
    if len(wheels)!=1:raise RuntimeError("expected one fixture wheel")
    wheel=wheels[0]
    inputs.update(artifact_bytes={"wheel":wheel.read_bytes()},filename=wheel.name,
                  source_claim=encode_proposal({"repository_uri":URI,"git_commit":commit}))
    signer=CryptoSigner.generate_ed25519()
    module=parse(inputs["manifest_raw"])
    policy={"schema_version":"openrgd.builder-policy.v0.1-candidate",
        "policy_id":"org.example.review.builder-policy","policy_version":"0.1.0",
        "module_id":module["module_id"],"module_version":module["module_version"],
        "repository_uri":URI,"git_commit":commit,"source_tree_sha256":tree,
        "recipe_sha256":digest(files["pyproject.toml"]),"package_root":PACKAGE,
        "build_type":BUILD_TYPE,"builder_id":BUILDER,"builder_keyid":signer.public_key.keyid,
        "builder_public_key":signer.public_key.keyval["public"],"grants_authority":False}
    return {"inputs":inputs,"repository":repo,"policy":policy,"signer":signer,"source_files":files}

def statement_for(fixture,inputs=None):
    p=fixture["policy"];i=fixture["inputs"] if inputs is None else inputs
    uri="git+"+p["repository_uri"]+"@"+p["git_commit"]
    # Independent fixture statement generation; never call verifier expectation.
    return {"_type":"https://in-toto.io/Statement/v1",
        "subject":[{"name":i["filename"],"digest":{"sha256":digest(i["artifact_bytes"]["wheel"])[7:]}}],
        "predicateType":"https://slsa.dev/provenance/v1",
        "predicate":{"buildDefinition":{"buildType":BUILD_TYPE,
            "externalParameters":{"repository":p["repository_uri"],"commit":p["git_commit"],"packageRoot":p["package_root"]},
            "internalParameters":{},
            "resolvedDependencies":[{"uri":uri,"digest":{"gitCommit":p["git_commit"],
                "sha256":p["source_tree_sha256"][7:]}},
                {"uri":uri+"#pyproject.toml","digest":{"sha256":p["recipe_sha256"][7:]}}]},
            "runDetails":{"builder":{"id":p["builder_id"]},"metadata":{"invocationId":str(uuid4())}}}}

def sign_statement(statement,signer):
    envelope=Envelope(encode_proposal(statement),PAYLOAD_TYPE,{})
    envelope.sign(signer)
    return encode_proposal(envelope.to_dict())

def verification_inputs(fixture,inputs=None,statement=None,signer=None,policy=None):
    i=deepcopy(fixture["inputs"] if inputs is None else inputs)
    st=statement_for(fixture,i) if statement is None else statement
    return {**i,"submitted_proposal_raw":proposal_for(i),
            "attestation_raw":sign_statement(st,fixture["signer"] if signer is None else signer),
            "policy_raw":encode_proposal(fixture["policy"] if policy is None else policy),
            "local_repository":fixture["repository"]}
