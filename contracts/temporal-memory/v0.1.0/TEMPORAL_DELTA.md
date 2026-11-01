# D-TIME-01 — Versioned legacy-import correction (proposal)

The current `contracts/agent/v0.1.0/contracts/00_TEMPORAL_CHRONON_PROFILE.md` §11 says to create a TimeAtom using historical `memory.sqlite3.created_at`, label it legacy/unattested and issue AnchorRef64. This risks suggesting Chronograf measured a past event. Core-D **does not change that existing candidate document**.

Proposed flow:

```text
original source bytes + digest (unchanged)
  → HistoricalTimeAssertion with legacy.posix.system and UNKNOWN/UNATTESTED quality
  → real Chronograf measurement of current import operation
  → ImportAnchorEvidence linking source claim to new measured anchor
  → authorized HistoryCommitRequest, stable idempotency key, exact payload commitment
  → external writer verifies Life/role/effect/clock and commits one historical-import record
  → authenticated writer receipt; derived source_event → chronon lookup
```

Separate event/valid time, import/commit time, and knowledge/reinterpretation time. The original event is not witnessed anew; do not backdate a TimeAtom or mint a fake anchor. An AnchorRef64 has namespace, opaque uint64 handle and TimeAtom SHA-256; a handle is not a timestamp or global clock. If writer or Chronograf is unavailable, keep source evidence and report uncertainty, not a fake Chronon. Lost ACK must be resolved using the same idempotency key.

Review/semver delta needs actual Chronograf and RGD-Physics/History owners, historical migration fixtures, privacy policy and explicit acceptance.
