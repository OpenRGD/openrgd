# CORE-CAL-01B — Explicit source conformance profiles and internal references

**2026-11-28 · candidate · non-normative · non-actuating.** Stacked on Core [#22](https://github.com/OpenRGD/openrgd/pull/22) exact `ecb970e97ae9f8a86428b26ad67aa00f5dad1c08` (CORE-CAL-01A); underlying unchanged Core main `afe1a831b950a4e6560f0285a0103fc4eaa343b7`, OpenRGD Standard draft 0.2.0, toolchain 0.1.1. Responds to [CAL-021-C](https://github.com/OpenRGD/rgd-calibration/blob/646dbc05bcefd15942b25bb55b3c99096f0cccc9/docs/handoffs/CAL-021-C-TO-CORE.md). No new runtime, installer, accepted standard, source repair or CAL binding.

## 1. Conformance is relative to an independently selected profile

`ConformanceProfile` identifies a versioned profile, supported standard version, fixed versioned reference-rule set and explicit inventory. The exact raw profile digest is included in every report. The operator/consumer must select and review the policy independently of the submitted source; the model cannot self-certify by changing its manifest, kernel, domain flags or a claimed profile identifier. No inference of profile authority from name, JSON schema or digest. This initial profile supports **standard 0.2.0 only**.

One classification for every in-scope path:

| Applicability | Absent | Present |
|---|---|---|
| REQUIRED | REQUIRED_MISSING (fail) | REQUIRED_PRESENT; evaluate covered checks |
| OPTIONAL | OPTIONAL_ABSENT (permitted if unreferenced) | OPTIONAL_PRESENT; same covered checks as required |
| NOT_APPLICABLE | NOT_APPLICABLE_ABSENT | NOT_APPLICABLE_PRESENT (profile conflict) |
| UNCLASSIFIED | no record | UNCLASSIFIED_PRESENT (explicit inventory missing; fail) |

NOT_APPLICABLE is a deliberate profile exclusion (must be absent in this initial strict profile), not a missing file, disabled process, unknown hardware condition, or permission. Require an explicit nonempty rationale for every classification. Never use it to suppress a reference: an applicable document referencing an excluded file fails even if that file exists. Optional means not required by inventory, not a license to keep dangling references. Exact case-sensitive POSIX indexed source paths only. No alias, symlink, guessed stem, extension conversion or arbitrary URI resolution. Duplicate paths, casefold collisions and invalid profile rejected. A valid profile may be intentionally minimal: the report is only about that scope, not global validity.

The BHL reference fixture classifies the 76 actual indexed paths: 30 kernel-selected modules plus manifest, kernel, master meta-schema, runtime_validation and safety_critical are 35 required paths chosen **for this review**; remaining 41 optional. None marked NOT_APPLICABLE because the current source includes them. This inventory is test evidence, not a universal requirement list, claim of complete BHL hardware or normative policy. Missing optional but actually referenced paths still fail the reference check. Other profiles may exclude modules with explicit rationale; no inference from robot embodiment. Changes require a new reviewed profile revision; no global profile publication/version ledger implemented.

## 2. Layered report, same stable input

The tool reuses 01A's bounded snapshot, exact Core hash, parser, raw file commitments and required-path projection. One external profile is authored; the list of REQUIRED paths for 01A is generated, not separately edited. The original bundle is copied once; 01A takes its own private copy of that stable outer snapshot. All rule input bytes are checked against the exact raw indexed-file commitments returned by 01A before parsing. Never reopen the original source, never compute a second canonical root. Trust assumptions of 01A remain: trusted interpreter, reviewed checkout, stable operator-controlled source and temporary storage; not a hostile filesystem sandbox.

Report binds profile digest and deterministic local encoding of the nested SourceAssessment. Local JSON encoding is not a signing format. Integrity can MATCH while inventory, fragment structure, references or review findings fail. MISMATCH still permits scoped diagnostics on the computed indexed bytes, but no successful CLI exit. Unsupported standard version or unavailable/unbound index blocks evaluation, not a false clean result. Full schema, semantic consistency, provenance, robot/Life/body identity, legacy CAL model hash binding and physical calibration remain explicitly false. No authority, runtime readiness, installation, grant or physical execution.

## 3. Scoped structural schemas and typed reference families

The actual master `rgd_schema.jsonc` expressly calls itself a meta-schema, not a strict field validator. Do not feed it to JSON Schema and declare the model compliant. Instead, nine **open component fragments** check required fields and types of the documented subset only; unknown fields are not rejected by these fragments. Each applicable present component reports PASS/FAIL/NOT_COVERED, with NOT_ASSESSED for absent/excluded/unclassified paths. NOT_COVERED is not validated, even when the scoped check succeeds. No global schema or all-reference claim.

| Source | Checked namespace / rule family |
|---|---|
| manifest | canonical exact kernel and master source paths |
| kernel | module-loading list (duplicate and self/metadata target rejection), declared foundation file map, named engine file fields when section present, known pre-check engine names |
| description | actuator drives_joint -> description.joint_topology_map; component_model -> actuation_library.component_catalog_map |
| actuation_library | component catalog object map (fragment only) |
| actuation_topology | target_joint -> description.joint_topology_map; component_model -> library catalog; use_profile -> local control_profiles_map |
| calibration | exact description path; keys of kinematic/dynamics joint maps and extrinsics/intrinsics sensor maps -> description maps (explicit global_body sentinel excluded from joint namespace) |
| sensor_fidelity | related file map (known fields have exact expected path); keys -> description.sensors_mounting_map |
| hal_mapping | logical actuator/sensor refs -> description namespaces; QoS refs -> local qos_profiles_map |
| runtime_validation | preflight source file refs, unique check IDs and severity policy refs |

Only explicitly identified fields are checked. File-valued maps above are checked as maps of indexed JSONC paths, not generic recursive suffix inference. Exact known field-role mappings fail even if a wrong target exists. If an applicable source fragment fails, its rules are blocked; references to malformed targets fail. Missing/unclassified/excluded targets fail, no optional fallback. A file resolution to a syntactically valid applicable document outside nine fragments establishes **only indexed document presence**, not its schema validity. For symbol resolution use the exact specified map and identifier; no matching across namespaces. Maximum 2048 reported references; limit forces FAIL, not silent truncation success.

Excluded/unimplemented: remaining source schemas, link/frame topology and geometry, actuator/firmware physical identity and compatibility, full HAL/non-kinematic bindings, all external URIs, kernel legacy mirror ref (`rgd_schema.json`), mixed export lists, continuous monitor semantics, units, ranges, safety gate semantics, transitive dependency/cycle policy and cross-language numeric equivalence. Do not globally scan every *_ref_str or auto-add all missing files. These need explicit owner-reviewed contract profiles. No assumptions about which reference sample values correspond to actual Paky-01.

## 4. Findings for CORE-CAL-01C

Separately characterize the existing empty SHA-256 target_description_hash_str placeholder and preflight local block_motion=false with global severity allow_motion=false. Report findings, **do not determine precedence, change severity, infer permission, or rewrite hashes**. A nonempty digest is not qualified or matched to a physical profile. Report exact offending source JSON pointers and typed references. Actual reference BHL is expected to fail scoped checks even with preserved V1 root; any remediation requires distinct 01C change, owner review and versioned hash migration.

## 5. Candidate API and validation

Use from trusted reviewed checkout, same pinned Core dependencies and test-only jsonschema:
```bash
PYTHONPATH=src python contracts/source-conformance/v0.1.0/source_conformance.py \
  --bundle /path/to/rgd-project \
  --profile contracts/source-conformance/v0.1.0/fixtures/bhl-static-review-profile.json
```
Python `assess_conformance(bundle, profile_raw)` (bytes) returns the structured report. Invalid profile rejected before assessment; JSON stdout for completed reports, exit 0 iff all **requested scoped** checks pass including 01A, inventory, fragments, references and no review findings; exit 2 otherwise. There is no new installed CLI command or overall VALID claim. Schema validation alone does not authenticate the producer or recompute report semantics. No remote schema retrieval, file repair or physical action.

CI tests exact 01A regressions, real baseline BHL, minimal passing scoped fixtures, required/optional/exclusion/unclassified behavior, malformed and dangling references, exact policy and snapshot commitments and expected legacy conflicts. 01A's already verified actual CAL Rust exchange remains unchanged; 01B does not modify or require a migration of the CAL sidecar. No new authority and no merge.
