# OpenRGD historical reconciliation

## Scope

This work reconciles the public `OpenRGD/openrgd` repository with later local artifacts without redesigning the ecosystem from scratch or projecting later convergence decisions backward into the 2025 lineage.

The branch starts from:

```text
4776e637b4d575d14d55f06423c87cfe1ec0de87
Prepare release 0.1.1 (rename PyPI package to 'rgd')
```

## Evidence classification

- **IMPLEMENTED** — executable code, CI, tests or committed artifacts verified directly;
- **SPECIFIED** — machine-readable or written specification exists;
- **DECIDED FOR RECONCILIATION** — adopted on this branch, pending review/merge;
- **PROPOSED** — future boundary not yet approved;
- **SUPERSEDED** — retained historically but contradicted by later accepted evidence;
- **OPEN / UNCERTAIN** — insufficient evidence or unresolved compatibility.

## Implemented closures

### Repository and seed

- generated build/package artifacts removed;
- active Python/Windows CI established;
- Python and packaging metadata corrected;
- 76 selected canonical source artifacts synchronized with `standard/` and the default seed;
- real `rgd init` materialization verified;
- runtime-profile overrides require explicit reason, decision reference and pinned canonical/seed digests.

### Runtime boundary

- incomplete bundled ROS 2/Viam runtime preserved as historical evidence;
- runtime removed from the installed canonical package;
- `rgd run` converted to a deterministic non-actuating, fail-closed compatibility boundary;
- external embodied-runtime ownership documented;
- ASCII USD importer detached from the stale safety template generator.

### Generated artifacts and hashing

- recursive domain/unified bundles and volatile benchmark snapshots removed;
- duplicate UR5 profiles and checked-in exports removed;
- unverified external URDF examples and incomplete MSIX placeholder removed;
- competing generator lineages replaced by one deterministic Python implementation;
- `OPENRGD_SOURCE_TREE_SHA256_V1` introduced;
- `rgd hash`, deterministic `compile-spec` and guarded `build-standard` implemented;
- all removed paths recorded by Git tree/blob identity under `docs/history/generated-artifacts/`.

## Current authority

```text
spec/                              normative modular source
standard/                          tracked strict-JSON leaf mirror
src/openrgd/seeds/default/spec/    tracked derived default profile
spec/openrgd_unified_spec.json     generated machine bundle, untracked
```

Detailed documents:

- [`ARTIFACT_MAP.md`](ARTIFACT_MAP.md)
- [`ARTIFACT_POLICY.json`](ARTIFACT_POLICY.json)
- [`CANONICAL_HASHING.md`](CANONICAL_HASHING.md)
- [`EXAMPLES_AND_FIXTURES.md`](EXAMPLES_AND_FIXTURES.md)
- [`RUNTIME_BOUNDARY.md`](RUNTIME_BOUNDARY.md)
- [`RUNTIME_STATUS.json`](RUNTIME_STATUS.json)
- [`DECISIONS.md`](DECISIONS.md)
- [`AUDIT_2026-09-02.md`](AUDIT_2026-09-02.md)

## Imported convergence artifact

`contracts/agent/v0.1.0/` was imported from:

```text
openrgd-convergence-alpha-v0.1.zip
sha256 a295463bfc9fb9ad26bc2bff90800874d9e4f7c5db8219fc9a0b7123d2ceb987
```

The package remains a **CONVERGENCE CANDIDATE** and retains explicit non-retroactivity language.

## Open decisions

- final acceptance status of Agent Contracts;
- URDF importer lineage and owned test fixtures;
- static Synapse/export lifecycle tests;
- exact next standard/toolchain release scope;
- recovery or formal exclusion of `openrgd-v0.2-aion-ready`;
- branch protection and required checks;
- commit, release and artifact signing;
- final names and repositories for Physics, Chronograf, embodied runtime, LeRobot and Ethics.
