# CORE-COG-0001_REVIEW-01 — Canonical Core source audit

**Date:** 2026-10-31  
**Status:** REVIEW-01 / EVIDENCE-BACKED / NON-NORMATIVE  
**Scope:** OpenRGD/openrgd `main` @ `afe1a831b950a4e6560f0285a0103fc4eaa343b7`, with inspected draft PRs.  
**Tracking:** [Core PR #8](https://github.com/OpenRGD/openrgd/pull/8), [Core issue #9](https://github.com/OpenRGD/openrgd/issues/9), [COG PR #1](https://github.com/OpenRGD/rgd-cognition/pull/1), [COG PR #3](https://github.com/OpenRGD/rgd-cognition/pull/3).

This is a sanitized implementation-boundary review, **not an accepted ABI**, physical robot enrollment, Life creation, Chronon write, firmware/runtime release, or permission grant. It supplements, and does not edit, PR #8. No `spec/`, `standard/`, packaged seed, hash policy, CLI, running robot, or `main` changes are proposed in this PR.

## 1. Verified baseline and scope limits

- GitHub `main` HEAD: `afe1a831b950a4e6560f0285a0103fc4eaa343b7`; full recursive tree inspected (451 entries, not truncated).
- `spec/00_core/kernel.jsonc` `meta_group.version_semver_str = 0.1.0`, `rgd_version_semver_str = 0.2.0`, model/reference ID `did:rgd:berkeley-humanoid-lite`; these axes are separately stated in `VERSIONING.md`. This is **not** evidence of physical enrollment.
- `src/openrgd/core/profile.py` exposes `ProfileSnapshot.robot_id` from `kernel.meta_group.id` and the `check` validation payload's `robot_id`; changing semantics in place would break public consumers and tests. COG-02 already maps this to `kernel_reference_id` in its own read-only view.
- Current kernel selection includes `03_agency/world_model.jsonc` and `04_volition/orchestra.jsonc`, but not `03_agency/oneiric_state.jsonc` or `04_volition/aspirations.jsonc`. Existence in `spec/` is not activation.
- Current `contracts/agent/v0.1.0/STATUS.json` is `candidate`, `normative:false`, `accepted:false`. The GitHub `main` tree currently contains **four** JSON Schemas in `contracts/agent/v0.1.0/schemas/`; other semantics are candidate Markdown, not runtime services.
- `contracts/agent/v0.1.0/schemas/cognition-proposal.schema.json` explicitly REQUIRES `action_intent`. COG-01 independently defines non-actuating `CognitiveProposal` and `CognitiveTrace` candidate types; do not alias or rewrite.
- `contracts/agent/v0.1.0/contracts/00_TEMPORAL_CHRONON_PROFILE.md` section 11 instructs legacy import to create a TimeAtom from a historic timestamp and issue AnchorRef64. The new memory proposal requires separating **historical-time assertion** from **newly measured import/commit anchor**; the old text is a migration conflict, not proof of old anchor issuance.
- `spec/02_operation/social_identity.jsonc` includes reference-shaped DID/RIN/registry URI values; no external proof of registration is provided by those fields. Source integrity, issuer trust, artifact publication, robot enrollment, Life binding, and role ownership must be independently established.
- On GitHub `main` the previous locally prepared Extension Architecture, Command Plugin ABI and Somatic-alignment reviews are **not present as accepted contract trees**. Do not silently rely on their unpublished state for this audit. Reconcile them in later reviewed integration work.
- PR #6 (multimodal feedback) and PR #7 (visual/CAD assets) remain open drafts; avoid overlapping changes. PR #8 is two documents under `docs/reconciliation/` only.
- Historical eight microkernel/registry/coordinator/AION source blobs are **reported by the handoff but not available as accepted microkernel ABI files in the inspected `main` tree**. The exact historical implementations are **not audited by this review**. Obtain their pinned blob inventory before deciding which methods, state machines, or serialization can be retained.

## 2. Evidence matrix — existing vs requested

`EXISTING` = source/schema currently present. `REUSE` = stable concept useful as input, not necessarily normative. `CANDIDATE` = a proposed new interface. `CONFLICT` = incompatible definitions. `NEEDS GOVERNANCE` = requires explicit external owner and acceptance.

| Subject | Source evidence / current state | Classification | Owner / consequence |
|---|---|---|---|
| Five roles Safety/Life/Work/Relation/Imagination | `kernel.jsonc` has coordination, safety supervisor and orchestration, but no accepted versioned five-kernel event ABI | REUSE + CANDIDATE | Core defines ABI; Somatic owns physical safety; no forced five processes |
| Legacy microkernel blobs | Historical provenance stated in handoff, not accessible in current accepted tree | NEEDS GOVERNANCE | Audit source hashes and ownership before importing code |
| Kernel/reference vs physical identity | `profile.py` uses reference as `robot_id`; `social_identity.jsonc` contains declarative identity literals | CONFLICT | Versioned alias/deprecation, avoid changing output on COG-02 pin |
| Life continuity | No validated LifeIdentity/RobotLifeBinding/role-fencing implementation in Core `main` | CANDIDATE | Identity/Life authority outside Core; no boot-time minting |
| Forge vs publication | Canonical integrity tooling exists, but not a registered issuer/receipt in Core | REUSE + CANDIDATE | RGD-EXT registry, no implicit registration or grants |
| COG grounding | COG #3 pins Core producer/root; source integrity only, all positive Life/robot bindings null | EXISTING (external draft) | Preserve source verifier, add separate future identity resolver |
| Action/consultative proposal | Core v0.1 mandatory `action_intent` vs COG consultative no-action proposal | CONFLICT | New versioned bridge; no in-place edit |
| Autonomous goal admission | COG #1 has bounded synchronous turn host, NOT autonomous agenda | CANDIDATE | Work/COG implement admission after typed policy grants |
| Effect taxonomy | Existing safety/permission semantics, no accepted five-scope EffectRequest/Decision ABI | CANDIDATE | Core authority contract, separate history/voice/digital/physical gates |
| World provider interfaces | `world_model.jsonc` selected and illustrative, no actual provider ABI | REUSE + CANDIDATE | Versioned migration, not removal |
| Aspirations & orchestra | `aspirations.jsonc` unselected, `orchestra.jsonc` selected; weighting is not grant | REUSE | Governance defines mission; Coordinator only non-critical resources |
| Chronon & Memory | Candidate temporal and projection text/schema, no verified writer or L0-L4 operational ledger | REUSE + CANDIDATE | Chronograf time; Physics/history; Memory projections |
| Oneiric | `oneiric_state.jsonc` unselected; `03_CHRONON_MEMORY_CONTRACT.md` distinguishes synthetic from physical | REUSE + CANDIDATE | Imagination/Work/Memory, no retroactive history mutation |
| Bitemporal legacy import | Current Temporal Profile `11` vs newly required historical/unattested time separation | CONFLICT | Chronograf/Physics/Memory acceptance before importer |
| Privacy/erasure | Agent contracts explicitly leave legal erasure/tombstone unresolved | NEEDS GOVERNANCE | Evidence/Memory/registry data controller, propagate deletion |
| Safety | Core docs and `safety_critical.jsonc` are declarative; no physical runtime authority verified | REUSE / HARD BOUNDARY | Somatic/Body gate independent of COG, no hardware effects |

**Migration cost labels (planning, not measured):** L = isolated candidate docs/schemas/fixtures; M = cross-repo producer/consumer adaptation; H = canonical `spec` + mirror/seed/hash/CLI/COG pin migration or identity/history recovery. Microkernel ABI M; Life binding M/H; Temporal import M/H; World profile H; consultative proposal M; simple candidate event/effect schema L/M.

## 3. Minimal microkernel ABI proposal — not yet schema

Exactly five **logical roles**, not five mandatory processes:

| Role | Consumes | Emits (proposed) | Negative/positive authority ceiling |
|---|---|---|---|
| **Safety** | qualified safety/health evidence, policy state | safety advisories or independent Somatic veto/reflex events | Physical reflex authority remains independent in Somatic/Body Gate; cognition does not override |
| **Life** | qualified homeostatic data, continuity status | bounded need/resource proposals | No fabricated state or direct grants; `UNKNOWN` remains unknown |
| **Work** | admitted goal + finite budgets | TaskPlan, progress/outcome, bounded subgoal candidates | May manage task lifecycle, not create rights or move hardware |
| **Relation** | social context, communication policy reference | communication candidates, relationship observations | External Communication Gate decides actual emission |
| **Imagination** | memory/evidence refs, world model interfaces | hypothetical scenes, OneiricReview proposals | Synthetic provenance; no physical event or self-issued history |

Proposed `KernelDescriptor`: `kernel_id`, `role`, `api_version`, `implementation_ref`, `event_input_types`, `event_output_types`, `required_capability_refs`, `requested_effect_scopes`, `resource_bounds`, `failure_policy`, `provenance_profile`. Requested scopes are **not grants**.

Proposed `KernelEvent`: versioned namespace/kind, producer ID, immutable correlation/idempotency key, source clock/domain and time quality, context revision, Life/binding/role-fence references **when verified**, TTL/deadline, evidence refs, typed payload, synthetic/observed provenance. Malformed, expired, conflicting, ambiguous or unverified privileged events fail closed. No automatic five-service runtime topology or broad type-erased event bus is mandated.

**Single arbitration chain** (no split ownership): mission/policy RGD/Volition → deterministic `GoalAdmission` (COG/Work prototype consumes external grants) → one non-critical resource Coordinator → Work lifecycle. Attention merely selects cues; Life proposes needs; Relation proposes communications; Imagination proposes hypotheses. Every generated subgoal returns to admission; no inherited permission. Somatic Safety remains an independent veto during physical execution.

**Five disjoint EffectRequest categories**: `INTERNAL_READ_ONLY`; `HISTORY_COMMIT_REQUEST`; `COMMUNICATION_REQUEST`; `DIGITAL_EFFECT_REQUEST`; `PHYSICAL_ACTION_REQUEST`. `HISTORY_COMMIT_REQUEST` is a privileged history write, not read-only. Each external effect requires its own policy/authority and idempotent gate; “goal admitted” never means “effect permitted.”

## 4. Life / Agent / Runtime / Robot contract direction

Separate at least: model `bundle_id` and `source_root`; local `forge_id` and immutable publication `artifact_id` / `artifact_digest`; enrolled physical `robot_id`/`body_instance_id`; persistent lineage `life_id`; cognitive software `agent_id`; public `persona_id`; ephemeral `runtime_instance_id`, `boot_id`, `session_id`.

Candidate objects: `LifeIdentity`, `AgentDescriptor`, `RobotLifeBinding`, `LifeActivation`, `RuntimeInstance`, `RoleLease/Fencing`, `ContinuityStatus`. Persist verified identity custody and history checkpoints via external authority, **not** the Core parser. Distinguish activation epoch from role-fencing generation. A reloaded process must not mint a new Life silently. On missing/invalid records: `RECOVERY_REQUIRED`; on stale/competing leader: `STALE`/`CONFLICT`, no privileged commits or effects. An offline lock is not global split-brain proof. Cloned backups, migration and fork require separate trust decisions.

For COG #3, preserve `robot_id:null` / `life_id:null` and `kernel_reference_id` under `SOURCE_INTEGRITY_VERIFIED` until genuine binding evidence exists. Do not patch the pinned `afe1…` Core source/API or claim an issuer/robot identity from a DID literal.

## 5. Temporal / Memory / Oneiric interoperability direction

**Ownership:** Chronograf measures/anchors; RGD-Physics/history writer creates canonically versioned Chronon envelopes; L1 evidence vault holds protected media/hash/retention; L2 is a single canonical Chronon history, not necessarily an exhaustive stream; L3 Memory and L4 autobiography are derived projections; COG/Work/Imagination may propose changes but are not ledger writers. L0 is volatile.

Proposed contracts: `HistoricalTimeAssertion` (source event-time claim plus its uncertain domain), `ImportAnchorEvidence` (actual new importer/Chronograf anchor), `EvidenceAvailability` (gaps, redaction, retention), `SalienceHint`, `MemoryAnnotation`, `OneiricReview`, `CognitiveCommitment`, `ContinuityCheckpoint`. Preserve time axes for `AS_KNOWN_AT(T)` and `CURRENT_ASSESSMENT_OF(T)`. Oneiric review is itself a real computational event if an authorized writer records it; simulated motion is **never** a witnessed physical event. `REVIEW_COMPLETED` never implies `MILESTONE_CONFIRMED`.

Legacy migration **must not** retro-attest an old timestamp as Chronograf's newly observed time: retain the old timestamp as unattested assertion; attach a separate current import/commit anchor and explicit temporal quality. Do not modify candidate Temporal Profile v0.1 in place without a versioned delta and coordinated review.

Derived checkpoints are accelerators, not a competing history authority and not permission snapshots. On restart verify ledger watermark, leases, revocation, evidence availability and profile pin; rebuild or enter recovery. Logical append-only provenance must coexist with authenticated privacy erasure/redaction across backups, indexes and replicas; governance is open.

## 6. World / legacy compatibility

`world_model.jsonc` currently contains example GIS, grasp probabilities and scene references, selected by `kernel.module_loading_order_list`. Do not delete or rewrite it; produce a dependency inventory covering `kernel`, `spec`, `standard`, packaged seed, hash root, `check/boot` CLI, reference tests and COG #3 pinned context. Propose **four independent provider interfaces**: `WorldStateReader`, `WorldPredictor`, `WorldSimulator`, `ActionPolicyProvider`. Their implementation remains external. A VLA policy must not inherit motion authorization from model selection.

The Core candidate `CognitionProposal` with mandatory `action_intent` must remain unchanged. The COG consultative `CognitiveProposal` remains non-actuating and distinct. Only a separately versioned adapter may convert an admitted/authorized proposal into future action semantics; no dummy ActionIntent for thought, recall or research.

## 7. Immediate safe paths and blockers

**Available now (candidate lab):** COG-01 bounded offline non-actuating turns; COG-02 source-root-pinned read-only RGD context; synthetic GoalAdmission prototype constrained to `INTERNAL_READ_ONLY` with no Life/writer/voice/device claims; offline test fixtures and policy-negative examples.

**Blocked until independent proofs:** persistent Life binding/enrollment; primary role exclusivity across a partition; stable RGD/COG/Somatic effect grants; canonical Chronon writes; autonomous persistent agenda; Oneiric persistent memories/milestones; physical/digital/voice side effects. Passing tests or installing a schema cannot unlock these.

## 8. Decision status and acceptance rules

This review distinguishes **operator direction** from **accepted standard**. D001/D003/D005 are operator directions awaiting ABI/protocol implementation; D002/D006/D007/D008 are proposals; D004 is design-confirmed with candidate contracts; D009/D010 are verified compatibility gaps; D011 is deprecation intent awaiting governance; D012 is a non-negotiable boundary. Detailed dispositions are in `CORE_COG_0001_DECISION_LOG_REVIEW_01.md`.

**Promotion gates:** explicit governance approval; versioned schemas/positive and adversarial fixtures; cross-repo producer/consumer reference flow; backwards compatibility and deprecation evidence; threat/privacy/retention review; no false physical/issuer/time attestations. PR merge alone leaves status `candidate / accepted:false / normative:false`. See `CORE_COG_0001_PR_ROADMAP.md`.

## 9. Reproducibility and limitations

Source audit used GitHub repository/PR/issue metadata, `main` file tree, and representative exact source files. No claim of a running Life, approved ABI, robot instance, physical commissioning, measured 1 kHz, or simulated result as fact. CI statuses stated in COG PR descriptions were read as **PR claims**, not independently re-run by this review. Full historical microkernel blobs and private RFC appendices were not attached to this public Core tree; any detailed old-ABI compatibility remains **blocked pending a pinned, sanitized inventory**.

**Next:** seek maintainer review of the matrix and contract ownership, then open independent *candidate* contract PRs B/C/D/E after approved schema design. Nothing in this review changes the canonical source tree or an external runtime.
