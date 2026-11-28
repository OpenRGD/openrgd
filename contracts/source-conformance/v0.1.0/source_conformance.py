"""CORE-CAL-01B scoped static conformance, never a safety or installation gate."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

ROOT=Path(__file__).resolve().parent
A_ROOT=ROOT.parents[1]/"source-assessment/v0.1.0"
sys.path.insert(0,str(A_ROOT))
import assessment as source

RULE_PROFILE="OPENRGD_STATIC_REFERENCE_RULES_V0.1_CANDIDATE"
MANIFEST="manifest.jsonc"
KERNEL="00_core/kernel.jsonc"
MASTER="rgd_schema.jsonc"
DESCRIPTION="01_foundation/description.jsonc"
LIBRARY="01_foundation/actuation_library.jsonc"
TOPOLOGY="01_foundation/actuation_topology.jsonc"
CALIBRATION="01_foundation/calibration.jsonc"
FIDELITY="01_foundation/sensor_fidelity.jsonc"
HAL="01_foundation/hal_mapping.jsonc"
RUNTIME="02_operation/runtime_validation.jsonc"
FRAGMENTS={MANIFEST:"Manifest",KERNEL:"Kernel",DESCRIPTION:"Description",
           LIBRARY:"ActuationLibrary",TOPOLOGY:"ActuationTopology",CALIBRATION:"Calibration",
           FIDELITY:"SensorFidelity",HAL:"HAL",RUNTIME:"RuntimeValidation"}
EMPTY_DIGEST="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
IDENT=re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,159}")
MAX_REFERENCES=2048

class ConformanceError(ValueError):
    """Fixed diagnostic; no grant."""

def no_retrieval(uri):
    raise NoSuchResource(ref=uri)

DOCS=[json.loads(p.read_bytes()) for p in (
    A_ROOT/"schemas/source-assessment.schema.json",
    ROOT/"schemas/source-conformance.schema.json",
    ROOT/"schemas/component-fragments.schema.json")]
for doc in DOCS:
    Draft202012Validator.check_schema(doc)
REGISTRY=Registry(retrieve=no_retrieval).with_resources(
    (doc["$id"],Resource.from_contents(doc)) for doc in DOCS)

def validator(doc,kind):
    return Draft202012Validator({"$ref":doc["$id"]+"#/$defs/"+kind},registry=REGISTRY)

def encoded(value):
    return (json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,
                       separators=(",",":"))+"\n").encode("utf-8")

def require(ok,code):
    if not ok:raise ConformanceError(code)

def parse_profile(raw):
    try:
        require(type(raw) is bytes and 0<len(raw)<=source.MAX_POLICY,"PROFILE_BYTES")
        p=source.parse_object(source.decode_text(raw))
        require(validator(DOCS[1],"ConformanceProfile").is_valid(p),"PROFILE_SCHEMA")
        paths=[x["path"] for x in p["components"]]
        require(all(source.source_path(x) for x in paths),"PROFILE_PATH_INVALID")
        require(len(paths)==len({x.casefold() for x in paths}),"PROFILE_PATH_DUPLICATE")
        policy={x["path"]:x["applicability"] for x in p["components"]}
        require(policy.get(MANIFEST)=="REQUIRED","PROFILE_MANIFEST_REQUIRED")
        require(all(x["rationale"].strip() for x in p["components"]),"PROFILE_RATIONALE_REQUIRED")
        return p,policy
    except source.AssessmentError as e:
        raise ConformanceError("PROFILE_JSON") from e

def projection(p,policy):
    return encoded({"schema_version":"openrgd.required-source-profile.v0.1-candidate",
        "profile_id":p["profile_id"],"profile_version":p["profile_version"],
        "standard_version":p["standard_version"],
        "required_paths":sorted(k for k,v in policy.items() if v=="REQUIRED")})

def base(p,raw,a):
    return {"schema_version":"openrgd.source-conformance-report.v0.1-candidate",
        "rule_profile":RULE_PROFILE,"profile_id":p["profile_id"],
        "profile_version":p["profile_version"],"profile_sha256":source.sha(raw),
        "source_assessment_sha256":source.sha(encoded(a)),"source_assessment":a,
        "evaluation_status":"SOURCE_UNAVAILABLE","inventory_status":"NOT_ASSESSED",
        "fragment_schema_status":"NOT_ASSESSED","reference_status":"NOT_ASSESSED",
        "review_findings_status":"NOT_ASSESSED","components":[],"references":[],"findings":[],
        "canonical_schema_validated":False,"semantic_consistency_validated":False,
        "profile_governance_accepted":False,"publisher_verified":False,"robot_binding_verified":False,
        "profile_model_hash_bound":False,"physical_calibration_certified":False,
        "actuation_enabled":False,"grants_authority":False}

def checked_report(r):
    require(validator(DOCS[1],"ConformanceReport").is_valid(r),"REPORT_SCHEMA")
    return r

def pointer(*parts):
    return "/"+"/".join(str(x).replace("~","~0").replace("/","~1") for x in parts)

def inventory(policy,indexed):
    rows=[]
    for path in sorted(set(policy)|indexed):
        app=policy.get(path,"UNCLASSIFIED")
        present=path in indexed
        status={"REQUIRED":("REQUIRED_PRESENT","REQUIRED_MISSING"),
                "OPTIONAL":("OPTIONAL_PRESENT","OPTIONAL_ABSENT"),
                "NOT_APPLICABLE":("NOT_APPLICABLE_PRESENT","NOT_APPLICABLE_ABSENT"),
                "UNCLASSIFIED":("UNCLASSIFIED_PRESENT","UNCLASSIFIED_PRESENT")}[app][0 if present else 1]
        rows.append({"path":path,"applicability":app,"present":present,
                     "inventory_status":status,"fragment_status":"NOT_ASSESSED"})
    return rows

FOUNDATION_TARGETS={n+"_file_ref_str":"01_foundation/"+n+".jsonc" for n in (
    "description","calibration","compute_topology","power_distribution","actuation_library",
    "actuation_topology","actuation_dynamics","firmware_mapping","hal_mapping","physics_solver_overrides",
    "soft_materials_library","soft_body_dynamics","surface_properties","sensor_fidelity",
    "sensor_health_monitor","wear_fatigue_model")}
FIDELITY_TARGETS={"description_ref_str":DESCRIPTION,"calibration_ref_str":CALIBRATION,
                  "hal_mapping_ref_str":HAL,"runtime_validation_ref_str":RUNTIME}
ENGINE_FILE_TARGETS={
    "hardware_runtime_profile_engine":{k+"_ref_str":"01_foundation/"+k+".jsonc" for k in
        ("compute_topology","power_distribution","hal_mapping","firmware_mapping")},
    "simulation_profile_engine":{k+"_ref_str":"01_foundation/"+k+".jsonc" for k in
        ("physics_solver_overrides","soft_materials_library","soft_body_dynamics","surface_properties")},
    "perception_health_engine":{k+"_ref_str":"01_foundation/"+k+".jsonc" for k in
        ("sensor_fidelity","sensor_health_monitor")},
    "actuation_envelope_engine":{k+"_ref_str":"01_foundation/"+k+".jsonc" for k in
        ("actuation_library","actuation_topology","actuation_dynamics")},
    "wear_budget_engine":{"wear_fatigue_model_ref_str":"01_foundation/wear_fatigue_model.jsonc"},
    "volition_orchestra_engine":{k+"_ref_str":"04_volition/"+k+".jsonc" for k in
        ("alignment","orchestra","social_synergy","ledger")},
    "safety_supervisor":{"alignment_invariants_ref_str":"04_volition/alignment.jsonc",**{
        k+"_ref_str":"01_foundation/"+k+".jsonc" for k in
        ("surface_properties","sensor_health_monitor","power_distribution","wear_fatigue_model")}}
}
PRECHECK_SECTIONS=set(ENGINE_FILE_TARGETS)

class Checker:
    """Closed rule families, exact indexed file and local symbol namespaces."""
    def __init__(self,rows,docs,r):
        self.rows={x["path"]:x for x in rows}
        self.docs=docs
        self.r=r
        self.blocked=False
        self.limit=False
    def finding(self,code,path=None,loc=None):
        row={"code":code,"path":path,"pointer":loc}
        if row not in self.r["findings"]:
            require(len(self.r["findings"])<2048,"FINDING_LIMIT")
            self.r["findings"].append(row)
    def result(self,rule,origin,loc,target,symbol,status):
        if len(self.r["references"])>=MAX_REFERENCES:
            self.limit=True
            self.finding("REFERENCE_CHECK_LIMIT")
            return
        self.r["references"].append({"rule_id":rule,"source_path":origin,"source_pointer":loc,
            "target_path":target,"target_symbol":symbol,"status":status})
    def target_status(self,path):
        row=self.rows.get(path)
        if row is None or row["applicability"]=="UNCLASSIFIED":return "TARGET_UNCLASSIFIED"
        if row["applicability"]=="NOT_APPLICABLE":return "TARGET_NOT_APPLICABLE"
        if not row["present"]:return "TARGET_MISSING"
        if path not in self.docs or row["fragment_status"]=="FAIL":return "TARGET_FRAGMENT_INVALID"
        return "RESOLVED"
    def file(self,rule,origin,loc,value,expected=None):
        if not source.source_path(value) or not value.endswith(".jsonc"):
            self.result(rule,origin,loc,None,None,"INVALID_REFERENCE");return
        state=self.target_status(value)
        if expected is not None and value!=expected:
            state="WRONG_TARGET"
        self.result(rule,origin,loc,value,None,state)
    def symbol(self,rule,origin,loc,target,ns,value):
        if not isinstance(value,str) or not IDENT.fullmatch(value):
            self.result(rule,origin,loc,target,None,"INVALID_REFERENCE");return
        state=self.target_status(target)
        if state=="RESOLVED":
            table=self.docs[target].get(ns)
            if not isinstance(table,dict):state="TARGET_FRAGMENT_INVALID"
            elif value not in table:state="SYMBOL_MISSING"
        self.result(rule,origin,loc,target,value,state)
    def refmap(self,rule,origin,loc,table,expected=None):
        for k,v in sorted(table.items()):
            self.file(rule,origin,loc+"/"+k,v,None if expected is None else expected.get(k))
    def rowsymbols(self,rule,origin,table,field,target,ns):
        for k,row in sorted(self.docs[origin][table].items()):
            self.symbol(rule,origin,pointer(table,k,field),target,ns,row[field])
    def keysymbols(self,rule,origin,table,target,ns,skip=()):
        for k in sorted(self.docs[origin][table]):
            if k not in skip:self.symbol(rule,origin,pointer(table,k),target,ns,k)
    def run(self):
        def applicable(p):
            row=self.rows.get(p)
            return row is not None and row["present"] and row["applicability"] in ("REQUIRED","OPTIONAL")
        for p in sorted(FRAGMENTS):
            if applicable(p) and self.rows[p]["fragment_status"]!="PASS":self.blocked=True
        def covered(p):return applicable(p) and self.rows[p]["fragment_status"]=="PASS"
        if covered(MANIFEST):
            m=self.docs[MANIFEST]["meta_group"]
            self.file("MANIFEST_KERNEL",MANIFEST,pointer("meta_group","kernel_ref_str"),m["kernel_ref_str"],KERNEL)
            self.file("MANIFEST_SCHEMA",MANIFEST,pointer("meta_group","rgd_schema_ref_str"),m["rgd_schema_ref_str"],MASTER)
        if covered(KERNEL):
            k=self.docs[KERNEL];seen=set()
            for i,v in enumerate(k["module_loading_order_list"]):
                loc=pointer("module_loading_order_list",i)
                if v in seen:self.result("KERNEL_MODULE",KERNEL,loc,v if source.source_path(v) else None,None,"DUPLICATE_REFERENCE")
                elif v in (KERNEL,MANIFEST,MASTER):self.result("KERNEL_MODULE",KERNEL,loc,v,None,"WRONG_TARGET")
                else:self.file("KERNEL_MODULE",KERNEL,loc,v)
                seen.add(v)
            if "foundation_introspection" in k:
                self.refmap("KERNEL_FOUNDATION_FILE",KERNEL,pointer("foundation_introspection"),
                            k["foundation_introspection"],FOUNDATION_TARGETS)
            for section,fields in sorted(ENGINE_FILE_TARGETS.items()):
                if section not in k:continue
                # Optional engine sections have a typed field contract when present.
                for field,expected in sorted(fields.items()):
                    v=k[section].get(field) if isinstance(k[section],dict) else None
                    self.file("KERNEL_ENGINE_FILE",KERNEL,pointer(section,field),v,expected)
            if "execution_pipeline" in k:
                seen=set()
                for i,engine in enumerate(k["execution_pipeline"]["pre_checks_list"]):
                    status=("DUPLICATE_REFERENCE" if engine in seen else
                            "RESOLVED" if engine in PRECHECK_SECTIONS and isinstance(k.get(engine),dict)
                            else "SYMBOL_MISSING")
                    self.result("KERNEL_PRECHECK",KERNEL,pointer("execution_pipeline","pre_checks_list",i),KERNEL,engine,status)
                    seen.add(engine)
        if covered(DESCRIPTION):
            self.rowsymbols("DESCRIPTION_ACTUATOR_JOINT",DESCRIPTION,"actuators_topology_map",
                            "drives_joint_ref_str",DESCRIPTION,"joint_topology_map")
            self.rowsymbols("DESCRIPTION_ACTUATOR_MODEL",DESCRIPTION,"actuators_topology_map",
                            "component_model_ref_str",LIBRARY,"component_catalog_map")
        if covered(TOPOLOGY):
            for rule,field,target,ns in (
                ("ACTUATION_TARGET_JOINT","target_joint_ref_str",DESCRIPTION,"joint_topology_map"),
                ("ACTUATION_COMPONENT_MODEL","component_model_ref_str",LIBRARY,"component_catalog_map"),
                ("ACTUATION_CONTROL_PROFILE","use_profile_ref_str",TOPOLOGY,"control_profiles_map")):
                self.rowsymbols(rule,TOPOLOGY,"joint_actuator_mapping_map",field,target,ns)
        if covered(CALIBRATION):
            m=self.docs[CALIBRATION]["meta_group"]
            self.file("CALIBRATION_DESCRIPTION",CALIBRATION,pointer("meta_group","target_description_ref_str"),
                      m["target_description_ref_str"],DESCRIPTION)
            for rule,table,ns,skip in (
                ("CALIBRATION_KINEMATIC_JOINT","kinematic_offsets_map","joint_topology_map",()),
                ("CALIBRATION_EXTRINSIC_SENSOR","sensor_extrinsics_delta_map","sensors_mounting_map",()),
                ("CALIBRATION_INTRINSIC_SENSOR","sensor_intrinsics_map","sensors_mounting_map",()),
                ("CALIBRATION_DYNAMICS_JOINT","dynamics_correction_map","joint_topology_map",("global_body",))):
                self.keysymbols(rule,CALIBRATION,table,DESCRIPTION,ns,skip)
            if m["target_description_hash_str"]==EMPTY_DIGEST:
                self.finding("LEGACY_DESCRIPTION_DIGEST_PLACEHOLDER",CALIBRATION,pointer("meta_group","target_description_hash_str"))
        if covered(FIDELITY):
            self.refmap("FIDELITY_RELATED_FILE",FIDELITY,pointer("meta_group","related_files_map"),
                        self.docs[FIDELITY]["meta_group"]["related_files_map"],FIDELITY_TARGETS)
            self.keysymbols("FIDELITY_SENSOR",FIDELITY,"sensor_error_profiles_map",DESCRIPTION,"sensors_mounting_map")
        if covered(HAL):
            self.rowsymbols("HAL_ACTUATOR",HAL,"actuator_drivers_map","logical_actuator_ref_str",DESCRIPTION,"actuators_topology_map")
            self.rowsymbols("HAL_SENSOR",HAL,"sensor_drivers_map","logical_sensor_ref_str",DESCRIPTION,"sensors_mounting_map")
            for table in ("actuator_drivers_map","sensor_drivers_map"):
                self.rowsymbols("HAL_QOS_PROFILE",HAL,table,"qos_profile_ref_str",HAL,"qos_profiles_map")
        if covered(RUNTIME):
            obj=self.docs[RUNTIME];seen=set()
            for i,row in enumerate(obj["pre_flight_checks_list"]):
                loc=pointer("pre_flight_checks_list",i);cid=row["check_id_str"]
                if cid in seen:self.result("RUNTIME_CHECK_ID",RUNTIME,loc+"/check_id_str",RUNTIME,cid,"DUPLICATE_REFERENCE")
                seen.add(cid)
                self.refmap("RUNTIME_PREFLIGHT_SOURCE",RUNTIME,loc+"/sources_ref_map",row["sources_ref_map"])
                self.symbol("RUNTIME_SEVERITY",RUNTIME,loc+"/severity_enum",RUNTIME,"severity_policies_map",row["severity_enum"])
                policy=obj["severity_policies_map"].get(row["severity_enum"])
                if policy is None:self.finding("SEVERITY_REFERENCE_UNRESOLVED",RUNTIME,loc+"/severity_enum")
                elif row["on_failure_policy"]["block_motion_bool"] is False and policy["allow_motion_bool"] is False:
                    self.finding("DECLARED_MOTION_POLICY_CONFLICT",RUNTIME,loc+"/on_failure_policy/block_motion_bool")
        self.r["reference_status"]=("FAIL" if self.limit or any(x["status"]!="RESOLVED" for x in self.r["references"])
                                   else "BLOCKED" if self.blocked else "PASS")

def assess_conformance(bundle,profile_raw):
    p,policy=parse_profile(profile_raw)
    projected=projection(p,policy)
    with tempfile.TemporaryDirectory(prefix="rgd-source-conformance-") as tmp:
        try:spec=source.snapshot_spec(bundle,tmp)
        except (source.AssessmentError,OSError) as e:
            a=source.base_report(source.parse_requirements(projected),projected)
            code=str(e) if isinstance(e,source.AssessmentError) else "SOURCE_READ_FAILED"
            a["input_status"]="SOURCE_TREE_UNAVAILABLE" if code=="SOURCE_TREE_UNAVAILABLE" else "SNAPSHOT_REJECTED"
            source.diag(a,code)
            return checked_report(base(p,profile_raw,a))
        # 01A makes a private copy of the stable outer snapshot. Never reopen
        # original inputs; bind all bytes used for rules to 01A commitments.
        a=source.assess_source(spec,projected)
        r=base(p,profile_raw,a)
        if a["source_index"] is None:return checked_report(r)
        if a["declared_standard_version"]!=p["standard_version"]:
            r["evaluation_status"]="PROFILE_VERSION_MISMATCH";return checked_report(r)
        indexed={x["path"] for x in a["source_index"]["files"]}
        commitments={x["path"]:x for x in a["raw_file_commitments"]}
        docs={};syntax_bad=set()
        try:
            require(indexed==set(commitments) and len(indexed)==len(a["raw_file_commitments"])
                    and len(indexed)==len(a["source_index"]["files"]),"SNAPSHOT_BINDING_FAILED")
            for path in sorted(indexed):
                require(source.source_path(path),"SNAPSHOT_BINDING_FAILED")
                raw=source.read_regular(spec/path,source.MAX_FILE);entry=commitments[path]
                require(source.sha(raw)==entry["raw_sha256"] and len(raw)==entry["size_bytes"],"SNAPSHOT_BINDING_FAILED")
                if path.endswith(".jsonc"):
                    try:_,_,docs[path]=source.parse_conservative(raw)
                    except source.AssessmentError:syntax_bad.add(path)
        except (ConformanceError,source.AssessmentError,OSError):
            r["evaluation_status"]="SNAPSHOT_BINDING_FAILED"
            r["findings"]=[{"code":"SNAPSHOT_BINDING_FAILED","path":None,"pointer":None}]
            return checked_report(r)
        rows=inventory(policy,indexed)
        r.update(evaluation_status="ASSESSED",components=rows,
                 inventory_status="FAIL" if any(x["inventory_status"] in
                   ("REQUIRED_MISSING","NOT_APPLICABLE_PRESENT","UNCLASSIFIED_PRESENT") for x in rows) else "PASS")
        checker=Checker(rows,docs,r)
        for row in rows:
            path=row["path"]
            if not row["present"] or row["applicability"] not in ("REQUIRED","OPTIONAL"):continue
            if path in syntax_bad:
                row["fragment_status"]="FAIL";checker.finding("INDEXED_SYNTAX_INVALID",path)
            elif path not in FRAGMENTS:row["fragment_status"]="NOT_COVERED"
            elif not validator(DOCS[2],FRAGMENTS[path]).is_valid(docs[path]):
                row["fragment_status"]="FAIL";checker.finding("FRAGMENT_SCHEMA_INVALID",path)
            else:row["fragment_status"]="PASS"
        r["fragment_schema_status"]=("FAIL" if any(x["fragment_status"]=="FAIL" for x in rows)
                                     else "PASS" if any(x["fragment_status"]=="PASS" for x in rows) else "NOT_ASSESSED")
        checker.run()
        r["review_findings_status"]="FOUND" if r["findings"] else "NONE"
        return checked_report(r)

def passes_scoped_checks(r):
    return (r["evaluation_status"]=="ASSESSED" and source.passes_requested_checks(r["source_assessment"])
            and r["inventory_status"]==r["fragment_schema_status"]==r["reference_status"]=="PASS"
            and r["review_findings_status"]=="NONE")

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle",type=Path,required=True)
    ap.add_argument("--profile",type=Path,required=True)
    args=ap.parse_args(argv)
    try:r=assess_conformance(args.bundle,source.read_regular(args.profile,source.MAX_POLICY))
    except (ConformanceError,source.AssessmentError,OSError):
        print("SOURCE_CONFORMANCE_INPUT_REJECTED",file=sys.stderr);return 2
    print(json.dumps(r,sort_keys=True,ensure_ascii=True,allow_nan=False))
    return 0 if passes_scoped_checks(r) else 2

if __name__=="__main__":
    raise SystemExit(main())
