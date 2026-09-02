# 02 — Somatic Translation Contract v0.1

The Somatic Translator is the hardware-agnostic boundary between approved
intent and embodied execution.

```text
Approved ActionIntent / ActionGraph
        + Self Model
        + Capability Registry
                 ↓
          Somatic Translator
                 ↓
           CapabilityPlan
                 ↓
       Operation Safety Gate
                 ↓
             Body Adapter
```

It MUST NOT emit motor IDs, raw Feetech ticks, CAN frames or simulator-specific
commands. Those belong below the body-adapter boundary.

A CapabilityPlan contains one or more typed capability steps with parameters,
expected effects, risk/reversibility metadata and observation requirements.

In v0.1 the reference translator implements the simplest valid case: one
ActionIntent becomes one declared capability step. This is intentionally a
contract baseline, not the final motion planner.
