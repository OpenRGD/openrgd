# Core-B ↔ COG-C0/C1 — source-level crosswalk

2026-11-01, CANDIDATE review. Sources: Core `55a034ceb1cdaab8bed6848fcdde85c9436bc9e0` (`contracts/kernel/v0.1.0/schemas/kernel-goal-effect.schema.json`); COG `a8ae925c9cacbce8bd7a6db01833d4159445d47a` (`agenda_c0.py`, `schemas/agenda-c0.schema.json`). C1 #5 composes C0, not a replacement for its admission owner. No production adapter implemented by this document.

| COG field / behavior | Core-B destination | Rule / gap |
|---|---|---|
| candidate_id | goal_id | May preserve as stable scoped identifier; not an identity proof |
| full immutable C0 candidate | goal_revision | Explicit commitment/encoding profile; candidate_id alone does not prove exact mutable content |
| context_revision | context.revision | Exact pin; no recomputation that hides a stale source |
| session_id | context.session_id | Preserve exact session; do not infer runtime_instance_id or boot_id from it |
| no runtime ID in candidate | context.runtime_instance_id | Obtain from trusted host; do not manufacture Life from a session UUID |
| life_id null / NOT_CONNECTED | SESSION_SCOPED with null binding/activation | Preserve. Core-C presence cannot upgrade COG-02 null identity schema |
| origin_role_hint work/imagination | origin + producer provenance | Local hint only; not authenticated Work/Imagination ownership |
| three specialized goal_kind values | INVESTIGATE / ONEIRIC_REVIEW + task_ref | Preserve specialization in a versioned referenced payload; do not discard first-step vs evidence-conflict meaning |
| requested_effect_scope (one) | requested_effects (array) | One explicit category; external_network_requested must remain denied, not silently dropped |
| requested_budget_steps | budget.steps | Wall time, child count/depth and queue caps come from host admission, not guessed unlimited defaults |
| parent_goal_id/depth | parent_goal_id/depth | Re-admit child, validate actual parent/context and aggregate remaining resources |
| ttl_ms | lifetime | Requires original receipt/deadline and same monotonic domain. Mapping time is NOT creation time |
| evidence_refs / DECLARED_ONLY | provenance.evidence_refs + payload | Keep synthetic/declared qualifiers; never infer OBSERVED or calibrated evidence |
| ADMITTED/REJECTED/DEFERRED | ADMIT/REJECT/DEFER | Renaming outcomes is insufficient: retain policy revision, exact goal revision, budget and evaluated grant refs |
| granted_effect_scope | eligible_effects | C0 lab decision is not a transferable permission or EffectGateDecision ALLOW |
| C0 generation | NOT role_fencing_generation | It is task callback invalidation. Obtain role fencing separately; null/session-scoped semantics require explicit policy |
| QUEUED | ADMITTED (possible mapping) | Needs exact admission reference and task ownership; no execution yet |
| PAUSED_USER/PAUSED_LIFE/WAITING_EVIDENCE | PAUSED (possible mapping) | Preserve distinct reason in an agreed payload; plain enum cast loses information |
| COMPLETED_WITH_UNCERTAINTY | COMPLETED (possible mapping) | Keep uncertainty and UNVERIFIED outcome. Never imply successful physical skill |
| ABSTAINED/EXPIRED/DEFERRED | no lossless direct state alias | Do not force FAILED/REJECTED; define reason/outcome payload or next candidate revision |
| OneiricAnnotation | future Core-D annotation | Keep SYNTHETIC_FIXTURE_ONLY, null Chronon/Life, supersedes; not a verified milestone |
| checkpoint PROVISIONAL_NONCANONICAL | no durable Core-C checkpoint | Inspection only, not restorable authority/history |

## Recommended next COG increment (not a rewrite)

Add a separately versioned, opt-in SESSION_SCOPED bridge using the real C0/C1 producer and a Core-B validator pinned by commit. Capture host context, immutable source object, original monotonic handoff and remaining lifetime. Missing creation/deadline, authenticated role or payload semantics must cause reject/defer, not invented defaults. Start with read-only investigation and synthetic Oneiric tests. Keep existing COG #1/#3/#4/#5 schemas untouched and original output available.

## Conformance exit gates

1. Producer is the real C0/C1 implementation, not a hand-copied JSON fixture; Core-B consumer sees explicit normalized types.
2. Rejected and delayed candidates cannot turn into fresh admissions; duplicate conversions do not renew TTL.
3. Reboot/session/context mismatch or stale task generation rejects outputs; task generation never becomes a role lease.
4. User/Life pause and evidence-wait remain distinguishable; resume revalidates original evidence lifetime and policy.
5. Specialized outcomes and synthetic/uncertain provenance are retained; a schema-valid record is not a factual observation.
6. No history commit, external communication, network, digital effect or physical movement; no positive Life binding.

This matrix completes the field-level audit portion of B-01. B-02 remains open until a real consumer uses the new ABI end-to-end. Existing 70+18 COG-02 compatibility tests in Core-B are regression evidence, not new-ABI adoption. New C1 compatibility CI must pin `a8ae925...`, without claiming its synthetic IMU data came from a live sensor.
