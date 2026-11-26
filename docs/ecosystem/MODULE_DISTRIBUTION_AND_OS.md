# ECO-01 / EXT-01 — One module publication, many consumers
**2026-11-26 · Proposed architecture / NON-NORMATIVE · No implementation, installation, deployment or grant.**
This is a design input to CORE-ECOSYSTEM-01, not a second registry or acceptance of an ABI. It builds on the existing [repository map](../reconciliation/REPOSITORY_MAP.md), P0 review #12, the earlier extension architecture work (local review artifacts, not assumed published), and Core-B/C/D candidates. RGD-OS remains a reserved repository, not a shipped operating system.

## Current baseline (source reviewed)
- [rgd-modules@0268b374](https://github.com/OpenRGD/rgd-modules/tree/0268b3748042d04fd3561553616388368881e04a): `registry/index.json` lists only `org.openrgd.calibration@0.2.0`; release descriptor references pinned source and compares selected fields with the producer's `module.openrgd.json`. `rgd_registry/core.py` supports pinned Git/Cargo, candidate releases, no hardware permissions and a calibration-specific safety profile. The descriptor schema only supports command_line_json / inspect. Discovery and install already share an engine, but not every future module type.
- [Console@a0ef857c](https://github.com/OpenRGD/rgd-console/tree/a0ef857cf425c1bb14ad8f62acec21f8c1324866): Dockerfile.module-agent embeds that exact registry revision; module-agent catalog calls registry.catalog/status_of, API relays /modules/catalog, Web maps dynamic registry entries. Reload queries the embedded snapshot, not latest GitHub. Explicit operator confirmation and zero-motion restrictions remain; Calibration Inspector and bundled Console modules are separate integration surfaces. Current local source/digest checks are not signed distribution or a live refresh protocol.
- [Module Registry #2](https://github.com/OpenRGD/rgd-modules/pull/2): IMU RFC only, not an installable entry. [Console #22](https://github.com/OpenRGD/rgd-console/pull/22): existing PERIPH stack reconciliation. Do not duplicate peripheral management. [rgd-os](https://github.com/OpenRGD/rgd-os) main is a README reservation.
- Core owns semantic model, cross-component contracts and governance. Core's skill extension policy is not a package install grant; Core-B/C effect/identity candidates do not implement host permission issuance.

## Proposed source-of-truth boundaries

| Information | Authoritative owner | Consumers |
|---|---|---|
| Semantic capability/interface vocabulary and versioned interoperability contracts | openrgd (Core), with owning module reviews | Producers, registry, runtime, CLI, Console, OS |
| Module identity, declared capabilities, typed interface/operation requirements, dependencies, supported distribution metadata | module producer's versioned module.openrgd.json (proposed evolved manifest; preserve v0.1) | Release validation and registry projection |
| Approved release selection, exact source/artifact/manifest digest, review/trust/revocation metadata | rgd-modules | Module manager engine, all clients |
| Actual installed release, exact dependency lock, health, selected deployment and local policy/grants | host-local manager/supervisor and independently authorized policy owners | Console, CLI, eventual OS; not repository files |
| Engineering repo/ownership/dependency overview | Core docs/ecosystem | Humans and optional read-only UI; links or generated projection of release data, never installer input |
| RI compatibility | RI registry + actual owners | Core links to pinned evidence; no copied authoritative matrix |

One editable declaration for each semantic field. Intentional published copies are generated/validated projections, not independent hand-edited catalogs. A release adds registry-owned approval and immutable artifact identity, not new capability claims. A producer's manifest cannot approve its own release. Repository name or presence is not a module ID, package publication, installed instance, resource lease, Life or physical permission. Component IDs in the engineering inventory may map to zero/many module releases. Private modules are opt-in scoped catalogs with separate access; public Core contains no private repository metadata, tokens or configuration. Inventory completeness must not block installation of an independently approved supported module.

## Target publication and discovery flow

1. Producer defines a stable namespaced module ID and version and authors one manifest in its own repository; CI checks schema, interface contracts, dependencies, compatibility and negative permission tests.
2. Build/review exact immutable source/artifact, including manifest digest and artifact/platform metadata. Do not try to self-embed the enclosing Git commit in its own manifest. Proposed registry publication workflow takes a pinned producer release, derives descriptor/index entries, validates exact source and content, and opens an operator-reviewed publication PR. Retain independent registry eligibility and publisher trust. Reject duplicate ID/version with different content.
3. Publish versioned immutable catalog snapshots. Proposal: authenticated/signed index/manifest with digest, expiry, rollback/freshness and revocation policy. Key management and signature format are separate review work; no signing implementation now. Catalog refresh explicitly verifies policy and stages new snapshot before atomic selection, preserves last known good for read-only status, never installs or activates automatically. Unknown/revoked/stale trust must fail closed for new privileged actions; no unsafe automatic shutdown of physical control based solely on catalog outage.
4. One reusable Module Manager engine (evolve existing registry engine and isolate host lifecycle backend; final package/service placement to review). Console, CLI and RGD-OS use the same versioned catalog/plan/status/install interfaces, not their own installers. A host profile resolves dependencies to exact versions/digests and locks composition. Detect missing/cyclic/conflicting/incompatible dependencies and ambiguous providers before modifying a host. Explicit approval for downloads/builds and for resolved dependency plan. No floating main or silent upgrade. Atomic staged install, verified result, coexistence/rollback per supported type.
5. Separate install, configure, enable, start, stop, health, update and remove. Installed/ready != enabled != running != healthy != calibrated != authorized. State transitions, restart, reconciliation and rollback are host-local, with least privilege and audited explicit grants. Default is no auto-start, device access, network egress or actuation. PERIPH remains resource owner; Somatic remains independent safety authority. History writes, external communication and digital/physical effects retain their separate gates. No generic manifest command/shell execution, arbitrary frontend script loading, Docker socket or privileged container merely because a release is listed.
6. Generic UI renders validated metadata, capabilities, compatibility and lifecycle/status. Use typed, versioned interfaces (initially offline read-only command-line JSON); specialized panels consume named interfaces and remain optional. Unsupported interface or distribution kind => visible not supported, no install/activation. A supported class must not require module-specific edits to every client.

```text
producer manifest -> reviewed release publication -> versioned Module Registry snapshot
                                                    |
                                                    v
                     shared module manager / local host policy + lifecycle backend
                        |                  |                  |
                     Console              CLI              RGD-OS
```

The OS should initially be a host/distribution composition consumer of these interfaces (e.g., Linux and independent supervisors), not a new package registry or a replacement for the real-time Somatic path. No OS deployment is proposed. Bootstrap/recovery must not depend on downloading the registry; core read-only recovery/status should work offline. Device/service management requires independently reviewed profiles, not a permissive generic installer.

## Candidate milestones (order matters)

| Gate | Owner | Deliverable |
|---|---|---|
| EXT-01A | Core + Registry + Console | Inventory current v0.1 contracts, bundled module and producer manifests; agree ownership, IDs, schema versions and no-duplication rule. Recover earlier extension/command ABI review, do not overlay old archive. |
| EXT-01B | Registry with Core review | Versioned generic manifest/release profile and deterministic generated publication/index; keep CAL 0.2 and existing v0.1 reader unchanged. Design trust/update/version compatibility, bounded parsing and dependency plan. |
| EXT-01C | Registry/manager + Console | Shared engine and authenticated host API, read-only catalog snapshot refresh, explicit atomic install; replace per-module installer special cases only after negative compatibility tests. |
| EXT-01D | Module producers | Demonstrate a second module in the supported non-actuating offline class, no hardware access, no new UI/backend/OS entry. Later add independently reviewed distribution kinds (native binary, Python, service or peripheral provider); do not register IMU as installable until supported lifecycle, resource and policy gates exist. |
| EXT-01E | RGD-OS / CLI | Reuse the exact catalog/manager contracts in a second consumer or isolated OS composition prototype; no second registry, no new physical privileges. |
| ECO-01 | Core | Repository ownership map links module registry and RI registry; optional read-only generated metadata and compatibility view, never feeds installer directly. |

## Definition of done: one new supported module release

A test-only second non-actuating module is introduced by a manifest and reviewed generated release record. A fresh approved snapshot exposes both releases to Console/CLI/OS-compatible consumers without edits to client module lists, per-module backend routes or OS configuration. Existing Calibration v0.1 install/inspect and rollback remain working. New unsupported distribution kinds need a new generic reviewed backend once, not a bespoke backend per module. New semantic capabilities may require shared contract review; new effects always require independent policy/grants.

Test rejection of unknown schema/kind, changed manifest or artifact, duplicate release/digest, stale/revoked snapshot, invalid publisher, invalid paths, incompatible host/API, missing/cyclic dependencies, corrupted installed binary, unsafe requested privilege, unexpected build/activation, failed update/rollback, offline snapshot and unauthorized install. Demonstrate install does not start the process or grant access, and no automatic hardware actions from registry refresh. No promise of production sandboxing or signing until implementation and actual independent acceptance.

## Scope
This document is a proposal only. No schema, catalog entry, module registration, command, test implementation, runtime, canonical spec, registry or Console change. No automatic merge. Confirm publication, trust and lifecycle decisions with owners before implementing. Keep existing source pins and current no-device policy.
