"""Static consistency review layered on the pinned 01A/B candidates.

Not an executable safety gate, model editor, calibration validator or loader.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import tempfile

from jsonschema import Draft202012Validator
from referencing import Resource

ROOT=Path(__file__).resolve().parent
B_ROOT=ROOT.parents[1]/"source-conformance/v0.1.0"
sys.path.insert(0,str(B_ROOT))
import source_conformance as sc

source=sc.source
LEGACY="LEGACY_UNQUALIFIED"
RAW="RAW_DESCRIPTION_SHA256_V0.1_CANDIDATE"
SCHEMA=json.loads((ROOT/"schemas/foundation-consistency.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
REGISTRY=sc.REGISTRY.with_resource(SCHEMA["$id"],Resource.from_contents(SCHEMA))
VALIDATOR=Draft202012Validator(SCHEMA,registry=REGISTRY)
APPLICABLE=("REQUIRED_PRESENT","OPTIONAL_PRESENT")

def declared_failure_policy(global_allow,local_block):
    """Conditional on a failed check. Never returns ALLOW or executes policy."""
    if type(global_allow) is not bool or type(local_block) is not bool:
        return "POLICY_UNRESOLVED","INDETERMINATE"
    if not global_allow and not local_block:
        return "GLOBAL_BLOCK_LOCAL_NONBLOCK_CONFLICT","BLOCK_REQUIRED"
    if global_allow and local_block:
        return "LOCAL_STRICTER_THAN_GLOBAL","BLOCK_REQUIRED"
    return "POLICY_CONSISTENT",("BLOCK_REQUIRED" if local_block or not global_allow
                                else "NO_BLOCK_FROM_THIS_RULE")

def disposition(row):
    status=row["status"]
    if status=="SYMBOL_MISSING":
        return ("CATALOG_EVIDENCE_REQUIRED" if row["rule_id"] in
                ("ACTUATION_COMPONENT_MODEL","DESCRIPTION_ACTUATOR_MODEL")
                else "IDENTITY_REVIEW")
    if status in ("WRONG_TARGET","INVALID_REFERENCE"):return "PATH_ROLE_REVIEW"
    if status in ("TARGET_MISSING","TARGET_UNCLASSIFIED","TARGET_NOT_APPLICABLE"):
        return "PROFILE_DEPENDENCY_REVIEW"
    return "FRAGMENT_REVIEW"

def group_references(report):
    groups={}
    for row in report["references"]:
        if row["status"]=="RESOLVED":continue
        key=(row["rule_id"],row["status"],row["target_path"],row["target_symbol"])
        if key not in groups:
            groups[key]={"rule_id":key[0],"status":key[1],"target_path":key[2],
                         "target_symbol":key[3],"disposition":disposition(row),
                         "occurrences":0,"source_locations":[]}
        g=groups[key];g["occurrences"]+=1
        g["source_locations"].append({"path":row["source_path"],"pointer":row["source_pointer"]})
    return [groups[k] for k in sorted(groups,key=lambda x:tuple("" if v is None else v for v in x))]

def component(report,path):
    return next((x for x in report["components"] if x["path"]==path),None)

def scope(report,path):
    row=component(report,path)
    return row["inventory_status"] if row is not None else (
        "OUT_OF_SCOPE" if report["evaluation_status"]=="ASSESSED" else "NOT_ASSESSED")

def absent_status(s):
    if s=="NOT_APPLICABLE_ABSENT":return "NOT_APPLICABLE"
    if s=="OPTIONAL_ABSENT":return "ABSENT_OPTIONAL"
    # An omitted classification is not automatically an explicit exclusion.
    return "BLOCKED"

def document(report,spec,path):
    """Return a covered applicable document after exact raw-byte binding."""
    row=component(report,path)
    if row is None or row["inventory_status"] not in APPLICABLE or row["fragment_status"]!="PASS":
        return None
    entries=[x for x in report["source_assessment"]["raw_file_commitments"] if x["path"]==path]
    sc.require(len(entries)==1,"SNAPSHOT_BINDING_FAILED")
    raw=source.read_regular(spec/path,source.MAX_FILE)
    entry=entries[0]
    sc.require(source.sha(raw)==entry["raw_sha256"] and len(raw)==entry["size_bytes"],"SNAPSHOT_BINDING_FAILED")
    _,_,obj=source.parse_conservative(raw)
    sc.require(sc.validator(sc.DOCS[2],sc.FRAGMENTS[path]).is_valid(obj),"SNAPSHOT_BINDING_FAILED")
    return obj,raw

def runtime_review(report,spec):
    s=scope(report,sc.RUNTIME)
    if s not in APPLICABLE:
        return s,absent_status(s),[]
    loaded=document(report,spec,sc.RUNTIME)
    if loaded is None:return s,"BLOCKED",[]
    obj,_=loaded
    rows=[]
    counts={}
    for item in obj["pre_flight_checks_list"]:
        cid=item["check_id_str"];counts[cid]=counts.get(cid,0)+1
    for i,check in enumerate(obj["pre_flight_checks_list"]):
        cid=check["check_id_str"]
        severity=check["severity_enum"]
        global_policy=obj["severity_policies_map"].get(severity)
        allow=None if global_policy is None else global_policy["allow_motion_bool"]
        block=check["on_failure_policy"]["block_motion_bool"]
        status,constraint=declared_failure_policy(allow,block)
        if counts[cid]>1:status,constraint="POLICY_UNRESOLVED","INDETERMINATE"
        rows.append({"check_id":cid,"source_pointer":sc.pointer("pre_flight_checks_list",i),
                     "severity":severity,"global_allow_motion":allow,"local_block_motion":block,
                     "review_status":status,"declared_failure_constraint":constraint,
                     "runtime_evaluated":False,"grants_authority":False})
    # Empty declarations provide no check to evaluate, not assurance of safety.
    return s,("ASSESSED" if rows else "BLOCKED"),rows

def empty_commitment(report,profile):
    return {"scope":scope(report,sc.CALIBRATION),"selected_digest_profile":profile,
            "status":"NOT_ASSESSED","description_path":None,"declared_sha256":None,
            "observed_raw_description_sha256":None,"profile_model_hash_bound":False,
            "physical_calibration_certified":False,"grants_authority":False}

def description_review(report,spec,profile):
    r=empty_commitment(report,profile)
    if r["scope"] not in APPLICABLE:
        r["status"]=absent_status(r["scope"]);return r
    loaded=document(report,spec,sc.CALIBRATION)
    if loaded is None:r["status"]="BLOCKED";return r
    cal,_=loaded
    meta=cal["meta_group"]
    declared=meta["target_description_hash_str"]
    path=meta["target_description_ref_str"]
    r["description_path"]=path;r["declared_sha256"]=declared
    # Reuse the exact 01B typed relationship: no alias or guessed file.
    links=[x for x in report["references"] if x["rule_id"]=="CALIBRATION_DESCRIPTION"
           and x["source_path"]==sc.CALIBRATION]
    if len(links)!=1 or links[0]["status"]!="RESOLVED" or path!=sc.DESCRIPTION:
        r["status"]="BLOCKED";return r
    desc=document(report,spec,sc.DESCRIPTION)
    if desc is None:r["status"]="BLOCKED";return r
    r["observed_raw_description_sha256"]=source.sha(desc[1])
    if declared==sc.EMPTY_DIGEST:r["status"]="PLACEHOLDER"
    elif profile==LEGACY:r["status"]="UNQUALIFIED"
    else:r["status"]="MATCH" if declared==r["observed_raw_description_sha256"] else "MISMATCH"
    return r

def base(report,profile):
    return {"schema_version":"openrgd.foundation-consistency-report.v0.1-candidate",
            "policy_profile":"OPENRGD_FOUNDATION_CONSISTENCY_V0.1_CANDIDATE",
            "source_conformance_sha256":source.sha(sc.encoded(report)),
            "source_conformance":report,"evaluation_status":"BLOCKED","review_status":"BLOCKED",
            "reference_groups":group_references(report),"runtime_policy_scope":scope(report,sc.RUNTIME),
            "runtime_policy_status":"BLOCKED","runtime_policy_rows":[],
            "description_commitment":empty_commitment(report,profile),
            "snapshot_binding_verified":False,"canonical_schema_validated":False,
            "semantic_consistency_validated":False,"runtime_evaluated":False,"physical_binding_verified":False,
            "profile_model_hash_bound":False,"physical_calibration_certified":False,
            "publication_committed":False,"actuation_enabled":False,"grants_authority":False}

def checked(report):
    sc.require(VALIDATOR.is_valid(report),"CONSISTENCY_REPORT_SCHEMA")
    return report

def review_consistency(bundle,profile_raw,description_digest_profile=LEGACY):
    sc.require(description_digest_profile in (LEGACY,RAW),"UNSUPPORTED_DESCRIPTION_DIGEST_PROFILE")
    profile,policy=sc.parse_profile(profile_raw) # validate external input before touching source
    with tempfile.TemporaryDirectory(prefix="rgd-foundation-review-") as tmp:
        try:spec=source.snapshot_spec(bundle,tmp)
        except (source.AssessmentError,OSError) as e:
            # Preserve the original failure diagnostic using the existing
            # 01A/B constructors. Never reopen the original input on failure.
            projected=sc.projection(profile,policy)
            a=source.base_report(source.parse_requirements(projected),projected)
            code=str(e) if isinstance(e,source.AssessmentError) else "SOURCE_READ_FAILED"
            a["input_status"]="SOURCE_TREE_UNAVAILABLE" if code=="SOURCE_TREE_UNAVAILABLE" else "SNAPSHOT_REJECTED"
            source.diag(a,code)
            report=sc.checked_report(sc.base(profile,profile_raw,a))
            return checked(base(report,description_digest_profile))
        report=sc.assess_conformance(spec,profile_raw)
        r=base(report,description_digest_profile)
        if report["evaluation_status"]!="ASSESSED":return checked(r)
        try:
            # Bind every indexed byte of the frozen outer copy, not just the
            # two policy documents; no re-open of the caller's original source.
            a=report["source_assessment"]
            entries=a["raw_file_commitments"]
            indexed={x["path"] for x in a["source_index"]["files"]}
            sc.require(len(entries)==len(indexed) and {x["path"] for x in entries}==indexed,
                       "SNAPSHOT_BINDING_FAILED")
            for entry in entries:
                path=entry["path"]
                sc.require(source.source_path(path),"SNAPSHOT_BINDING_FAILED")
                raw=source.read_regular(spec/path,source.MAX_FILE)
                sc.require(source.sha(raw)==entry["raw_sha256"] and len(raw)==entry["size_bytes"],
                           "SNAPSHOT_BINDING_FAILED")
            s,rt,rows=runtime_review(report,spec)
            commitment=description_review(report,spec,description_digest_profile)
        except (sc.ConformanceError,source.AssessmentError,OSError):
            return checked(r)
        r.update(evaluation_status="ASSESSED",snapshot_binding_verified=True,
                 runtime_policy_scope=s,runtime_policy_status=rt,runtime_policy_rows=rows,
                 description_commitment=commitment)
        clear=(sc.passes_scoped_checks(report)
               and rt in ("ASSESSED","NOT_APPLICABLE","ABSENT_OPTIONAL")
               and all(row["review_status"] in ("POLICY_CONSISTENT","LOCAL_STRICTER_THAN_GLOBAL") for row in rows)
               and commitment["status"] in ("MATCH","NOT_APPLICABLE","ABSENT_OPTIONAL"))
        r["review_status"]="SCOPED_CLEAR" if clear else "REVIEW_REQUIRED"
        return checked(r)

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle",type=Path,required=True)
    ap.add_argument("--profile",type=Path,required=True)
    ap.add_argument("--description-digest-profile",choices=(LEGACY,RAW),default=LEGACY)
    args=ap.parse_args(argv)
    try:
        r=review_consistency(args.bundle,source.read_regular(args.profile,source.MAX_POLICY),
                             args.description_digest_profile)
    except (sc.ConformanceError,source.AssessmentError,OSError):
        print("FOUNDATION_CONSISTENCY_INPUT_REJECTED",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True,ensure_ascii=True,allow_nan=False))
    return 0 if r["review_status"]=="SCOPED_CLEAR" else 2

if __name__=="__main__":raise SystemExit(main())
