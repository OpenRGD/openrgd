# OpenRGD Agent Contracts v0.1.0

Status: **CANDIDATE**

This package explores shared interfaces between cognition, embodiment, time/memory and ethical decision evidence:

1. Cognition Contract — `ActionIntent` with optional representation references.
2. Somatic Translation Contract — approved intent → hardware-agnostic `CapabilityPlan`.
3. Chronon ↔ AION Memory Contract — Chronons are canonical evidence; memories are projections.
4. Ethos ↔ Chronon / DecisionTrace Contract — structured ethical/decision evidence linked by commitments.

The intended priority is:

```text
hard constitution / explicit policy block
             >
soft semantic representation / ranking
             >
operational choice among allowed actions
```

The contracts deliberately separate representation from permission to act. They remain candidate interfaces until implementations and conformance tests make the boundary mature enough to accept.
