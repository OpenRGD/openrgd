# OpenRGD Historical Reconciliation

## Scope

This work reconciles the public `OpenRGD/openrgd` repository with later local artifacts without redesigning the ecosystem from scratch or pretending that later convergence decisions existed in the 2025 history.

The branch starts from public commit:

```text
4776e637b4d575d14d55f06423c87cfe1ec0de87
Prepare release 0.1.1 (rename PyPI package to 'rgd')
```

The detailed repository audit is available in [`AUDIT_2026-09-02.md`](AUDIT_2026-09-02.md).

Artifact authority and convergence rules are documented in:

- [`ARTIFACT_MAP.md`](ARTIFACT_MAP.md) — human-readable ownership and reconciliation map;
- [`ARTIFACT_POLICY.json`](ARTIFACT_POLICY.json) — machine-readable validation and override policy.

## Evidence policy

Evidence is classified as:

- **IMPLEMENTED** — executable code, CI, tests or committed artifacts verified directly;
- **SPECIFIED** — machine-readable or written specification exists;
- **DECIDED FOR RECONCILIATION** — adopted on this branch, pending review/merge;
- **PROPOSED** — plausible future boundary or repository, not yet approved;
- **SUPERSEDED** — preserved historically but contradicted by later accepted structure;
- **OPEN / UNCERTAIN** — insufficient evidence or unresolved compatibility.

## Current status

### IMPLEMENTED on this branch

- generated build artifacts removed and ignored;
- active CI for Python 3.10/3.12 and Windows executable build;
- packaging metadata repaired;
- candidate agent contracts imported with source hash and local validation;
- old contradictory documents preserved under `docs/history/` rather than silently deleted;
- repository invariants and reconciliation tests enforced in CI;
- deterministic leaf-artifact checker for `spec/`, `standard/` and the packaged default seed;
- real `rgd init` test proving complete seed materialization and limiting kernel mutation to the project DID;
- archival of the superseded seed-only skill index under `docs/history/seed/`.

### SPECIFIED in the repository

- OpenRGD bundle target version `0.2.0`;
- six domains: Foundation, Operation, Agency, Volition, Evolution and Ether;
- kernel profile and modular JSONC specification;
- CLI/import/export/Synapse scaffolding;
- explicit source/derived artifact authority and hash-pinned seed-override requirements.

### DECIDED FOR RECONCILIATION, pending merge

- `OpenRGD/openrgd` is the single normative root for the standard and cross-component contracts;
- standard, CLI and contract versions remain independent;
- `spec/` is the human-readable normative source;
- `standard/` is a strict JSON compatibility mirror validated by parsed semantic equivalence;
- the packaged default seed is a derived runtime profile, byte-identical to selected canonical sources unless an explicit `RUNTIME_PROFILE_OVERRIDE` is approved and digest-pinned;
- generated domain/unified bundles remain outside the leaf-mirror closure until their generator is reconciled separately;
- convergence artifacts retain explicit candidate status and cannot rewrite history retroactively.

### VERIFIED CLOSURE

The validated implementation head reports:

```text
STANDARD: 76 expected, 0 missing, 0 mismatched, 0 unexpected
DEFAULT SEED: 76 expected, 0 missing, 0 mismatched,
0 approved overrides, 0 unexpected
```

The previous packaged-seed drift finding is therefore resolved on this branch.

### SUPERSEDED

- the legacy domain taxonomy `Foundation / Safety / Capability / Ethics / History / Collective`;
- the old root `GLOSSARIO.md`, which contained ignore rules rather than terminology;
- documentation that presented missing paths as implemented modules;
- stale seed revisions of the kernel header, actuation topology and surface properties;
- the seed-only strict-JSON two-entry skill index;
- generated unified outputs stored inside the active default seed.

### OPEN / UNCERTAIN

- deterministic ownership and regeneration of domain bundles, unified specifications, benchmark snapshots and robot-instance copies;
- exact release/tag scoping for the next public version;
- migration of later `openrgd-v0.2-aion-ready` content, whose archive was not available in this workspace;
- final ownership and names of Physics, Chronograf, embodied runtime, LeRobot and Ethics repositories;
- promotion criteria for Agent Contracts from candidate to accepted;
- the prototype runtime's unresolved safety-module reference;
- canonical serialization and bundle-hash scope;
- remaining full CLI lifecycle coverage;
- protection and required checks for `main`.

## Imported convergence artifact

`contracts/agent/v0.1.0/` was imported from:

```text
openrgd-convergence-alpha-v0.1.zip
sha256 a295463bfc9fb9ad26bc2bff90800874d9e4f7c5db8219fc9a0b7123d2ceb987
```

Its own provenance file records the non-retroactivity rule.
