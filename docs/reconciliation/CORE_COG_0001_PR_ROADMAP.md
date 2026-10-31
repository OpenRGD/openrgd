# CORE-COG-0001 — Independent draft PR roadmap and conformance plan

**2026-10-31 / REVIEW PLANNING ONLY / NON-NORMATIVE**  
**Pinned Core:** `OpenRGD/openrgd@afe1a831b950a4e6560f0285a0103fc4eaa343b7`.  
**Related:** [CORE-COG handoff PR #8](https://github.com/OpenRGD/openrgd/pull/8), [tracking issue #9](https://github.com/OpenRGD/openrgd/issues/9), [COG #1](https://github.com/OpenRGD/rgd-cognition/pull/1), [COG #3](https://github.com/OpenRGD/rgd-cognition/pull/3).

All contract paths below are **PLANNED CANDIDATE PATHS, NOT EXISTING FILES OR ACCEPTED SCHEMAS** unless explicitly identified as current source. Use independent PRs, `STATUS.json` with `maturity:candidate`, `normative:false`, `accepted:false`, `stable_release_allowed:false`, and synthetic-only positive/negative fixtures. No accepted `spec/` changes without a separate governance decision.

## 0. PR series, owner and migration cost

| PR / dependency | Intended owner(s) | Planned change | Acceptance evidence / migration cost |
|---|---|---|---|
| **A — Core handoff (#8)**, draft, already open | Core coordination | Two sanitized non-normative handoff/decision docs | Documentation review only; L |
| **A2 — REVIEW-01 (this draft)**, independent of #8 | Core maintainer, COG/EXT/MEM representatives | Source matrix, reviewed Decision Log, PR roadmap/handoff | Links to exact upstream sources; zero normative file changes; L |
| **B — Kernel/Goal/Effect candidate ABI** | Core contracts; Work/COG consumers; Somatic Safety authority reviewer | Five roles, events, bounded admissions and effect scopes | Validate pure schemas, adversarial fixtures, external COG producer/consumer prototype; M |
| **C — Life/Agent/Runtime/Binding candidate ABI** | Core identity definitions; RGD-EXT/Identity-Life implementation | Scope of IDs, evidence, custody, epochs/leases, recovery/fork | Explicit positive/negative trust/recovery/fencing tests; no real enrollment; M/H |
| **D — Temporal/Memory/Oneiric candidate delta** | Chronograf time; RGD-Physics/history; Memory, Imagination, Work | Provenance of legacy times, writer interfaces, evidence availability, reappraisal and checkpoints | Cross-component fake writer/reader/consumer, bitemporal and privacy fixtures; M/H |
| **E — World/COG compatibility and migration RFC** | Core/World/COG/Embodied | Four world provider capabilities; consultative proposal adapter; selected static world_model deprecation plan | Pinned producer/consumer tests, dependency audit; H if normative spec changed |
| **Separate EXT forge/registry RFC** | RGD-EXT/registry authority | Local forge vs official publication/attestation; physical enrollment independent | Offline/registry trust and immutable receipt test; Core validates references only |

**Suggested order:** complete A2 review, then B and C as independent candidate branches with optional ID references; D coordinates with actual Temporal owner; E only after COG compatibility analysis. B/C may iterate in parallel as long as their `STATUS.json` remains candidate. PR #6/#7/#8 must not be force-merged or overwritten.

## 1. B — Kernel/Goal/Effect ABI (planned paths)

Base `contracts/kernel/v0.1.0/` with `STATUS.json`, `README.md`, `schemas/`, `examples/positive/`, `examples/negative/`, `validate.py` and `VALIDATION.md`.

| Planned schema | Key contract boundary |
|---|---|
| `schemas/kernel-descriptor.schema.json` | ID + fixed logical role + ABI version + provided/required event kinds + resource limits + failure policy + requested scopes (NOT granted authority) |
| `schemas/kernel-event.schema.json` | Event ID, kind/version, producer, correlation/idempotency, TTL, time quality, provenance, optional verified Life/binding/role-fence refs |
| `schemas/cognitive-goal-candidate.schema.json` | Explicit epistemic goal, evidence/context, origin, recursion depth, bounded budgets and expiry |
| `schemas/goal-admission-decision.schema.json` | Deterministic accept/defer/reject, policy revision, evaluated grants, reason, max scope, no grants minted |
| `schemas/agenda-transition.schema.json` | State transition, predecessor, task owner/lease, idempotency and causal provenance |
| `schemas/effect-request.schema.json` | Exactly one `INTERNAL_READ_ONLY`/`HISTORY_COMMIT_REQUEST`/`COMMUNICATION_REQUEST`/`DIGITAL_EFFECT_REQUEST`/`PHYSICAL_ACTION_REQUEST`, evidence and requested permissions |
| `schemas/effect-gate-decision.schema.json` | Independent gate's allow/deny/defer outcome, scoped proof/expiry, never an LLM-granted capability |

Implementation owner: `rgd-cognition` prototype `GoalAdmission` and Work loop; external communication/digital/history gates; physical gate remains independent Somatic authority. **No kernel runtime code added to Core.** Existing `orchestra.jsonc` weights are soft ranking, not positive authority.

**Positive fixtures:** all five roles described without processes, bounded internal goal, Work admitted after external policy, deterministic replay, reasoner outputs advisory cue.  
**Negative fixtures:** self-granted permission, unauthorized egress, phantom Life ID, invalid TTL, stale context or RTX response, unbounded recursive goals, duplicate event ID, second Coordinator, unaudited history write, simulated physical safety bypass.  
**Compatibility:** COG #1 `cog-v0.1` schemas untouched; COG #3 source-root context unchanged. Add candidate adapters rather than changing their tests.

## 2. C — Life/Agent/Runtime/Binding ABI (planned paths)

Base `contracts/identity/v0.1.0/` with `STATUS.json`, schemas, conformance fixtures, `THREAT_MODEL.md`, recovery/lease/migration notes.

| Planned schema | Purpose |
|---|---|
| `schemas/life-identity.schema.json` | Persistent cognitive-experiential lineage, authority/proof refs, creation/revocation state |
| `schemas/agent-descriptor.schema.json` | Agent software role and scoped capabilities, not an implicit `life_id` |
| `schemas/robot-life-binding.schema.json` | Verifiable Life ↔ enrolled robot/body link, provenance, status, uncertainty; never auto-issued |
| `schemas/life-activation.schema.json` | Binding activation epoch, conditions and proof; separate from each restart |
| `schemas/runtime-instance.schema.json` | Unique boot/session/process instance and parent/ref links; not a new Life |
| `schemas/role-lease.schema.json` | Role owner, fencing generation, validity, issuer/grant proof; old leaders rejected |
| `schemas/continuity-status.schema.json` | `UNBOUND/UNKNOWN/STALE/CONFLICT/RECOVERY_REQUIRED` plus evidence and safe behavior |

**Owner of runtime identity issuance, trust roots, locks and revocations is external.** Core publishes data types and validators only. `ProfileSnapshot.robot_id` remains legacy reference output on the pinned Core: new typed consumer uses `kernel_reference_id` and a **separately verified** physical `robot_id`.

**Positive fixtures:** same Life after verified reboot and LLM swap, fresh `runtime_instance_id`; valid manual/local provisional path remains unverified; lease generation increases on new leader; scoped verified bindings only with test authority evidence.  
**Negative fixtures:** no custody key, cloned backup, offline split-brain, stale old lease, disabled issuer, expired proof, alleged instance DID without proof, restore with conflicting watermark, unapproved migration or fork. Fail closed without creating a new Life.

**Migration:** if public `check/boot` payload is ever changed, version/deprecate output while supporting COG #3's `afe1a831…` pin and source-integrity-only state. No impersonation of physical registration from a source digest.

## 3. D — Temporal/Memory/Oneiric ABI (planned paths)

Base `contracts/temporal-memory/v0.1.0/` with `STATUS.json`, `TEMPORAL_DELTA.md`, schemas, synthetic ledger fixtures and tests. Existing `contracts/agent/v0.1.0` remains unchanged.

| Planned schema | Purpose / boundary |
|---|---|
| `schemas/historical-time-assertion.schema.json` | Unattested old event timestamp, original domain and quality |
| `schemas/import-anchor-evidence.schema.json` | Separate actual Chronograf measurement/anchor associated with import time |
| `schemas/evidence-availability.schema.json` | L1 digest/provenance/retention, loss/redaction, capture gaps |
| `schemas/cognitive-commitment.schema.json` | Structured significant decision/learning delta with authorized writer request, not token dump |
| `schemas/salience-hint.schema.json` | Provisional salience, uncertainty, event/evidence link, independent revision |
| `schemas/memory-annotation.schema.json` | Versioned interpretation, source refs, `supersedes`, knowledge/valid time |
| `schemas/oneiric-review.schema.json` | Reappraisal result (`SUPPORTED/REFUTED/UNRESOLVED`), simulated vs observed provenance |
| `schemas/continuity-checkpoint.schema.json` | Derived Life/binding refs, ledger watermark, agenda/Work and revision state; cannot restore grants |

**Owner:** Chronograf is time authority, Physics/history writer owns canonical Chronon ledger, Evidence Vault L1 retains protected payload, Memory owns L3/L4 derived views, Imagination/COG propose; Work admits reappraisal as ordinary bounded goal. None is a second writer.

**Positive fixtures:** observed first step with provisional hint → later review → evidence-backed annotation/milestone candidate; `AS_KNOWN_AT` preserves original belief while `CURRENT_ASSESSMENT_OF` shows update; history gap indicated. Legacy timestamp remains claim, actual import anchor measured at import.  
**Negative fixtures:** dream classified as real physical step; retro-issuing anchor with legacy timestamp; disconnected writer returns fake chronon; one sample=one Chronon mandatory claim; milestone confirmation derived only from `REVIEW_COMPLETED`; checkpoint resurrects revoked grant; erased evidence silently remains searchable.

**Privacy acceptance prerequisite:** deletion, consent/retention, cache/index/replica/backup handling, digest correlatability and historical proof availability. No public raw sensor/video/person data in fixtures.

## 4. E — World/COG compatibility and normative migration plan

First produce an **inventory-only** PR under `docs/reconciliation/`, then, if accepted, candidate `contracts/world/v0.1.0/` schemas:

- `world-state-reader.schema.json` — observed/queryable reality state with uncertainty.
- `world-predictor.schema.json` — forecasts and evidence refs, no physical authorization.
- `world-simulator.schema.json` — counterfactual results, synthetic provenance.
- `action-policy-provider.schema.json` — suggested candidates only, never raw hardware dispatch.
- `cognitive-proposal-adapter.schema.json` (separately versioned) — explicit transition between non-actuating COG proposal and an admitted action intent, **never** a dummy action intent.

Do not remove `spec/03_agency/world_model.jsonc` or modify Core `CognitionProposal` v0.1; first inventory refs from `kernel.jsonc`, `spec/`, `standard/`, `src/openrgd/seeds/default/spec/`, canonical tree hash, CLI `check/boot`, `tests/test_profile_inspection.py`, COG #3 `rgd-context-v0.2` and integration tests. Any normative `spec` change needs separate semver/governance, regenerated strict mirror and seed, new hash, backwards-compatibility adapter, and independent COG branch update.

## 5. Minimum cross-repository conformance grid

| Scenario | Core producer/validator | External consumer/reference | Must assert |
|---|---|---|---|
| BHL profile check/boot and source root | Existing `src/openrgd/core/profile.py` and canonical validator | COG #3 pinned resolver | Identical original output; no physical identity or actuation claim |
| Valid advisory kernel event | B candidate fixture/validator | COG Work lab | Deterministic admission without side effects |
| Unauthorized subgoal/tool request | B candidate negative fixture | COG/Effect gates | Reject or defer; no egress/history/motion |
| Reboot/LLM swap/role-fencing | C candidate fixtures | External Identity-Life authority fake | Same verified Life, new runtime, old writer fenced |
| Missing key/clone/partition | C candidate negative fixtures | Identity-Life fake | RECOVERY_REQUIRED or CONFLICT; no second primary writer |
| Legacy history import | D candidate fixtures | Fake Chronograf + Physics writer | Historical assertion ≠ newly attested anchor |
| Oneiric reinterpretation | D candidate ledger history | Fake Memory/Work/Imagination | Original Chronon unchanged; as-known/current results differ |
| Writer disconnected/privacy erasure | D candidate negative fixtures | Fake History/Memory stores | No false persistence; projections/availability updated |
| World provider replacement | E candidate interface fixtures | COG/World test providers | Same semantic types; synthetic results not sensor claims |
| COG proposal bridge | Existing Core Agent v0.1 + COG #1 candidate | Explicit adapter | No mutation of either old schema and no silent ActionIntent |

**Testing discipline:** JSON Schema 2020-12 validation; version mismatch and unknown-field negatives; serialization roundtrips if wire encoding is defined; deterministic/idempotency/fencing replay; recovery and fail-closed suites; **actual cross-repo producer/consumer integration** in a later PR. CI passing is not identity proof, safety certification or hardware benchmark.

## 6. Pre-merge release/acceptance checklist

- [ ] Owner has inspected all required historical source blobs and their provenance before microkernel ABI extraction.
- [ ] Candidate `STATUS.json` remains `accepted:false` even if the PR is merged.
- [ ] No permissions inferred from extension discovery, kernel role, model output, local forge or source hash.
- [ ] COG #1/#3 remain separately reviewable; no required retarget/rebase on these docs.
- [ ] Core `main`, `spec/`, `standard/` and seed unchanged by A/A2 review.
- [ ] Negative fixtures cover stale delegation, split-brain, synthetic→physical mislabelling, legacy time, unauthorized effects.
- [ ] Privacy and safety owner review before any real Life/Chronon/Robot claims.
- [ ] Contract acceptance requires explicit governance, maturity update, versioning and reference flows; no automatic tag/release.
- [ ] No private robot-instance records, identity keys, raw person media or unpublished RFC source bundles in public GitHub.

## 7. Immediate CORE → COG/MEM/EXT handoff

**To COG:** continue COG-01 and COG-02 unchanged, candidate/offline/non-actuating. A session-scoped bounded `GoalAdmission` experiment may be developed under restrictive fake policy. Do **not** claim persistent Agenda C, verified Life, registered physical robot or memory. Preserve source-root pin and null positive identities until a verified Core identity binding exists.

**To RGD-EXT:** keep `forge_id`/digest/local validation separate from issuer receipt, `artifact_id` and physical/Life enrollment. No registration automatically via `rgd check`, `rgd boot`, package install or local forge. Provide trust-state fixtures for Core identity contracts.

**To Chronograf / RGD-Physics / Memory:** align legacy import semantics before creating historical Chronons; expose actual writer/read/anchor proof and evidence availability; protect L1/media and retention, support bitemporal derived annotations and no second history. Proposed Oneiric commits require admitted Work goal and authorized history writer.

**To Somatic/Embodied:** physical safety/reflex never waits on cognition/ANN; candidate cognitive proposals cannot reach a Body Adapter as instructions; future positive actuation requires separate capability, operation safety and low-level gates.

**To Core maintainers:** retain normative `spec` and pinned toolchain; review A2 matrix then approve independent candidate ABI design. No new runtime in Canonical Core.

**Current status:** planned candidate interfaces only; A/A2 documents are the sole GitHub write scope of this phase.
