# CORE-D → COG / Chronograf / RGD-Physics / Memory

**Candidate 2026-11-01.** Core main `afe1a831...`; Core-B #11 `55a034c...`; Core-C #13 `fa5e8ff...`; COG #6 `877a450...`. Existing implementation and null Life/Chronon of COG #6 remain unchanged.

**COG/Work/Imagination:** keep exactly one Core-B admission, bounded task reservations, lifecycle/outcome semantics. Oneiric review may occur internally and return REFUTED/UNRESOLVED; its synthetic scenario is not a physical step. Persistence requires separately approved History effect and active Life/writer verification; no self-granted authority.

**Chronograf:** provide real measured import/commit anchors and uncertainty with namespace, handle, full TimeAtom proof; never attest an old timestamp retroactively. Global/multi-robot alignment is separate.

**RGD-Physics/History:** own one canonical ledger, exclusive receiver-side writer fencing, qualified time, content commitment, durable idempotency and loss-of-ACK receipt lookup. Do not reuse FakeWriter as real service.

**Memory/Vault:** L1 evidence/retention, L2 canonical Chronon, L3/L4 derived bitemporal views and checkpoint validation; privacy redaction propagates to caches/replicas/backups. Old interpretations remain historically distinguishable.

**Core-C/Identity/RGD-EXT:** actual enrollment, binding, custody, revocation and lease authority required before real Life-bound writes. A schema reference, forge digest or role name cannot invent them.

**Review gates:** Chronograf anchor verifier, writer receipts, privacy erasure, evidence availability, cross-repo producer/consumer integration, ML-001 sampling coverage and recovery across restart/partitions. No canonical source or runtime changes in this PR.
