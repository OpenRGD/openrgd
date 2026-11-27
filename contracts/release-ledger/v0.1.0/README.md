# EXT-01B.3C — Immutable Release Ledger (candidate reservation profile)

**2026-11-27 · NON-NORMATIVE · no production release admission, publishing or execution.**
Core owns this contract; the official OpenRGD registry (rgd-modules) owns the ledger and any future publication transaction. Console/CLI/OS are catalog clients, not direct database writers. This is not a Chronon ledger, a Life identity service, a second catalog or a replacement for TUF.

## Identity, history and operations

A release key is (catalog_id,module_id,module_version), with the EXT-01A identifier/version vocabulary. The ledger_id identifies an explicitly initialized durable ledger lineage; it is not a release identifier. The initial profile permanently binds each reserved release key to the **raw ReleaseProposal SHA-256** (which already binds exact manifest and artifact bytes) and retains those bytes. No repackaging under the same version, no implicit version normalization, no replacement with a newly signed differing proposal. Existing legacy v0.1 keys are reserved by a pinned catalog snapshot; never reinterpret them as new proposals.

The profile is deliberately a **reservation/review ledger**, not a published-release schema: EXT-01B.3D source/build provenance and real publication authority are still absent. A candidate reservation is not an official installable release. Use a separately reviewed version/profile for production admission.

| Operation | Allowed prior state | Result |
|---|---|---|
| RESERVE_CANDIDATE | no record, expected_revision=0, exact reviewed candidate | RESERVED_CANDIDATE, revision 1 |
| WITHDRAW | RESERVED_CANDIDATE, exact current revision | WITHDRAWN |
| REVOKE | RESERVED_CANDIDATE or WITHDRAWN, exact current revision | REVOKED |

No return to RESERVED_CANDIDATE after withdrawal/revocation; no deletion, no reuse, even for identical bytes. A different request_id for a reserved key is rejected (look up the original); retry of the exact same successful request_id and exact bytes returns the immutable original receipt, even if current state is later revoked. That receipt is historical evidence only, not current eligibility. A reused request_id with different bytes conflicts across all releases in the same ledger. Rejected/uncommitted requests do not consume IDs. No clock-based expiry or eviction of the successful idempotency record. A stale expected_revision is refused. Revocation does not imply an immediate motor stop or existing host shutdown; those are independently governed.

## Records and authority

- ReleaseLedgerRequest binds exact proposal and evidence SHA-256, scope, request_id, expected release revision, operation and reason. It grants nothing.
- Reservation evidence reuses the exact existing RegistryReviewTarget with REVIEWED_CANDIDATE, checked against exact proposal key and namespace. A shaped record is not proof. The owner must independently authenticate current TUF review and local registry approval to record a candidate.
- ReleaseDispositionNotice binds withdrawal/revocation to exact key, proposal, operation, request, revision, scope and reason; it is an unverified claim until an independent owner-authorized control path authenticates it. Do not infer permission from text or TUF withdrawal failure. Revocation authority/keys/transport remain independent.
- ReleaseLedgerReceipt identifies one committed candidate event, its prior global receipt digest, exact request/evidence/authority context digest and resulting revision/state. It is unsigned local storage evidence, not a TUF target or install permission. The sequence is an integer order, not a timestamp. The raw digest of deterministic local receipt serialization is computed externally; no self-hash and no new signing canonicalization profile.
- ReleaseLedgerCheckpoint contains exact catalog/ledger identity, pinned legacy catalog digest and event sequence+receipt digest, including genesis. A previously retained trusted checkpoint can detect a restored prefix shorter than the checkpoint or a conflicting prefix; it is not an external attestation or protection against someone replacing both database and checkpoint. An append-only hash chain alone does not prove authenticity.

Commit exact request, proposal/evidence, independently supplied owner-verification context and receipt atomically, before reporting success. Use the existing bounded proposal parser, exact raw digests, local serialization, and shared transition rules; no duplicate registry schema. The owner must provide fresh verification for new transactions; retries return prior receipt without another write or renewed authority. No positive flag may be derived from JSON alone. Lost ACK -> same request lookup/retry, not a new key.

## Storage-neutral acceptance requirements

The registry's reference backend will use SQLite, explicit initialization and one catalog/ledger identity per private local database, serialized write transactions and immutable events. It must refuse missing/corrupt/unexpected state rather than silently bootstrap. Retain exact legacy catalog baseline, uniqueness and history. Checkpoint preservation/recovery, durable fsync/transaction behavior, independent writers, fault rollback and actual trust producer integration are tested within the local scope; no claim of replicated/distributed consensus, hostile admin protection, production key custody, authenticated clocks, crash-proof external checkpoint storage or atomic publication of TUF snapshots. Actual ledger admission and signed catalog publication will need a reviewed transactional/outbox/reconciliation protocol, including publication/revocation races and rollback. No change to legacy install policy, Core spec or current catalog.
