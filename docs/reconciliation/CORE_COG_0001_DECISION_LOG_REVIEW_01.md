# CORE-COG-0001_DECISION_LOG — REVIEW-01

**Date:** 2026-10-31  
**Maturity:** DRAFT / NON-NORMATIVE / no acceptance implied  
**Evidence baseline:** `OpenRGD/openrgd@afe1a831b950a4e6560f0285a0103fc4eaa343b7`; `rgd-cognition` draft PR #1 `aef3cd4be6c9405d3c8069d90b031484e11d6f4b` and stacked PR #3 `940757af306dc538d3f3e0c70fed5f0671024be9`.  
**Relation:** supplements (does not supersede, modify or merge) [PR #8 Decision Log](https://github.com/OpenRGD/openrgd/blob/docs/core-cog-0001-handoff-20261031/docs/reconciliation/CORE_COG_0001_DECISION_LOG_2026_10_31.md) and [issue #9](https://github.com/OpenRGD/openrgd/issues/9).

## Decision state vocabulary

- **USER_DIRECTION** — confirmed operator design direction, not a governance-approved standard.
- **DESIGN_CONFIRMED / CONTRACT_CANDIDATE** — agreed conceptual separation; shared ABI still unaccepted.
- **SOURCE_EXISTING** — actual current code, schema, or documented claim; does not certify runtime evidence.
- **PROPOSED / REVIEW_NEEDED** — candidate requires explicit architecture/maintainer decision.
- **CONFLICT_VERIFIED** — two currently visible interface definitions or procedures disagree.
- **NON_NEGOTIABLE_BOUNDARY** — architecture/security constraint for the review; not a declaration of certification.
- **OPEN_GOVERNANCE / BLOCKED_BY_EVIDENCE** — owner, proofs, source inventory, or tests missing.

No entry below has `ACCEPTED_STANDARD` or `DEPLOYED` status.

| ID | Decision or question | Review-01 state | Owner(s) | Evidence / gate |
|---|---|---|---|---|
| **D001** | Five logical microkernels `Safety, Life, Work, Relation, Imagination` first-class; versioned descriptor/event ABI | USER_DIRECTION; ABI PROPOSED | Core ABI + external Somatic | `kernel.jsonc` has supervisor/orchestra but not five accepted ABI roles; historical eight blobs require pinned audit. Do not import runtime. |
| **D002** | Durable `life_id` distinct from `agent_id`, `robot_id`, `persona_id`, `runtime_instance_id` | PROPOSED; positive binding unproven | Core identity contracts / Identity-Life authority | `ProfileSnapshot.robot_id` is model reference; no mint-on-boot; require enrollment/recovery/fork/lease fixtures. |
| **D003** | Local forge/digest provenance independent of attested artifact publication/registry and enrollment | USER_DIRECTION; PROTOCOL_CANDIDATE | RGD-EXT / Registry; Core validation | Source hash proves bytes only; no implicit issuer/physical identity/actuation. |
| **D004** | ML-001 L0–L4, Chronon canonical experience history; projections and autobiography derived | DESIGN_CONFIRMED; CONTRACT_CANDIDATE | Chronograf / Physics-History / Memory | Existing `03_CHRONON_MEMORY_CONTRACT.md` is candidate; no canonical writer or storage conformance claimed. |
| **D005** | Agenda C autonomous epistemic goal pursuit bounded by policy | USER_DIRECTION; NOT_IMPLEMENTED_IN_CORE | COG/Work, external policy gate | COG-01 is synchronous turn host, not persistent agenda; no digital/voice/physical grant. |
| **D006** | Single admission/resource arbitration ownership; Attention and Work not co-authority | PROPOSED / REVIEW_NEEDED | Core Kernel/Effect ABI + COG Work | `GoalAdmission` consumes grants, Coordinator handles only non-critical budgets; each subgoal re-admitted. |
| **D007** | ONEIRIC-001 reappraisal with synthetic provenance and non-destructive versioned annotations | PROPOSED / REVIEW_NEEDED | Imagination / Memory / Work / History writer | `oneiric_state.jsonc` exists but is not kernel-selected. Cannot alter original Chronon or claim physical milestone. |
| **D008** | Separate effect request scopes: internal, history, communication, digital, physical | PROPOSED / REVIEW_NEEDED | Core Authority + independent effect gates | `HISTORY_COMMIT_REQUEST` privileged; `INTERNAL_READ_ONLY` cannot write ledger; digital and communication not implied by safety gate. |
| **D009** | Bitemporal `AS_KNOWN_AT` vs `CURRENT_ASSESSMENT_OF`; no retro-attested legacy anchors | CONFLICT_VERIFIED | Chronograf / Physics / Memory | Temporal Profile v0.1 `11` says issue an AnchorRef64 from legacy timestamp; versioned delta must separate past claim from new import anchor. |
| **D010** | New consultative `CognitiveProposal` must not be Core `CognitionProposal` requiring `action_intent` | CONFLICT_VERIFIED | Core Agent + COG / Somatic translator | Existing Core JSON Schema requires `action_intent`; COG #1 no-action proposal is independently typed. Versioned bridge only. |
| **D011** | Replace fixed illustrative world state with `WorldStateReader/WorldPredictor/WorldSimulator/ActionPolicyProvider` | USER_DIRECTION; MIGRATION_REVIEW_REQUIRED | Core / World / COG / Somatic | `world_model.jsonc` is kernel-selected; removing changes hash/mirror/seed/check/boot and COG #3's pin. |
| **D012** | No false identity, time anchor, history, issuer or actuation authority; no unreviewed main/deploy | NON_NEGOTIABLE_BOUNDARY | Every owner | Candidate schemas never confer grants; Somatic gate independent of model; no private data in public PR. |
| **D013 (review)** | Role fencing generation separate from Life activation epoch; stale delegations/RTX responses rejected | PROPOSED / REVIEW_NEEDED | Identity-Life + Work/COG | Remote inference is not second Life leader; offline partition cannot be solved by local lock only. |
| **D014 (review)** | Retention/erasure applies to protected evidence, projections, replicas and backups despite logical append-only history | OPEN_GOVERNANCE | History/Memory + privacy owner | Existing agent `DECISIONS.md` lists legal erasure/tombstone unresolved; require legal/technical policy before normative claims. |
| **D015 (review)** | Candidate interfaces evolve without redefining COG #1/#3 or asserting local prototype contracts are normative | SOURCE_EXISTING + PROPOSED | Core/COG | COG #3 pins Core source/toolchain SHA and returns UNBOUND identity; preserve its test baseline and no-actuation semantics. |
| **D016 (review)** | Documentation/package work must reflect actual GitHub `main`, not unpublished local extension/somatic revisions | SOURCE_EXISTING / REVIEW_NEEDED | Core maintainers | Current `main` lacks accepted Extension Architecture and Command Plugin ABI trees; reconcile separately before cross-import. |

## Explicit architecture questions requiring acceptance

1. **Life initial enrollment:** what proof and custody establish `LOCAL_PROVISIONAL` vs verified physical/Life binding? Who can issue/revoke and how is key loss recovered?
2. **Primary role fencing:** one leader for each exclusive role on Paky-01, with distinct activation and lease/generation; behavior on partition, old writer, cloned restore, and delegation.
3. **Kernel ABI:** exact names, `KernelDescriptor/KernelEvent` versioning, migration of the eight historical blobs, compatibility guarantees and resource quotas. Safety in Somatic remains independent.
4. **Effect gates:** who issues/verifies permission for history commit, communication, digital changes and physical movement? What if a policy grant is revoked while pending?
5. **Chronon/Time:** cross-domain temporal claims, historical import semantics, data retention, verified writer state and ability to query as-known history.
6. **Oneiric:** where does a provisional `SalienceHint` live; how do `supersedes`, known-time, simulated provenance and consensus of reviews work?
7. **World modeling:** independent providers' ABI, read-only source pin stability, deprecation schedule for selected static model.
8. **Governance:** published ABI status machine, release/version plan, consent/privacy policy, and scope of future multi-body Life.

## Decisions NOT taken in REVIEW-01

- No acceptance or promotion of any proposal to normative Core status.
- No mandate for five OS processes or any new microkernel daemon.
- No real Life ID, robot ID, issuer receipt, Chronograf anchor or actor role lease issued.
- No activation of autonomous agenda, model egress, Voice, CAN, device movement or runtime process.
- No deletion or modification of `spec/03_agency/world_model.jsonc`, ``pec` source hash, mirrors or seeds.
- No requirement to merge/retarget COG PR #1/#3 or Core PR #6/#7/#8.
- No claim that archived/recovered microkernel source blobs have been reviewed line-by-line.

## Next disposition

Maintain this document as **Review-01**, obtain owners' comments, and only then produce candidate schemas with separate machine-readable `STATUS.json`, conformance fixtures, and validated cross-project producer/consumer flows. See `CORE_COG_0001_PR_ROADMAP.md` and `CORE_COG_0001_REVIEW_01.md`.
