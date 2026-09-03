# 03 — Chronon ↔ AION Memory Contract v0.1

## Canonical source

Chronons are the canonical append-only evidence of the agent's life.
Memory types are projections over that history.

```text
Chronon history
   ├─ working
   ├─ episodic
   ├─ semantic
   ├─ procedural
   ├─ autobiographical
   ├─ relationship
   ├─ decision
   └─ lessons
```

Canonical evidence MUST NOT be silently rewritten because a later model changes
its interpretation. Corrections and consolidations point to the Chronons they
were derived from and MAY supersede prior projections.

Embeddings, summaries, indexes, confidence/relevance scores and caches are
derived state and MAY be rebuilt.

A consolidation operation SHOULD itself be recorded as a LEARNING or
MEMORY_CONSOLIDATION Chronon.

### Oneiric provenance

Synthetic/dreamed experiences MUST be distinguishable from physical history.
They may produce lessons or skill candidates, but MUST NOT be represented as
observed physical events without later physical validation.

### Forgetting

v0.1 defines forgetting as a projection/policy lifecycle operation, not
automatic destruction of historical Chronons. Legal erasure/anonymization is
an explicitly unresolved privacy profile.
