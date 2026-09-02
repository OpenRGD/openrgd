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
**Decision:** `spec/` is the human-readable source for the reference standard. `standard/`, packaged seeds and unified files are derived representations and must not diverge silently.

## R-004 — Independent versions

**Status:** ADOPTED ON BRANCH  
**Decision:** Standard bundle, kernel profile, Python toolchain and contract packages have independent versions.

## R-005 — Canonical domain taxonomy

**Status:** CONFIRMED FROM SPECIFICATION  
**Decision:** `00_core` coordinates `01_foundation`, `02_operation`, `03_agency`, `04_volition`, `05_evolution`, and `06_ether`. The alternate Safety/Capability/Ethics/History/Collective taxonomy is superseded.

## R-006 — Candidate contract import

**Status:** IMPLEMENTED  
**Decision:** Import the 2026 Agent Contracts into the canonical repository with their original candidate status, exact source archive hash and explicit non-retroactivity language.

## R-007 — Generated artifacts

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
**Decision:** Preserve contradictory 2025 documents byte-for-byte under `docs/history/`, while replacing root documentation with the reconciled view.

## R-011 — No silent implementation claims

**Status:** ADOPTED ON BRANCH  
**Decision:** A schema, placeholder file or conceptual module must not be described as a complete runtime implementation without executable evidence and validation.
