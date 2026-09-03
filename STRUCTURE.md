# OpenRGD canonical repository structure

## Status

This document defines the authority model adopted by the historical reconciliation branch. It becomes repository policy only after review and merge.

## Authority order

1. `spec/manifest.jsonc` declares the standard version, integrity profile and domain maturity.
2. Modular files under `spec/` are the human-readable normative source.
3. Accepted contracts under `contracts/` define cross-component interfaces within their declared scope.
4. Candidate contracts are reviewable formalizations, not stable normative law.
5. `standard/` is a tracked strict-JSON leaf mirror and cannot become an independent source of truth.
6. `src/openrgd/seeds/default/spec/` is a derived default runtime profile.
7. Machine bundles, exports and robot workspaces are generated products and remain untracked.
8. Historical evidence under `docs/history/` is non-normative.

Duplicate copies must not be resolved silently. Source/derived relationships are enforced through `ARTIFACT_POLICY.json`, canonical hashing and CI.

## Canonical domains

### `00_core` — coordination

Bundle metadata, kernel identity, validation references and cross-domain orchestration.

### `01_foundation` — physical reality

Body description, actuators, sensors, calibration, power, compute, firmware/HAL mappings, materials and physical constraints.

### `02_operation` — operation and safety

Operational envelopes, runtime validation, safety-critical behavior, compliance and autonomic protection.

### `03_agency` — capability and interaction

World model, declared skills, capability interfaces and action semantics.

### `04_volition` — values and governance

Alignment, hard invariants, value priorities, decision governance and conflict resolution. Soft scores cannot override hard constitutional blocks.

### `05_evolution` — lifecycle and adaptation

Wear, plasticity, continuity, replication and termination semantics.

### `06_ether` — collective existence

Inter-agent coordination, shared computation, consensus, reputation and civilizational protocols.

The older Foundation/Safety/Capability/Ethics/History/Collective taxonomy is historical only.

## Canonical source integrity

The standard/profile source tree uses:

```text
OPENRGD_SOURCE_TREE_SHA256_V1
```

The profile commits selected modular source paths and exact source bytes. The manifest's own hash value is normalized to `sha256:SELF` while calculating the root. Details are in `docs/reconciliation/CANONICAL_HASHING.md`.

## Generated artifact boundary

```text
spec/ modular source
        │
        ├── standard/ strict leaf mirror
        └── deterministic machine bundle generated on demand
```

Tracked domain bundles, human unified copies, benchmark snapshots, generated workspaces and export outputs are prohibited. Their historical identities are recorded in `docs/history/generated-artifacts/`.

## Cognitive-to-physical boundary

The convergence-candidate interface is:

```text
LLM / VLM / VLA / planner / world model
                  ↓
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

- HyperAion is a representation, not actuation permission.
- `ActionIntent` is model-agnostic.
- `CapabilityPlan` remains hardware-agnostic.
- the Body Adapter owns servo IDs, buses, middleware messages and device commands;
- DecisionTrace stores structured evidence, not private reasoning.

These interfaces remain convergence candidates under `contracts/agent/v0.1.0/`.

## Temporal and memory ownership

- Robot Chronograf owns time measurement, clock domains, uncertainty and anchor resolution.
- RGD-Physics owns Chronon/Aion and causal-envelope semantics.
- the embodied runtime owns execution, recall and learning mediation.
- Chronons are canonical history; memories are projections.

## Implementation boundary in this repository

The Python package contains:

- CLI routing;
- JSONC loading and canonical hashing;
- deterministic strict-mirror and machine-bundle generation;
- URDF/USD importer scaffolding;
- static ROS 2 and Isaac-oriented Synapse generators;
- plugin discovery and policy scaffolding;
- a fail-closed `rgd run` compatibility/status namespace.

It does not contain an active physical runtime.

## External implementation candidates

Independent repositories are expected for:

- RGD-Physics;
- Robot Chronograf;
- embodied runtime;
- LeRobot/body adapters;
- RGD-Ethics.

Repository names and promotion state remain explicit decisions rather than implications from empty placeholders.
