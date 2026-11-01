# P0 discrepancy register — REVIEW-02

2026-11-01 / non-normative. Findings distinguish source facts from proposed resolutions. IDs P0-Rxxx are review tracking IDs, not accepted ADRs. Earlier handoffs and logs remain historical evidence.

| ID | Observed mismatch | Minimal disposition | Owner / closure gate |
|---|---|---|---|
| P0-R001 | GitHub main and locally delivered v0.2/0.2.1 reviews contain different contracts and kernel sources | Keep pins independent. Do not claim local Extension/Command/Somatic code is in main | Core: explicit port PR and regression tests |
| P0-R002 | Earlier reviews could not inspect eight historical microkernel sources; eight related texts are now available in uploaded review archives | Audit local content now, retain NOT_VERIFIED historical equivalence; do not assign an invented original Git SHA | Core: original source inventory match |
| P0-R003 | C0/C1 local GoalCandidate/Admission and Core-B have different states, timing and context fields | Explicit bridge; no schema alias or dummy ActionIntent | COG/Core: new producer/consumer integration |
| P0-R004 | C0 task generation changes on transitions; Core-B role fencing denotes authority ownership | Never copy task generation into role_fencing_generation | Identity/Work: real exclusive-role authority |
| P0-R005 | C0 publishes ttl_ms but its public view does not expose creation/deadline; a delayed conversion could renew lifetime | Capture trusted monotonic receipt/deadline at original handoff; preserve remaining lifetime, clock domain and dedup | COG: expired queued output rejected |
| P0-R006 | origin_role_hint is a local lab hint, not authenticated kernel identity | Do not promote a string to trusted origin/provenance | COG/Authority: source binding and consumer validation |
| P0-R007 | Core profile.robot_id means kernel reference; future Life/Robot contracts mean enrolled identities | Preserve old API/pins; use kernel_reference_id in a versioned view, verify physical identity separately | Core-C + COG migration |
| P0-R008 | A role lease or positive continuity claim may be mistaken for effect permission | Require current receipt/context/fence AND separate effect gate; no grant from identity schema | Identity/Effect gates |
| P0-R009 | Local historical Relation uses ActionIntent for speech; new five-effect taxonomy separates communication/digital/physical | Preserve source as evidence; port outputs into appropriate requests, not all into a motor pipeline | Relation + Communication Gate |
| P0-R010 | Local Safety mixes operation admission and 1 kHz reflex; Somatic archive separates them | Retain independent reflex; Core-B JSON events are not a 1 kHz wire ABI | Core/Somatic: prototype and timing evidence |
| P0-R011 | Legacy Temporal v0.1 import says create TimeAtom from old timestamp | Versioned delta: old timestamp assertion != current measured import anchor; preserve original quality | Chronograf/Physics/Memory |
| P0-R012 | Significant-events-only archive policy vs ML-001 event-triggered + periodic coverage + evidence bursts | Proposed ML-001 superseding policy needs benchmark; neither every sample nor completeness is implied | History/Ingress |
| P0-R013 | Local coordinator has shared-memory/AION, fixed pool, boot-order and restart assumptions | Keep transport/deployment runtime-specific, no five-process requirement; reject blind restart-to-authority | Runtime owners |
| P0-R014 | C0 synthetic Oneiric annotation could be mistaken for a persistent milestone | Retain SYNTHETIC_FIXTURE_ONLY; writer and evidence verification separate; completed review != confirmed event | Imagination/Memory/Work |
| P0-R015 | Static world_model selected on main, aspirations/oneiric descriptions unselected | Do not delete or auto-select; inventory before versioned migration | Core-E |

## Recovered local microkernel crosswalk

The exact uploaded source archives and per-file SHA-256 are in SOURCE_INVENTORY.json. These are reviewed source texts, not recovered executable runtimes or an attested Git lineage. `kernel_v3.jsonc` is explicitly historical and superseded inside the archive; current archive `kernel.jsonc` and `kernel_v2.jsonc` are additional neighboring revisions, not silently interchangeable.

| Local source | Reuse concept | Must adapt or leave runtime-owned |
|---|---|---|
| safety_kernel | negative authority, non-maskable reflex, raw telemetry not one Chronon per sample | operation vs reflex plane, 1 kHz targets not evidence; no Core-B event transport in reflex loop |
| life_kernel | homeostasis/resource envelope and goal proposals | authenticated telemetry, UNKNOWN values, resource actions separate from physical action; no Life issuance |
| work_kernel | task planning, no raw actuator commands, no fallback authority inheritance | deterministic admission before Work, per-subgoal re-admission, aggregate budgets, versioned result states |
| relation_kernel | social proposals, trust never grants actuation | communication and digital effects separated from historical speech ActionIntent |
| imagination_kernel | predictions/candidates, synthetic != physical, no direct policy/weight updates | Oneiric through Work, persistent changes through writer, no hardcoded sleep-only gate |
| kernel_modules_registry | roles and priority != authority | one Coordinator, deployment optional; timing and shared memory engineering targets |
| aion_struct | representation/transport do not authorize execution | retain separate binary codec and Chronograf ownership; JSON ABI does not freeze AION encoding |
| kernel_v3 | modular composition concept only | historical fixed memory, zero-copy, CHECK_HEADER_HASH_ONLY, restart-and-log and synchronization assumptions are not accepted security/runtime defaults |

## Shared contract boundaries for the remaining P0

### Forge / publication / identity

Keep source_root and exact distribution artifact digest distinct. Forge has a local validation record, not an issuer receipt. Publishing different bytes creates a different artifact; neither receipt nor digest enrolls a body or creates Life. Core-C references external enrollment/proofs rather than fabricating registry services. Registry trust roots, receipt signatures, key custody and offline revocation remain proposals requiring owners.

### Temporal / Chronon / Memory

Proposed Core-D delta must preserve (1) original event/valid-time claim and clock quality, (2) actual ingestion/commit anchor, (3) interpretation knowledge/revision time. AS_KNOWN_AT is not implemented by replacing old event timestamps. A single logical history may be replicated, but authoritative writer ownership must be fenced per role/scope. HistoryCommitRequest is privileged even on a local disk. Acknowledged commit, request timeout and disconnected writer are distinct outcomes; retries need stable idempotency and queryable receipts. No fake anchor or successful persistence on NOT_CONNECTED.

### Checkpoint and Oneiric

A checkpoint references the confirmed ledger watermark, current identity binding and learned revisions; it is not a parallel history or a saved permission grant. Restore revalidates revocation and current role owner. Reappraisal appends a versioned annotation with evidence, supersedes and known-time. Simulated scenarios never become physical observations. A real computation of a dream can be committed as computation, only by the authorized history writer. Preserve learning deltas, not hidden model reasoning. Evidence erasure/retention propagates to projections/cache/replicas/backups according to the still-unapproved privacy profile; immutable logical ordering does not promise perpetual raw-media retention.

## Status corrections, not promotions

- D001: local review texts are now inspectable, original historical equivalence still open; five-role direction unchanged.
- D005: autonomous agenda lab C0 and attention C1 exist in external drafts; product-level persistent Agenda C remains unimplemented.
- D002/D006/D007/D008: proposals remain proposals despite this consolidation.
- D009/D010: temporal legacy and CognitionProposal/CognitiveProposal conflicts remain versioned migration work.
- D016: exact GitHub main vs uploaded archive distinction is recorded; source alignment still requires reviewed port PRs.
