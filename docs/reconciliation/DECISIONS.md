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
**Decision:** Quarantine the incomplete bundled ROS 2/Viam runtime and retain `rgd run` only as a deterministic fail-closed compatibility/status boundary. Physical execution belongs in an independent embodied runtime and body adapter.

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
**Decision:** Remove the MSIX placeholder because it referenced an absent dummy executable and missing Assets. A future shell-integration package must be complete, built and tested before being tracked.
