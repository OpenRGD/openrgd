# OpenRGD historical reconciliation

## Scope

This directory records the reconciliation of the public `OpenRGD/openrgd` baseline with later recovered work without redesigning the ecosystem from scratch or projecting later decisions backward into the 2025 lineage.

Baseline:

```text
4776e637b4d575d14d55f06423c87cfe1ec0de87
Prepare release 0.1.1 (rename PyPI package to 'rgd')
```

## Evidence classification

- **IMPLEMENTED** — executable code, CI, tests or committed artifacts verified directly;
- **SPECIFIED** — machine-readable or written specification exists;
- **DECIDED FOR RECONCILIATION** — adopted on the branch, pending review/merge;
- **PROPOSED** — future boundary not yet approved;
- **SUPERSEDED** — retained historically but contradicted by later accepted evidence;
- **OPEN / UNCERTAIN** — insufficient evidence or unresolved compatibility.

## Closed workstreams

1. `spec/`, strict mirror and packaged-seed authority;
2. canonical source-tree hashing and deterministic compilation;
3. generated-artifact, duplicate-workspace and example cleanup;
4. quarantine of the incomplete bundled physical runtime;
5. evidence-only URDF and lightweight text-USDA import;
6. static non-actuating ROS 2 export;
7. integrity-aware `check` and non-actuating `boot` grounding;
8. governance, version axes, contract maturity and release boundaries;
9. repository/secret hygiene and stale-prototype cleanup;
10. identity and technical audit of the recovered AION-ready backup variant.

## Current authority

```text
spec/                              normative modular draft source
standard/                          tracked strict-JSON leaf mirror
src/openrgd/seeds/default/spec/    tracked derived default profile
contracts/                         maturity-labelled cross-component interfaces
governance/                        machine-readable repository policy
spec/openrgd_unified_spec.json     generated machine bundle, untracked
export/                            generated static interoperability output
tests/fixtures/                    owned non-normative test evidence
```

## Primary records

- [`AUDIT_2026-09-02.md`](AUDIT_2026-09-02.md) — main repository reconciliation audit;
- [`AI_HYGIENE_AUDIT.md`](AI_HYGIENE_AUDIT.md) — secret, stale-claim and active-tree hardening supplement;
- [`AION_READY_BACKUP_AUDIT.md`](AION_READY_BACKUP_AUDIT.md) and [JSON](AION_READY_BACKUP_AUDIT.json) — recovered backup identity, contamination and AION maturity audit;
- [`DECISIONS.md`](DECISIONS.md) — decisions R-001 through R-049;
- [`DECISIONS_HYGIENE.md`](DECISIONS_HYGIENE.md) — decisions R-050 through R-058;
- [`EVIDENCE_SCOPE.md`](EVIDENCE_SCOPE.md) and [JSON](EVIDENCE_SCOPE.json) — expected archive versus recovered backup identities;
- [`SPEC_CONTENT_HYGIENE.md`](SPEC_CONTENT_HYGIENE.md) and [JSON](SPEC_CONTENT_HYGIENE.json) — registered unverified draft assertions;
- [`MERGE_READINESS.md`](MERGE_READINESS.md) — current merge gates;
- [`ARTIFACT_MAP.md`](ARTIFACT_MAP.md) and [`ARTIFACT_POLICY.json`](ARTIFACT_POLICY.json) — source/derived ownership;
- [`CANONICAL_HASHING.md`](CANONICAL_HASHING.md) — integrity profile;
- [`RUNTIME_BOUNDARY.md`](RUNTIME_BOUNDARY.md) — non-actuating canonical-root boundary;
- [`IMPORT_EXPORT_LIFECYCLE.md`](IMPORT_EXPORT_LIFECYCLE.md) — evidence/import/export lifecycle;
- [`PROFILE_INSPECTION.md`](PROFILE_INSPECTION.md) — exact `check`/`boot` semantics.

## Recovered AION-ready backup

The historical checksum record identifies an expected ZIP:

```text
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

The uploaded full backup has a different ZIP SHA-256:

```text
f91ad48cd6a2e8a8bff5f3c559fb8f7fc475e9c4957864aeed6aa689d07615ae
```

It is a structurally valid, later local backup of the same working lineage, but byte identity is not proven and the difference is not limited to `.env`. The backup contains generated local artifacts, package metadata, a post-checksum `src/openrgd/main.py` edit and one secret-bearing `.env`.

The secret was not copied or fingerprinted in repository evidence. No evidence was found that `.env` entered the current GitHub repository or PR, but revocation of the exposed credential remains required.

The AION implementation is classified as an experimental codec and limited validator. It is excluded from PR #1 and requires a sanitized post-merge evidence-delta pull request.

## Merge state

Repository-tree reconciliation and hygiene are complete and CI-validated.

PR #1 remains draft because server-side protection of `main` is still absent. Issue #2 tracks the required pull-request enforcement, status checks, branch freshness, conversation resolution and force-push/deletion blocking.

No merge, tag, release, contract promotion or physical-runtime claim is authorized by these records.
