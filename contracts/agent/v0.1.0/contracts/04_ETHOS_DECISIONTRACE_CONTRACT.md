# 04 — Ethos ↔ Chronon / DecisionTrace Contract v0.1

Ethos Packet remains a separate forensic/ethical object with explicit temporal
and causal bindings. This contract does NOT assert that an Ethos Packet is a
Chronon or an Aion payload.

```text
subject Chronons
      ↓
constitutional/policy evaluation
      ↓
DecisionTrace
      ↓
optional Ethos Packet
      ↓
EthosBinding(subject Chronons, trace, packet commitments)
```

DecisionTrace results are `ALLOW`, `BLOCK`, `OVERRIDE`, or `ESCALATE` and carry
policy snapshot refs, rules/hard-invariant refs, evidence Chronons and a
content commitment.

A hardware signature can establish provenance/authenticity of an artifact. It
MUST NOT be interpreted as proof of moral correctness.

Thermodynamic/Ethos impact fields may be evidence used by policy, but no scalar
energy quantity is declared to be universal moral value by this contract.
