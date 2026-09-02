# Reconciliation Decision Register

Statuses in this register describe the reconciliation branch. `ADOPTED ON BRANCH` becomes repository policy only after review and merge.

## R-001 — Isolated reconciliation branch

**Status:** IMPLEMENTED  
**Decision:** All reconciliation changes are developed outside `main`, preserving the public baseline until review.

## R-002 — Single normative root

**Status:** ADOPTED ON BRANCH  
**Decision:** `OpenRGD/openrgd` owns the standard, schemas and cross-component interface contracts. Empty placeholder repositories are not authorities.

## R-003 — Specification authority

**Status:** ADOPTED ON BRANCH  
**Decision:** `spec/` is the human-readable source for the reference standard. `standard/`, packaged seeds and generated bundles are derived representations and must not diverge silently.

## R-004 — Independent versions

**Status:** ADOPTED ON BRANCH  
**Decision:** Standard bundle, kernel profile, Python toolchain and contract packages have independent versions.

## R-005 — Canonical domain taxonomy

**Status:** CONFIRMED FROM SPECIFICATION  
**Decision:** `00_core` coordinates `01_foundation`, `02_operation`, `03_agency`, `04_volition`, `05_evolution`, and `06_ether`. The alternate Safety/Capability/Ethics/History/Collective taxonomy is superseded.

## R-006 — Candidate contract import

**Status:** IMPLEMENTED  
**Decision:** Import the 2026 Agent Contracts into the canonical repository with their original candidate status, exact source archive hash and explicit non-retroactivity language.

## R-007 — Generated build artifacts

**Status:** IMPLEMENTED  
**Decision:** Build outputs, Python bytecode, package metadata and local archives are not source and must not be versioned.

## R-008 — Minimum Python version

**Status:** IMPLEMENTED  
**Decision:** Declare Python 3.10+ because the existing runtime uses PEP 604 unions and built-in generic annotations. Do not advertise untested Python 3.8 compatibility.

## R-009 — External component repositories

**Status:** PROPOSED  
**Decision candidate:** Physics, Chronograf, embodied runtime, LeRobot adapter and Ethics should have independent implementation repositories while consuming contracts from the canonical root. Final names remain open.

## R-010 — Historical documents

**Status:** IMPLEMENTED  
**Decision:** Preserve contradictory 2025 documents under `docs/history/`, while replacing root documentation with the reconciled view.

## R-011 — No silent implementation claims

**Status:** ADOPTED ON BRANCH  
**Decision:** A schema, placeholder file or conceptual module must not be described as a complete runtime implementation without executable evidence and validation.

## R-012 — Executable artifact authority

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Encode source/derived relationships in `ARTIFACT_POLICY.json` and enforce them through CI. Selected `spec/` leaves are normative; `standard/` must be semantically equivalent strict JSON; the packaged default seed must be byte-identical unless an approved override exists.

## R-013 — Runtime seed overrides

**Status:** ADOPTED ON BRANCH  
**Decision:** A seed-specific divergence is permitted only as an explicit `RUNTIME_PROFILE_OVERRIDE` containing a semantic reason, governance decision reference, canonical SHA-256 and seed SHA-256. Unlisted or stale differences fail CI. The current default seed has zero approved overrides.

## R-014 — Default seed convergence

**Status:** IMPLEMENTED  
**Decision:** Replace three stale default-seed copies with canonical source bytes, restore ten missing Agency/skill JSONC artifacts, archive the legacy strict-JSON skill index and remove generated unified products from the active seed.

## R-015 — Project identity personalization

**Status:** CONFIRMED / TESTED  
**Decision:** `rgd init NAME` may personalize the RGD DID in `00_core/kernel.jsonc`. It must then recalculate the canonical source root. Every other source difference must be explicit.

## R-016 — Canonical root is non-actuating

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Quarantine the incomplete bundled ROS 2/Viam runtime and retain `rgd run` only as a deterministic fail-closed compatibility/status boundary. Physical execution belongs in an independent embodied runtime and Body Adapter.

## R-017 — Generated products are not source

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Domain bundles, unified bundles, benchmark snapshots, generated robot profiles and interoperability exports must not be tracked as normative source. Reproducible products are generated on demand; historical identities are retained in the generated-artifact inventory.

## R-018 — Canonical source-tree integrity profile

**Status:** ADOPTED ON BRANCH  
**Decision:** OpenRGD standard/profile integrity uses `OPENRGD_SOURCE_TREE_SHA256_V1`. It commits exact selected source bytes and path metadata through SHA-256, normalizing only `manifest.jsonc`'s own `integrity_hash_str` to `sha256:SELF`.

## R-019 — One deterministic bundle compiler

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Replace the recursive domain/human-twin/benchmark generator lineage and the competing Node builder with one deterministic Python machine-bundle compiler. Generated output contains no wall-clock timestamp and is ignored by Git.

## R-020 — Examples require provenance and tests

**Status:** ADOPTED ON BRANCH  
**Decision:** Remove the three historical external URDF examples from the active tree. Future examples must be owned or redistribution-audited, minimal, hermetic, free of local secrets/paths and exercised by automated tests.

## R-021 — Duplicate generated workspaces

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Remove both checked-in UR5 workspaces because they share the same generated spec tree and differ only in timestamps. Local robot profiles belong outside the canonical repository source tree.

## R-022 — Strict mirror contains leaves only

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** `standard/` contains only strict-JSON equivalents of selected canonical leaves and static files. Domain/unified aggregates and benchmark copies are not allowed exceptions.

## R-023 — Incomplete packaging prototypes

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Remove the MSIX placeholder because it referenced an absent dummy executable and missing assets. A future shell-integration package must be complete, built and tested before being tracked.

## R-024 — URDF import extracts evidence; it does not create policy

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** The reconciled URDF path emits source-supported partial Foundation evidence. It must not synthesize kernel identity, constitutional alignment, safety policy, cognition or hardware authorization from absent source data.

## R-025 — Missing URDF physical values remain unknown

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** The URDF importer must not replace absent or malformed physical values with convenient torque, velocity or joint-range defaults. Non-finite values fail closed; absent values remain absent.

## R-026 — URDF source provenance is content-addressed

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Reconciled URDF evidence records source filename, format, byte count and SHA-256. Machine-local absolute paths are not part of the generated profile.

## R-027 — Seed enrichment does not prove body compatibility

**Status:** ADOPTED ON BRANCH  
**Decision:** `rgd alive` may explicitly combine imported evidence with a selected reviewed seed, personalize profile identity and recalculate integrity. The project manifest must retain `seed_compatibility_status = UNVERIFIED` until inherited physical, HAL, safety and behavioral modules are reviewed against the actual body.

## R-028 — Imported bodies cannot inherit HAL by name collision

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Static export must ignore inherited seed actuator and HAL bindings for a profile whose body description remains marked as imported partial evidence. A matching joint name is not provenance for a driver, address or interface.

## R-029 — ROS 2 Synapse is static and non-actuating

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** The active ROS 2 Synapse validates the canonical source root and compiled machine bundle, then emits deterministic configuration artifacts with an explicit completeness status. It never launches ROS 2 or authorizes execution.

## R-030 — Hardware export requires complete explicit bindings

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** `rgd_hardware.xacro` is generated only when every exported joint has explicit HAL interfaces and the exported set resolves to one system driver plugin. Otherwise export succeeds only as `CONFIGURATION_ONLY` and records missing bindings.

## R-031 — Target registry reflects implementation maturity

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** ROS 2 is the only active static-export target in this release candidate. The historical Isaac file is classified as a placeholder and removed from the active registry; `rgd export isaac` fails explicitly.

## R-032 — Owned URDF lifecycle fixture

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Admit `tests/fixtures/urdf/openrgd_minimal_arm.urdf` as a project-owned MIT test fixture. It is hermetic, non-normative and non-actuating, and exercises the mechanical lifecycle from source import through deterministic static export.

## R-033 — Text USDA is an evidence profile, not a full OpenUSD implementation

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** The active USD importer accepts only UTF-8 text USDA and implements a narrow, declared subset for directly authored stage metadata and revolute/prismatic UsdPhysics joints. It must not claim layer composition, reference/payload resolution, variant evaluation or complete OpenUSD semantics.

## R-034 — USD unit conversion requires authored evidence

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Convert revolute positions from authored degrees to radians. Convert prismatic positions to metres only when `metersPerUnit` is authored. Convert drive effort to N/Nm only when both `metersPerUnit` and `kilogramsPerUnit` are authored. Preserve raw source values independently of SI conversion.

## R-035 — USD importer does not invent physical defaults

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Missing USD values remain absent. Invalid/non-finite values, inverted limits, duplicate joint identifiers and ambiguous duplicate attributes fail closed rather than receiving convenience defaults.

## R-036 — USD joint relationships retain source semantics

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Preserve `physics:body0` and `physics:body1` as source prim-path relationships. The lightweight parser must not reinterpret them as a universal parent/child direction without a fuller composition and articulation model.

## R-037 — `rgd check` validates the static profile only

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** `check` validates the canonical source root, canonical kernel location, identity, safe and unique module references, module presence and JSONC object loading. It must explicitly state that physical execution and runtime readiness are not assessed.

## R-038 — `rgd boot` is grounding, not runtime startup

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** `boot` produces a deterministic, integrity-verified `OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT`. It does not start an embodied runtime, claim “ready” state, assess physical safety or authorize actuation.

## R-039 — Profile inspection fails closed

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** `check` and `boot` share one profile inspector. Stale source roots, unsafe or duplicate module references, missing files, invalid JSONC, non-object module roots and non-finite JSON values must cause a non-zero result rather than warnings or partial success.

## R-040 — Owned USDA lifecycle fixture

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Admit `tests/fixtures/usd/openrgd_minimal_arm.usda` as a project-owned MIT test fixture. It is hermetic, non-normative and non-actuating, and verifies stage metadata, evidence-bound unit conversion, profile inspection and deterministic static ROS 2 output.
