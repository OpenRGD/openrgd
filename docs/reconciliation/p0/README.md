# Core P0 — integration baseline REVIEW-02

**2026-11-01. Review coordination only; NON-NORMATIVE.** This supplements Core #8/#10 and the existing checklist, without replacing original decisions. No merge/deploy, accepted specification, registry issuance, Life enrollment, history writer or physical authorization is implied.

## One entry point, four distinct states

Use `SOURCE_INVENTORY.json` for exact source pins and archive fingerprints, `DISCREPANCIES.md` for ownership and migration decisions, and `COG_CORE_B_CROSSWALK.md` for the actual C0/C1 producer mapping. A file being available, a PR being merged, a contract being accepted, and a runtime being operational are separate facts. SHA equality establishes content, not authenticity or enrollment.

Live Core main remains `afe1a831b950a4e6560f0285a0103fc4eaa343b7`. Core-B #11 is draft at `55a034ceb1cdaab8bed6848fcdde85c9436bc9e0`. Cognition has advanced to C1 #5 at `a8ae925c9cacbce8bd7a6db01833d4159445d47a`, stacked on #4 -> #3 -> #1. Do not plan only against C0 or silently retarget those PRs.

## Execution order and ownership

| Work item | This review | Next evidence / owner |
|---|---|---|
| BASE-01/04 source and consumer inventory | Pinned main/draft/archive distinction; C1 included | Refresh on changed head, not on verbal recollection / Core |
| BASE-02 microkernel recovery | Eight local review texts recovered and inspected, hashes recorded | Original historical Git equivalence still unproven / Core maintainer |
| BASE-03 extension/plugin/somatic integration | Candidate archives located; not main or a release | Small independent port PRs; do not overlay ZIP on main / Core |
| B-01 Core-B/C0/C1 field mapping | Concrete compatibility gaps documented | Explicit versioned bridge and real new-ABI consumer / COG + Core |
| B-02..06 operational conformance | Existing Core-B checks are not new ABI adoption by COG | Session-scoped read-only producer/consumer integration / COG |
| C-01..05 Life/Agent/Runtime/Binding | Next independent PR-CORE-C: candidate schemas and fixture tests | Actual authority/custody/fencing/identity service is separate / Identity-Life |
| EXT-01..04 forge/publication/enrollment | Shared identity vocabulary and authority boundary below | Exact-byte issuance receipts, trust roots and offline verification / RGD-EXT |
| D-01..06 Temporal/Memory | Delta requirements consolidated; old Agent contracts unchanged | Chronograf/history producer agreement then versioned contracts / Temporal-Memory |
| ONEIRIC | Preserve C0 synthetic experiment, do not reimplement | Persisted reappraisal only through admitted Work + authorized writer / Work-Memory |

Partial rows do not close the entire checklist. In particular recovering eight local review files does not establish that they are the original eight historical blobs, and identity-shaped JSON does not implement continuity on the robot.

## Integration acceptance gates

1. Exact commit/artifact and version for every producer/consumer; no hidden dependency on local ZIPs.
2. Old Core source, Agent schemas, `check/boot`, canonical hashing and COG #1/#3 remain unchanged until explicit migration.
3. For Core-C, source integrity, issuer, publication, physical enrollment, Life binding, role ownership and effect authorization remain independent.
4. On reboot: recover Life explicitly, create new runtime/boot/session, revalidate current authority. Missing custody -> RECOVERY_REQUIRED; never mint another Life implicitly.
5. On restore: checkpoint is a derived hint; verify authoritative watermark and current revocation. On fork/migration: separate approval, not restart aliases.
6. Receiver checks current role fence for every privileged request; a number supplied by the sender is not a lease. Identical cloned credentials/IDs need external custody and session authentication, not JSON validation.
7. COG read-only labs may proceed without durable Life. New positive identity context cannot be injected into COG-02 schemas which explicitly require null IDs.
8. No accepted status, release, spec/hash migration or deployment from merely passing CI.

## Unified P0 terminology

- `bundle_id/source_root`: model/revision, not a robot.
- `forge_id/artifact_digest`: local validated artifact; publication of the same bytes has a distinct receipt/`artifact_id`.
- `robot_id`: physical unit only after an external enrollment procedure. A model DID or alias is not evidence.
- `life_id`: durable experiential lineage; Life kernel is not its issuer.
- `agent_id`: software participant; `runtime_instance_id/boot_id/session_id`: ephemeral execution identifiers.
- `life_activation_epoch`: binding activation, NOT each task restart.
- `role_fencing_generation`: current exclusive-role generation, NOT C0 task generation.
- L0 volatile, L1 evidence, L2 canonical Chronon history, L3 memory projections, L4 autobiography; not five independent ledgers.
- Original observation, derived interpretation, synthetic simulation and the real computation of a review are distinct provenance classes.

## What is deliberately not integrated here

No runtime code from archives, no replacement kernel, no `world_model.jsonc` deletion, no Chronon writer or new temporal codec, no new grant issuer, no five-process topology. Source reviews are inputs to narrowly scoped candidate PRs, not a second canonical Core.
