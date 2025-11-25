# OpenRGD Technical Structure

## Overview

OpenRGD (Robot Graph Definition) is not a monolithic file format, but a **hierarchical Semantic Graph**. This document defines the technical structure of the standard, organizing the complexity of robotic embodiment into six normative domains.

## Architecture Philosophy

The OpenRGD architecture is based on three fundamental principles:

1. **Separation of Concerns**: Each domain addresses a distinct aspect of robotic existence
2. **Hierarchical Composition**: Domains build upon each other in a logical dependency chain
3. **Semantic Coherence**: All domains contribute to a unified self-model that enables safe embodiment

## The Six Normative Domains

### 01_Foundation: Physical Reality Layer

**Purpose**: Defines the immutable physical reality of the machine.

**Scope**:
- Hardware abstraction
- Actuator dynamics and specifications
- Sensor fidelity and characteristics
- Physical dimensions and geometry
- Resource topology (power, thermal, computational)
- Kinematic and dynamic models

**Characteristics**:
- Ground truth of physical existence
- Changes only through physical modification
- Forms the basis for all higher-level reasoning

**File Structure**:
```
01_Foundation/
├── actuators/
│   ├── motors.json
│   ├── servos.json
│   └── pneumatics.json
├── sensors/
│   ├── proprioceptive.json
│   ├── exteroceptive.json
│   └── calibration.json
├── geometry/
│   ├── urdf/
│   ├── meshes/
│   └── kinematic_chains.json
├── resources/
│   ├── power_budget.json
│   ├── thermal_model.json
│   └── compute_topology.json
└── metadata.json
```

---

### 02_Safety: Autonomic Safety Layer

**Purpose**: Defines the operational envelopes and safety constraints that preserve machine and environment integrity.

**Scope**:
- Operational envelopes (velocity, acceleration, force limits)
- Reflex loops and emergency responses
- Hard constraints (joint limits, collision boundaries)
- Safety overrides and intervention protocols
- Fail-safe behaviors

**Characteristics**:
- Overrides cognitive intent when safety is compromised
- Immutable without explicit authorization
- Acts as the "immune system" of the robot

**File Structure**:
```
02_Safety/
├── envelopes/
│   ├── kinematic_limits.json
│   ├── dynamic_limits.json
│   └── workspace_boundaries.json
├── reflexes/
│   ├── collision_avoidance.json
│   ├── emergency_stop.json
│   └── recovery_behaviors.json
├── constraints/
│   ├── hard_limits.json
│   ├── soft_limits.json
│   └── zone_restrictions.json
└── metadata.json
```

---

### 03_Capability: Skill Interface Layer

**Purpose**: Maps the robot's potential interactions with the world through a capabilities API.

**Scope**:
- Skills library (primitives and compositions)
- Action templates and parameter spaces
- Capability prerequisites and dependencies
- API surface for cognitive model interaction
- Tool definitions and manipulation primitives

**Characteristics**:
- Defines "what the robot can do"
- Bridges intent and execution
- Modular and composable

**File Structure**:
```
03_Capability/
├── primitives/
│   ├── motion.json
│   ├── manipulation.json
│   ├── perception.json
│   └── communication.json
├── compositions/
│   ├── task_templates.json
│   └── skill_graphs.json
├── api/
│   ├── endpoints.json
│   ├── parameter_spaces.json
│   └── validation_schemas.json
└── metadata.json
```

---

### 04_Ethics: Value Alignment Layer

**Purpose**: Formalizes the system's value hierarchy and ethical constraints.

**Scope**:
- Value hierarchy and priority systems
- Ethical constraints and moral boundaries
- Decision-making governance
- Conflict resolution strategies
- Alignment specifications

**Characteristics**:
- Acts as the governance layer
- Resolves competing objectives
- Ensures alignment with intended purpose

**File Structure**:
```
04_Ethics/
├── values/
│   ├── hierarchy.json
│   ├── priorities.json
│   └── weights.json
├── constraints/
│   ├── moral_boundaries.json
│   ├── prohibited_actions.json
│   └── conditional_rules.json
├── governance/
│   ├── resolution_engine.json
│   └── audit_trail.json
└── metadata.json
```

---

### 05_History: Temporal State Layer

**Purpose**: Tracks the history and degradation of the system over time.

**Scope**:
- Component wear and fatigue models
- Usage history and maintenance logs
- Plasticity rates and adaptation metrics
- Maintenance schedules and predictions
- Performance degradation tracking

**Characteristics**:
- Introduces concept of "mortality"
- Enables predictive maintenance
- Records system evolution

**File Structure**:
```
05_History/
├── wear/
│   ├── component_fatigue.json
│   ├── usage_metrics.json
│   └── degradation_models.json
├── maintenance/
│   ├── schedules.json
│   ├── logs.json
│   └── predictions.json
├── evolution/
│   ├── adaptation_history.json
│   ├── learning_rates.json
│   └── performance_trends.json
└── metadata.json
```

---

### 06_Collective: Multi-Agent Layer

**Purpose**: Defines protocols for coordination and knowledge sharing between distinct entities.

**Scope**:
- Multi-agent coordination protocols
- Swarm consensus mechanisms
- Reputation management systems
- Knowledge sharing interfaces
- Communication standards

**Characteristics**:
- Enables collective intelligence
- Manages inter-robot relationships
- Facilitates distributed decision-making

**File Structure**:
```
06_Collective/
├── coordination/
│   ├── protocols.json
│   ├── consensus_mechanisms.json
│   └── task_allocation.json
├── communication/
│   ├── message_formats.json
│   ├── discovery.json
│   └── synchronization.json
├── reputation/
│   ├── trust_models.json
│   └── peer_evaluation.json
└── metadata.json
```

---

## Integration: The Semantic Kernel

The **Semantic Kernel** is the orchestration layer that dynamically loads and links all six domains. It ensures the cognitive agent possesses a complete, consistent, and context-aware picture of its embodiment before any action is planned or executed.

### Kernel Responsibilities

1. **Domain Loading**: Validates and loads all six domains in dependency order
2. **Graph Construction**: Builds the unified semantic graph from domain data
3. **Consistency Checking**: Ensures no conflicts between domain specifications
4. **Context Resolution**: Provides relevant context to cognitive models
5. **Safety Enforcement**: Ensures Safety Layer has ultimate override authority

### Kernel Structure

```
kernel/
├── loader/
│   ├── domain_loader.py
│   ├── validators.py
│   └── dependency_resolver.py
├── graph/
│   ├── semantic_graph.py
│   ├── query_engine.py
│   └── context_manager.py
├── enforcement/
│   ├── safety_monitor.py
│   └── constraint_checker.py
└── interfaces/
    ├── cognitive_api.py
    └── hardware_abstraction.py
```

---

## Implementation Guidelines

### Domain Dependencies

```
01_Foundation (base layer, no dependencies)
    ↓
02_Safety (depends on Foundation)
    ↓
03_Capability (depends on Foundation + Safety)
    ↓
04_Ethics (depends on Capability)
    ↓
05_History (depends on all above)
    ↓
06_Collective (depends on all above)
```

### Loading Order

Domains must be loaded in dependency order. The Kernel validates each domain before proceeding to the next.

### Validation Requirements

Each domain must include:
- `metadata.json` with version, author, timestamp
- JSON schema validation files
- Self-consistency checks
- Dependency declarations

### Extension Mechanism

Domains support extension through:
- Custom fields in `extensions/` subdirectories
- Versioned schema evolution
- Plugin architecture for domain-specific logic

---

## File Format Specifications

### Primary Format: JSON
- Human-readable and machine-parseable
- Schema validation via JSON Schema
- Support for comments via pre-processors

### Geometry Format: URDF + Extensions
- Standard URDF for kinematic chains
- Extended with OpenRGD-specific annotations
- Binary mesh formats (STL, OBJ) for visualization

### Temporal Data: JSON Lines
- Streaming format for history logs
- One JSON object per line
- Efficient for large temporal datasets

---

## Versioning Strategy

OpenRGD follows semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to domain structure
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes and documentation updates

Current version: **v0.1.0** (Draft Proposal)

---

## Future Extensions (v1.0+)

### AI-Assisted Stewardship
- Commitment Proposals (CPs) for machine-readable diffs
- Automated validation pipeline
- Human-in-the-loop approval process
- Cryptographic audit trails

### Advanced Features
- Real-time domain updates
- Distributed domain hosting
- Encrypted safety domains
- Blockchain-based provenance

---

## Contributing

To propose changes to this structure, please:

1. Read `CONTRIBUTING.md`
2. Submit an RFC (Request for Comments)
3. Engage with the community for feedback
4. Submit a pull request with proposed changes

---

## License

Copyright © 2025 OpenRGD Organization  
Distributed under the MIT License

---

## Contact

- **Lead Architect**: Pasquale Ranieri (Italia Robotica)
- **Repository**: https://github.com/OpenRGD/openrgd
- **Documentation**: https://openrgd.org (planned)

---

*This structure represents the v0.1 draft proposal and is subject to evolution through the RFC process.*