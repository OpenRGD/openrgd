# 01 — Cognition Contract v0.1

A cognition provider MAY be an LLM, VLM, VLA, world model, deterministic
planner, or future model. It MUST NOT receive authority to directly actuate a
body merely because it generated a high-scoring vector.

## Output

```text
CognitionProposal
├── proposal_id
├── cognition_provider_id / model_id
├── ActionIntent
├── AION octant (optional but structured)
├── HyperAionRef512 (optional)
├── parent Chronon refs
└── recalled-memory Chronon refs
```

`ActionIntent` is executable semantics. `HyperAionRef` is cognitive state.
They are complementary, not aliases.

### HyperAion v0.1 map

- dimensions 0..7: valence, legality, altruism, urgency, confidence,
  reversibility, authority, complexity;
- dimensions 8..31: reserved protocol space;
- dimensions 32..511: semantic/extension space, intentionally not frozen here.

A vector reference commits via SHA-256 to a producer-declared 512 × Float32
representation and MUST carry its encoding profile. v0.1 intentionally does
not freeze final byte endianness because the recovered HyperKernel transmuter
lineage was not portable on this point.

## Resolver hierarchy

Hard constitutional blocks are authoritative. A soft resolver such as
`sigmoid(dot(intent, context))` MAY rank/select among allowed actions but MUST
NOT override a hard block.

No chain-of-thought is required or persisted. Audit stores structured intent,
inputs/evidence refs, model identity, confidence and policy outcomes.
