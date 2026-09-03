# OpenRGD Governance

## 1. Scope and authority

`OpenRGD/openrgd` is the canonical, non-actuating repository for:

- the modular OpenRGD specification under `spec/`;
- cross-component contracts with explicit maturity;
- canonical hashing and deterministic compilation;
- evidence-only importers and static exporters;
- profile materialization and validation tooling;
- governance, compatibility and historical reconciliation records.

It does not own physical execution, Body Adapters or hardware orchestration. Those responsibilities belong to separately governed implementation repositories.

Canonical decisions are attributed to evidence, pull requests, RFCs and decision records. Names of temporary AI profiles used during design are not governance authorities and are not required in normative documentation.

## 2. Human accountability

The current project steward is:

```text
Pasquale Ranieri (@phate6872)
```

AI systems may help draft, review, test or analyze changes. A human maintainer remains accountable for accepting a normative change, merging a pull request and publishing a release.

## 3. Maturity states

Every specification or contract package must declare one of these states:

| State | Meaning |
|---|---|
| `candidate` | Reviewable convergence material; non-normative and subject to breaking change |
| `accepted` | Approved through the governance process and normative within its declared version/profile |
| `deprecated` | Retained for compatibility and provenance; no longer recommended |
| `historical` | Evidence only; never current authority |

Location inside this repository does not override the declared maturity state.

## 4. Change classes

### 4.1 Normative change

A change is normative when it modifies any of:

- selected files under `spec/`;
- an accepted contract;
- the canonical integrity profile;
- governance or versioning rules;
- conformance requirements;
- ownership boundaries between OpenRGD components.

A normative change requires:

1. a pull request;
2. a clear problem statement and evidence;
3. an RFC or decision-record update when compatibility or meaning changes;
4. canonical hash and derived-artifact updates where applicable;
5. compatibility and migration analysis;
6. all required CI checks;
7. explicit maintainer acceptance.

### 4.2 Candidate or experimental change

Candidate material may be added without becoming normative when it:

- declares `candidate` or `experimental` status;
- cannot silently alter accepted behavior;
- records provenance and open questions;
- includes validation appropriate to its claims.

### 4.3 Tooling change

A tooling change may modify the CLI, validators, importers or static exporters. It must not silently redefine the standard. If tooling exposes a missing contract, the change must include a Contract Delta or RFC rather than embedding a private interpretation.

### 4.4 Historical evidence

Historical material is immutable evidence. Corrections are appended as notes or new records; original bytes are not rewritten to match later decisions.

## 5. Pull-request governance

Direct pushes to `main` are prohibited by policy. Every merge must use a pull request and pass the checks listed in `governance/policy.json`.

Required review behavior during the single-maintainer phase:

- the author completes the public PR checklist;
- all review conversations are resolved;
- required CI is green on the final head;
- normative decisions are recorded explicitly;
- the maintainer records a final merge-readiness statement.

While only one maintainer exists, the required independent approval count is zero because GitHub does not permit authors to approve their own pull requests. When a second maintainer is appointed, normative pull requests must require at least one approval from a maintainer who is not the author.

## 6. RFC process

An RFC is required for:

- a new normative domain or top-level contract;
- breaking schema or wire-format changes;
- changes to hard invariants or governance-locked policy;
- a new canonical hash/signature profile;
- promotion of a candidate contract to accepted;
- ownership changes between repositories;
- changes that may affect physical safety boundaries.

Use `.github/ISSUE_TEMPLATE/rfc.md` and link the accepted result from `docs/reconciliation/DECISIONS.md` or a future versioned ADR/RFC directory.

## 7. Contract promotion

A candidate contract may become accepted only when all of the following are available:

1. complete schemas and normative text;
2. explicit compatibility and versioning rules;
3. producer and consumer conformance tests;
4. at least one validated reference flow;
5. no unresolved contradiction with the Canonical Core;
6. an accepted RFC or equivalent governance decision;
7. an updated machine-readable status file.

The current `contracts/agent/v0.1.0` package remains a convergence candidate.

## 8. Safety and emergency changes

Security or safety fixes may be expedited, but they must fail closed and must not be used to smuggle a normative expansion into the repository.

An emergency change must still:

- use a pull request whenever GitHub remains available;
- identify the concrete risk;
- minimize scope;
- preserve evidence;
- pass all feasible checks;
- receive a follow-up governance review before release.

No emergency process grants the canonical repository permission to actuate hardware.

## 9. Merge methods and commit history

The default merge method is a **merge commit**, preserving granular, reviewed commits and the pull-request boundary.

Squash merge is permitted only by an explicit decision when the intermediate commits are disposable and carry no useful implementation, migration or provenance evidence.

Historical reconciliation PR #1 must use a merge commit so its evidence-producing sequence remains reachable from `main`.

Force-pushes and deletion of `main` are prohibited.

## 10. Releases

Merge and release are separate decisions. Tag and artifact rules are defined in `RELEASE_POLICY.md`.

A source-tree hash proves content integrity under a declared profile. It is not a signature and does not prove authorship, review or moral correctness.

## 11. Governance changes

Changes to this document are normative and must follow the normative change process above.
