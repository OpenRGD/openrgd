# OpenRGD historical reconciliation

## Scope

This work reconciles the public `OpenRGD/openrgd` repository with recovered later artifacts without redesigning the ecosystem from scratch or projecting later convergence decisions backward into the 2025 lineage.

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

### 1. Repository and seed

- generated build/package artifacts removed;
- active Python/Windows CI established;
- Python and packaging metadata corrected;
- 76 selected source artifacts synchronized with `standard/` and the default seed;
- real `rgd init` materialization verified;
- runtime-profile overrides require explicit reason, decision reference and pinned digests.

### 2. Runtime boundary

- incomplete bundled ROS 2/Viam runtime preserved as historical evidence;
- runtime removed from the installed canonical package;
- `rgd run` converted to a deterministic non-actuating, fail-closed compatibility boundary;
- external embodied-runtime ownership documented.

### 3. Generated artifacts and hashing

- recursive domain/unified bundles and volatile benchmark snapshots removed;
- duplicate UR5 profiles and checked-in exports removed;
- unverified external URDF examples and incomplete MSIX placeholder removed;
- competing generator lineages replaced by one deterministic Python implementation;
- `OPENRGD_SOURCE_TREE_SHA256_V1`, `rgd hash`, deterministic `compile-spec` and guarded `build-standard` implemented;
- removed paths recorded by Git tree/blob identity.

### 4. URDF/USDA evidence, enrichment and static export

- URDF importer converted from a full-profile/policy generator to source-derived partial Foundation evidence;
- text USDA importer hardened into a narrow declared evidence profile;
- absent physical values no longer receive silent defaults;
- source provenance is content-addressed without machine-local paths;
- USD angular, linear and effort conversion is bound to authored unit evidence;
- `rgd alive` personalizes profile identity and records seed/body compatibility as `UNVERIFIED`;
- project-owned hermetic URDF and USDA fixtures added;
- ROS 2 static export made deterministic and bound to the source/bundle root;
- imported bodies prevented from inheriting seed HAL through name collisions;
- hardware Xacro withheld until explicit complete HAL evidence exists;
- historical Isaac placeholder removed from the active target registry;
- complete non-actuating lifecycles tested in CI.

### 5. Static profile inspection

- `rgd check` upgraded from path-existence checks to source-integrity and selected-module validation;
- `rgd boot` converted from warning-tolerant prompt assembly to deterministic non-actuating grounding;
- stale roots, unsafe/duplicate references, missing files and invalid/non-object modules fail closed;
- both commands explicitly deny hardware/runtime readiness claims;
- historical command implementations recorded by Git blob identity.

### 6. Merge readiness and governance freeze

- canonical repository ownership and human accountability frozen;
- temporary AI design-profile names excluded as governance authorities;
- maturity states formalized as `candidate`, `accepted`, `deprecated` and `historical`;
- Agent Contracts frozen as `candidate`, non-normative and non-releasable as stable contracts;
- normative RFC, pull-request and CODEOWNERS surfaces added;
- merge commits adopted by default to preserve granular reviewed history;
- standard, toolchain and contract tag namespaces separated;
- Windows release publication scoped to `toolchain-v*` tags only;
- merge and release separated;
- signing distinguished from source-tree integrity;
- AION-ready archive classified and excluded as digest-only evidence;
- governance consistency enforced in CI;
- server-side protection requirements documented and tracked in GitHub issue #2.

## Current authority

```text
spec/                              normative modular source
standard/                          tracked strict-JSON leaf mirror
src/openrgd/seeds/default/spec/    tracked derived default profile
contracts/                         maturity-labelled cross-component interfaces
governance/                        machine-readable repository policy
spec/openrgd_unified_spec.json     generated machine bundle, untracked
export/                            generated static interoperability output
tests/fixtures/                     owned non-normative test evidence
```

Detailed documents:

- [`ARTIFACT_MAP.md`](ARTIFACT_MAP.md)
- [`ARTIFACT_POLICY.json`](ARTIFACT_POLICY.json)
- [`CANONICAL_HASHING.md`](CANONICAL_HASHING.md)
- [`EXAMPLES_AND_FIXTURES.md`](EXAMPLES_AND_FIXTURES.md)
- [`IMPORT_EXPORT_LIFECYCLE.md`](IMPORT_EXPORT_LIFECYCLE.md)
- [`PROFILE_INSPECTION.md`](PROFILE_INSPECTION.md)
- [`RUNTIME_BOUNDARY.md`](RUNTIME_BOUNDARY.md)
- [`RUNTIME_STATUS.json`](RUNTIME_STATUS.json)
- [`EVIDENCE_SCOPE.md`](EVIDENCE_SCOPE.md)
- [`EVIDENCE_SCOPE.json`](EVIDENCE_SCOPE.json)
- [`MERGE_READINESS.md`](MERGE_READINESS.md)
- [`DECISIONS.md`](DECISIONS.md)
- [`AUDIT_2026-09-02.md`](AUDIT_2026-09-02.md)

Repository governance:

- [`../../GOVERNANCE.md`](../../GOVERNANCE.md)
- [`../../RELEASE_POLICY.md`](../../RELEASE_POLICY.md)
- [`../../SECURITY.md`](../../SECURITY.md)
- [`../governance/BRANCH_PROTECTION.md`](../governance/BRANCH_PROTECTION.md)
- [`../../governance/policy.json`](../../governance/policy.json)

## Imported convergence artifact

`contracts/agent/v0.1.0/` was imported from:

```text
openrgd-convergence-alpha-v0.1.zip
sha256 a295463bfc9fb9ad26bc2bff90800874d9e4f7c5db8219fc9a0b7123d2ceb987
```

The package remains a **CONVERGENCE CANDIDATE**. Its machine-readable status explicitly says:

```text
maturity = candidate
normative = false
accepted = false
stable_release_allowed = false
```

Merge does not promote it.

## Excluded digest-only evidence

Only a checksum record was available for:

```text
openrgd-v0.2-aion-ready.zip
sha256 8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

The archive bytes were unavailable and its contents were not inspected or inferred. It is explicitly excluded from PR #1 and is not merge-blocking. Later recovery requires digest verification and a separate evidence-delta pull request.

## Technical verification checkpoint

Governance implementation checkpoint:

```text
02222e88a4e5f5026d828e3f5d174ae65a0a2428
```

Pull-request workflow:

```text
33735707622 — SUCCESS
```

Verified:

- Python 3.10 and 3.12;
- all repository, artifact, hash, runtime and governance validators;
- Agent Contracts candidate-status validator;
- 35 pytest tests;
- Windows executable build and upload.

Artifact:

```text
id:     9885693022
name:   openrgd-rgd-windows
size:   12,190,774 bytes
sha256: bb1303549910927f9e1f04c9709fe54ca179ac8404139ab5c534c33073a0d966
```

## Merge status

Repository-tree governance is complete and technically verified.

PR #1 remains draft because GitHub currently reports `main` as unprotected. The only remaining merge-control gate is issue #2, which requires pull-request enforcement, the three named status checks, up-to-date branches, resolved conversations, and force-push/deletion blocking.

## Work intentionally outside PR #1

- promotion of Agent Contracts;
- generic seed/body compatibility certification;
- full OpenUSD SDK integration;
- live ROS 2 and hardware-bound validation;
- embodied runtime and Body Adapter repositories;
- recovery and inspection of the excluded AION-ready archive;
- stable release signing and attestations;
- final names and repository migration for Physics, Chronograf, LeRobot and Ethics.
