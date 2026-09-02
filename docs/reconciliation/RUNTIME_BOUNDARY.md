# OpenRGD Runtime Boundary

**Decision status:** ADOPTED ON RECONCILIATION BRANCH  
**Effective scope:** `OpenRGD/openrgd` packaging and CLI  
**Date:** 2026-09-02

## Decision

`OpenRGD/openrgd` is the normative standard and reference-tooling root. It does **not** ship a physical embodied runtime or hardware adapter implementation as part of the canonical `rgd` toolchain.

The historical bundled ROS 2 / Viam runtime prototype is quarantined under `docs/history/runtime-prototype/`. The `rgd run` namespace is retained only as a non-actuating compatibility/status boundary while the independent embodied-runtime repository is reconciled.

This decision does not delete the historical implementation and does not claim that an external runtime repository is already canonical or released.

## Evidence

The quarantined prototype could not satisfy either its own implied execution contract or the later convergence candidate:

| Area | Recovered implementation | Finding |
|---|---|---|
| Safety source | `RGDEngine` loaded `02_operation/safety_supervisor.jsonc` | File absent from the specification |
| Safety semantics | `validate_command()` compared one scalar against `max_impact_energy_j_float` | Not equivalent to the typed `runtime_validation.jsonc` and `safety_critical.jsonc` contracts |
| Perception API | ROS 2 callback called `engine.ingest_sense()` | Method absent; engine exposed `process_perception()` |
| ROS 2 actuation | `_configure_actuation()` | `pass` |
| Viam cognition/actuation | THINK and ACT phases | placeholders |
| Viam output | `publish_intent()` | `pass` |
| Execution boundary | adapter `publish_intent(intent)` | bypassed the convergent ActionIntent, somatic, safety and DecisionTrace layers |
| Packaging claim | `rgd run ros2`, `viam`, `hybrid` were exposed as runtime engines | Surface implied executable behavior that could not be demonstrated safely |

No evidence showed that `safety_critical.jsonc` or `runtime_validation.jsonc` could simply be renamed to satisfy the missing prototype dependency. They have distinct structures and responsibilities.

## Canonical separation

```text
OpenRGD/openrgd
├── normative specification
├── cross-component contracts
├── validators and compilers
├── import/export tooling
└── non-actuating runtime compatibility status

Independent embodied runtime
├── CognitionProposal / ActionIntent ingestion
├── Somatic Translator
├── CapabilityPlan execution
├── Operation Safety Gate
├── DecisionTrace
├── Body Adapter orchestration
├── Chronon evidence
└── runtime lifecycle

Body-adapter repositories
└── hardware-specific protocols, units, buses and device behavior
```

The target embodied-runtime repository name remains governed by `REPOSITORY_MAP.md`; the presence of an empty GitHub placeholder is not authority.

## CLI compatibility behavior

The canonical toolchain retains:

```text
rgd run status
rgd run ros2
rgd run viam
rgd run hybrid
```

`status` reports the externalized boundary and exits successfully.

The historical adapter names return a deterministic non-zero result and **never** import middleware libraries, open serial/CAN/network connections, instantiate hardware clients or issue actuator commands.

This makes the old surface fail closed while giving existing users a migration explanation instead of silently reporting an unknown command.

## Conformance rule

A future embodied runtime must consume versioned contracts and demonstrate at least:

```text
CognitionProposal
      ↓
ActionIntent
      ↓
Somatic Translator
      ↓
CapabilityPlan
      ↓
Operation Safety Gate
      ↓
DecisionTrace
      ↓
Body Adapter
      ↓
Hardware
```

It must not be copied into this repository merely to repair the old prototype. Its own implementation, tests, version and release lifecycle belong to the independently reconciled runtime repository.
