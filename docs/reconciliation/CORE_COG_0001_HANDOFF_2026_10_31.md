# CORE-COG-0001 — Cross-RFC architecture handoff (DRAFT)

**31 October 2026 · Review only · NON-NORMATIVE · No Core, robot or safety runtime activation.**

This is a sanitized public coordination note. It is not an accepted contract, a Life enrollment, an artifact publication, a Chronon writer, or a validated robot deployment. It reconciles RGD-EXT-0001 Handoff-02, CHRONON-MEM-0001 ML-001, COG-ARCH-0001 Review 02, and the candidate ONEIRIC-001 concept.

## 1. Decision boundaries

- **User direction — Cognition C:** autonomous epistemic goals within approved policy and finite budgets; communication, digital effects and physical actuation are separate effect domains. A generative model does not issue grants.
- **User direction — Five RGD microkernels:** Safety, Life, Work, Relation and Imagination are first-class architectural roles. Historic files need ABI reconciliation; they are not live kernel runtimes on Core `main`.
- **User direction — Two-tier Forge:** a local validated build has a `forge_id`, validation profile, exact-byte digest and provenance. Publication/issuance is a distinct attested event; only verified Registry receipt yields `artifact_id`/`REGISTERED`. Neither event creates physical/Life identity or motion authority.
- **ML-001:** logical memory levels L0 perceptual buffer, L1 evidence vault, L2 canonical Chronon life history, L3 derived cognitive memory, L4 derived autobiographical continuity. Eight memory classes (working, episodic, semantic, procedural, autobiographical, relationship, decision, lessons) are orthogonal to these levels.
- **ONEIRIC-001 candidate:** optional provisional SalienceHint during capture; later OneiricReview/MemoryAnnotation can reinforce, reject or supersede a label, but cannot mutate original Chronon history or treat simulated events as physically observed. The reappraisal process itself may be historical evidence if committed by an authorized writer.
- **World model:** deprecate illustrative `world_model.jsonc` only through a reviewed versioned migration. WorldStateReader, WorldPredictor, WorldSimulator and VLA/ActionPolicyProvider remain distinct interfaces.

## 2. Verified repository and compatibility baseline

- Canonical Core `OpenRGD/openrgd` `main` examined at `afe1a831b950a4e6560f0285a0103fc4eaa343b7`; `spec/` is the authority, `standard/` is a strict mirror, seeds derived. Preserve `OPENRGD_SOURCE_TREE_SHA256_V1` and existing check/boot behavior.
- `contracts/agent/v0.1.0/STATUS.json` declares `candidate=true` in maturity terms and explicitly `normative:false`, `accepted:false`. Core candidate `CognitionProposal` expects mandatory `action_intent`; COG's non-actuating `CognitiveProposal` is a different interface.
- `ProfileSnapshot.robot_id` currently derives from reference `kernel.meta_group.id`, not physical enrollment. Fix via versioned compatibility change (`kernel_reference_id`) rather than silently changing old CLI output.
- `aspirations.jsonc` and `oneiric_state.jsonc` exist as illustrative descriptions but are not selected by current `module_loading_order_list`; `world_model.jsonc` is selected and must not be directly deleted.
- Five historic microkernels and associated registry/coordinator were recovered in historical design work but are not accepted ABI on current Core `main`.
- [COG PR #1](https://github.com/OpenRGD/rgd-cognition/pull/1) is open/draft: bounded synchronous non-actuating host, TTL/dedup/replay, deterministic baseline, proposal/trace, no Chronon/identity/deploy.
- [COG PR #3](https://github.com/OpenRGD/rgd-cognition/pull/3) is open/draft and stacked on #1: canonical `inspect_profile`/`check`/`boot` consumer pinned to source-root, with source-integrity status only; robot and Life binding remain UNBOUND.
- Do not confuse code/CI validation with confirmed physical enrollment, TimeAuthority writer integration, motor permission, AI autonomy, or N150 performance.

## 3. Identity & continuity: contract requirements (P0)

Define distinct IDs: `bundle_id`, `source_root`, `forge_id`, `artifact_digest`, `artifact_id`, `robot_id`, `life_id`, `agent_id`, `persona_id`, `runtime_instance_id`, `boot_id`, `session_id`.

- `life_id` denotes a durable cognitive-experiential lineage; it is not a process PID, LLM model, RGD reference ID or automatically the `agent_id`.
- Reboot reuses a verified existing Life identity; no silent life creation. Missing/corrupt records must yield `RECOVERY_REQUIRED`.
- Separate **Life activation epoch** (binding/embodiment authority) from **role fencing generation** (unique current coordinator or writer owner). For the first robot, one active primary coordinator per exclusive role; remote inference is delegated, not second Life authority.
- Distinguish `REBOOT`, `RESTORE`, `MIGRATION`, `FORK`; backups copied to another machine cannot self-attest the original. A local lock alone cannot establish exclusivity during a network partition.
- Identity dimensions are independently verified: source-integrity, issuer signature, Registry receipt, robot enrollment, Life binding, runtime role/lease and safety readiness; never collapse to a single verified boolean.

**Candidate contract families:** `LifeIdentity`, `RobotLifeBinding`, `AgentDescriptor`, `RuntimeInstance`, `LifeActivation`, `RoleLease/Fencing`, `ContinuityStatus`. The Core owns typed definitions, not key management, locks, registry storage or process scheduling.

## 4. Microkernel ABI and single decision ownership (P0)

| Responsibility | Logical owner |
|---|---|
| Mission, aspirational profile and policy references | RGD/Volition + governance; `orchestra` soft ranking only |
| Deterministic cognitive goal admission | GoalAdmission (COG/Work prototype) consumes trusted grants and Life constraints; no authority creation |
| Non-critical resource arbitration | One Kernel Coordinator |
| Selection of salient information | COG Attention; cues only |
| Task graphs, checkpoints, state transitions | Work Kernel, for admitted goals |
| Homeostasis/resource envelope | Life Kernel with qualified telemetry; UNKNOWN stays UNKNOWN |
| Social proposals / communication | Relation; external Communication Gate |
| Dream, hypothesis, simulation | Imagination; no claim of observed reality |
| Independent physical veto and reflex | Safety/Somatic, outside the COG failure domain |

Define an ABI candidate with kernel ID/version, namespace, owned event kinds, trusted provenance, causal/context/binding refs, TTL, idempotency, requested effect scope, resources, and failure policy. A kernel descriptor's requested capabilities are **not** effective grants. New subgoals must be re-admitted with their own finite budgets.

**Effect classes to reconcile:** `INTERNAL_READ_ONLY`; `HISTORY_COMMIT_REQUEST` (a privileged write, not read-only); `COMMUNICATION_REQUEST`; `DIGITAL_EFFECT_REQUEST`; `PHYSICAL_ACTION_REQUEST`. No automatic access to CAN, network effects, email, repository changes, or proactive TTS from cognitive goal admission.

## 5. Chronon / Memory / Oneiric interoperability (P0)

- Chronograf owns clock/time/anchor; RGD-Physics owns Chronon/Aion semantics; Chronon ledger is canonical **experience history**, while artifact/identity registries are authoritative in their own domains. Memory, Work and autobiographical projections never become second historical writers.
- A frame or IMU sample is not automatically one Chronon; combine event-triggered, periodic coverage and bounded evidence bursts. Explicitly report capture gaps; the history is not necessarily exhaustive.
- Separate original evidence, contemporary provisional interpretation and later review. Example: `POSSIBLE_FIRST_STEP` during capture; later `REVIEW_FIRST_STEP` goal may support, refute or leave the proposition unresolved. `REVIEW_COMPLETED` does not imply `FIRST_STEP_CONFIRMED`.
- Oneiric work is managed through the same Work/GoalAdmission path, not a second decision authority. `KAI_ONEIRIC` is a temporal channel candidate, not a new clock authority. Simulated steps are not physical experiences.
- Provide `AS_KNOWN_AT(T)` and `CURRENT_ASSESSMENT_OF(T)` semantics; preserve event/valid time, ingestion/commit time and knowledge/revision time, including clock domains and uncertainty.
- **Known Temporal Profile conflict:** legacy import text derives TimeAtom from historic timestamp; newer ML-001 demands no retroactive Chronograf attestation. Model historical time as a claim and current import anchor as a distinct actual event; reconcile upstream contracts before writing old logs into Chronons.
- `ContinuityCheckpoint` is a derived, verifiable accelerator (Life refs, ledger watermark, agenda/Work, material beliefs, skill/model/policy revisions); it cannot restore expired grants. Historical cognitive commitments use an authorized writer, not raw model output.
- Respect retention/consent/erasure across evidence, indexes, backups and projections. An append-only logical chain does not excuse unlawful permanent storage.

## 6. Compatibility with COG code (do not rewrite PR #1/#3)

- COG-01 `InputEvent` allows only `USER_TEXT`/`OBSERVATION_NOTICE` and proposals `ANSWER/REPORT/ABSTAIN`; add *separate versioned candidate* `CognitiveGoalCandidate`, `GoalAdmissionDecision`, `AgendaTransition`, `GoalOutcome`, without silently mutating existing schemas.
- COG-02 uses the authentic RGD source integrity verifier but does not verify issuer, Life/Robot bindings or Chronon. A future identity resolver can expose verified scoped views; missing trust stays UNBOUND/UNKNOWN/STALE/CONFLICT.
- Separate `CognitiveProposal`/`CognitiveTrace` (non-actuating) from historical Core `CognitionProposal`/`DecisionTrace` Somatic; bridging requires later explicit approval and versioned adapter.
- Proposed autonomous agenda lab can be SESSION_SCOPED, deterministic and non-actuating, without claimed autobiography; durable identity/history development remains P0 in parallel.

## 7. Required falsification tests

1. Existing `rgd hash/check/boot` and BHL source root remain stable; no fake physical robot identity.
2. Local Forge has no official receipt; offline status stays unregistered; no automatic actuation.
3. Reboot and LLM swap retain the same authorized Life, new runtime ID; missing binding yields RECOVERY_REQUIRED.
4. Primary-role contention, fork, cloned backup and network partition cannot produce two accepted authoritative writers.
5. Stale RTX results rejected on generation/context/TTL mismatch.
6. Uncalibrated IMU/vision cannot certify pose, skill or motion approval.
7. Untrusted goal/kernel provenance, unauthorized tools, self-grants and recursive subgoals are rejected or bounded.
8. Oneiric reappraisal preserves original Chronon and historical as-known interpretation; newly available evidence may supersede annotations.
9. No fabricated Chronograf anchor or history when writer is NOT_CONNECTED; no unapproved durable write.
10. Privacy erasure and missing evidence are expressed accurately; no privileged device/network/digital/voice effect escapes policy.

## 8. Recommended PR order — review only

**A. Documentation/ADR (this PR).** Non-normative handoff, ownership map and decision log; no `spec/`, accepted contracts, CLI, mirror or seed edits.

**B. Candidate Kernel/Goal/Effect ABI.** Five roles, namespaces, effect taxonomy, producer/consumer schemas, negative fixtures and version rules; no imported historical runtime.

**C. Candidate Life/Agent/Runtime/Binding ABI.** Recovery, role leases/fencing, different trust levels, migration/fork; no real identity issuance.

**D. Candidate Chronon/Oneiric/Memory delta.** Temporal import, typed CognitiveCommitment/SalienceHint/OneiricReview/annotation, bitemporal retrieval, checkpoint and erasure; no writer claims.

**E. World compatibility and source migrations.** Dependency audit for `world_model.jsonc`, separate model-provider interfaces and `CognitionProposal` compatibility. Any change to `spec/`, mirror, seed or source hash requires independent versioned acceptance.

**No automatic normative promotion** when a candidate PR merges. Require acceptance governance, reference flow, conformance tests and updated maturity status.

## 9. Return handoff requested from Core chat

Produce `CORE-COG-0001_REVIEW-01`, a decision log with adopted/proposed/open status; exact contract file map, fixture/test matrix and migration costs; and a cross-repository interface handoff so COG-C0, RGD-EXT and CHRONON-MEM can proceed independently.

**Sources:** [Core structure](https://github.com/OpenRGD/openrgd/blob/main/STRUCTURE.md), [agent contract maturity](https://github.com/OpenRGD/openrgd/blob/main/contracts/agent/v0.1.0/STATUS.json), [Kernel](https://github.com/OpenRGD/openrgd/blob/main/spec/00_core/kernel.jsonc), [Oneiric description](https://github.com/OpenRGD/openrgd/blob/main/spec/03_agency/oneiric_state.jsonc), [Aspirations](https://github.com/OpenRGD/openrgd/blob/main/spec/04_volition/aspirations.jsonc), [COG PR #1](https://github.com/OpenRGD/rgd-cognition/pull/1), [COG PR #3](https://github.com/OpenRGD/rgd-cognition/pull/3). Private robot-instance evidence and private RFC source packages have not been copied into this public note.
