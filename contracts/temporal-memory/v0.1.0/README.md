# PR-CORE-D — Temporal / Memory / Oneiric ABI v0.1

**2026-11-01 — NON-NORMATIVE, NON-ACTUATING, NOT A CHRONOGRAF OR HISTORY RUNTIME.**

This draft defines ten strict, versioned JSON records for producer/consumer negotiation. Its parser does not authenticate any source, Chronograf TimeAtom, historical timestamp, Life, permission, Chronon, History commit or privacy erasure. `STATUS.json` remains `candidate / normative:false / accepted:false / runtime_implemented:false`. Merge does not promote a standard. This PR is additive: no edits to canonical `spec/`, mirrors, seeds, hash, existing Agent/Core-B/Core-C contracts, cognition or real-time runtime.

## Ownership boundaries
- **Chronograf** measures qualified time, clock domains, uncertainty, TimeAtom and opaque namespace-scoped AnchorRef64. An old source timestamp is *not* an anchor.
- **RGD-Physics / History** owns one logical canonical Chronon history and the current authenticated writer, causality, idempotent commit and lookup receipts. Core-D does not redefine the Chronon/Aion binary contract.
- **L1 Evidence Vault** owns protected original media, consent/retention and availability. **L2** Chronon history is canonical; **L3 memory projections** and **L4 autobiography** are derived/rebuildable. **L0** volatile telemetry may be consolidated later; never wait for persistence inside the Somatic reflex loop.
- **COG / Work / Imagination** may propose salience, oneiric reappraisal and structured learning. A proposal does not create history. Independent Core-B `HISTORY_COMMIT_REQUEST` permission and external Core-C verified Life/role ownership are needed at a real writer.
- **Identity/Life** enrollment, key custody and receiver-side fencing remain external. Valid schema/issuer/lease reference strings cannot mint grants.

## Ten candidate records

| Record | Responsibility |
|---|---|
| HistoricalTimeAssertion | Original event-time token, legacy clock domain, uncertainty; never self-reported as measured Chronograf time |
| ImportAnchorEvidence | Reference to actually measured *import* time; namespace, decimal uint64 handle and TimeAtom hash, externally verified |
| EvidenceAvailability | Visibility/redaction/retention reports across vault, projections, replicas, caches, backups; not proof of deletion |
| CognitiveCommitment | Structured learning/decision/correction candidate, not hidden reasoning or physical milestone verification |
| SalienceHint | Provisional importance, revisable with new evidence |
| MemoryAnnotation | New assessment, `supersedes`, original valid-time reference and asserted knowledge time; not an independent ledger |
| OneiricReview | A real computation about synthetic/replayed situations, not observed physical history |
| ContinuityCheckpoint | Derived pointers to verified history/Work/memory; cannot restore permissions or issue Life |
| HistoryCommitRequest | Privileged request with immutable payload digest, binding, current writer lease and independently gated effect refs |
| HistoryCommitReceipt | `COMMITTED`, `REJECTED`, `NOT_CONFIRMED` claims; never proof until authenticated writer/ledger validation |

## Non-retroactivity / bitemporal semantics

The existing Agent Temporal Profile v0.1 §11 suggests deriving a TimeAtom from a legacy source timestamp before issuing AnchorRef64. `TEMPORAL_DELTA.md` proposes a versioned correction: preserve past timestamp as **unattested assertion** and separately obtain an **actual import/commit-time** Chronograf measurement. Different clock domains cannot be compared by their raw numeric values. Anchor handles are opaque; full identity needs namespace, handle and TimeAtom SHA-256.

For `AS_KNOWN_AT(T)` the qualified historical knowledge/commit chronology, not a backdated claim inside a payload, determines what was known. `CURRENT_ASSESSMENT_OF(T_event)` reports the current derived interpretation of the same historical event. Earlier Chronons/annotations remain distinct. A dream ending `REVIEW_COMPLETED` may yield `REFUTED` or `UNRESOLVED`; it does not prove Paky-01 walked.

## Writer truth and negative authority

A request to persist a memory is not a successful persistence. The real writer must check actual principal/session, exclusive current role, Life binding, revocation, context, exact effect gate, payload, idempotency and independent measured commit time. A schema-valid `COMMITTED` text is insufficient proof. Disconnection or lost acknowledgement means `NOT_CONFIRMED`; query by the same scoped request/idempotency key rather than appending a duplicate. See `COMMIT_AND_QUERY.md`.

This package contains synthetic fixtures, a bounded offline validator and in-memory fake Chronograf/History/Memory tests. **Mocks are not authority services**, do not certify privacy erasure or provide hardware access. No new provider/consumer adoption by COG or real Chronograf is claimed; current GitHub CI pins Core-B #11, Core-C #13 and COG #6 independently to detect regressions. Real issuer/clock/history/effect-gate, privacy policy and cross-robot time remain explicit review gates.
