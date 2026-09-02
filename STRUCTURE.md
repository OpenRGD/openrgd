# OpenRGD Canonical Repository Structure

## Status

This document defines the repository authority model adopted by the historical reconciliation branch. It becomes the repository-level authority policy only when that branch is reviewed and merged.

## Authority order

Within this repository, authority is resolved in this order:

1. `spec/manifest.jsonc` declares the standard-bundle version and domain maturity.
2. Modular files under `spec/` are the human-readable source of the reference specification.
3. Accepted contracts under `contracts/` define cross-component interfaces within their declared scope.
4. Candidate contracts are reviewable formalizations, not stable normative law.
5. `standard/` is a generated strict-JSON mirror and MUST NOT become an independent source of truth.
6. `src/openrgd/seeds/default/spec/` is a distributable scaffold and MUST be synchronized from reviewed specification sources.
7. Generated bundles, examples, exports and historical snapshots are non-authoritative unless a normative file explicitly references them.

Where duplicate copies disagree, the disagreement MUST be surfaced and reconciled; tooling MUST NOT select a winner silently.

## Canonical domains

### `00_core` — Coordination

Owns bundle coordination, kernel metadata, loading order, validation references and cross-domain orchestration. It is not a substitute for the six semantic domains.

### `01_foundation` — Physical reality

Owns body description, actuators, sensors, calibration, power, compute, firmware/HAL mappings, materials and physical constraints.

### `02_operation` — Runtime operation and safety

Owns operational envelopes, runtime validation, safety-critical behavior, compliance and autonomic protection.

### `03_agency` — Capabilities and interaction

Owns the world model, declared skills, capability interfaces and the semantics through which cognition requests action.

### `04_volition` — Values and governance

Owns alignment, hard invariants, value priorities, decision governance and conflict resolution. Soft cognitive scores cannot override hard constitutional blocks.

### `05_evolution` — Lifecycle and change

Owns wear, adaptation, plasticity, continuity, replication and termination semantics.

### `06_ether` — Collective existence

Owns inter-agent coordination, shared computation, consensus, reputation and civilizational protocols.

The older `Foundation / Safety / Capability / Ethics / History / Collective` taxonomy is preserved only as a historical artifact and is not the canonical directory model.

## Cognitive-to-physical boundary

The current convergence-candidate interface is:

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

Key separation:

- HyperAion is a cognitive representation, not an actuation permission;
- `ActionIntent` expresses model-agnostic action semantics;
- `CapabilityPlan` remains hardware-agnostic;
- the Body Adapter owns servo IDs, ticks, buses, ROS messages and device-specific commands;
- DecisionTrace records structured evidence and outcomes, not private reasoning.

These interfaces are currently candidate material under `contracts/agent/v0.1.0/`.

## Temporal and memory boundary

The convergence candidate separates ownership as follows:

- Robot Chronograf measures time, clock domains, uncertainty and anchor resolution;
- RGD-Physics defines Chronon and Aion semantics;
- an embodied runtime executes cognition and builds projections;
- Chronons are canonical append-only history;
- episodes, facts, skills, summaries and embeddings are rebuildable projections.

## Implementation boundaries in this repository

The Python package currently contains:

- CLI command routing;
- JSONC loading and specification compilation;
- URDF and USD importers;
- ROS 2 and Isaac-oriented Synapse generators;
- prototype ROS 2 and Viam runtime adapters;
- an experimental pure-logic runtime engine;
- plugin-discovery and policy scaffolding.

These modules prove implementation activity but do not establish a complete production embodied runtime.

## Retained legacy areas

The following areas are deliberately retained pending a later evidence-based cleanup:

- `RGD-ur5/` and `my-robots/RGD-ur5/`;
- tracked example exports under `export/`;
- duplicate generated unified specifications;
- `src/cli.py` beside the packaged entry point;
- the bundled `plugins/rgd_timetravel/` prototype.

Their presence does not make them canonical.
