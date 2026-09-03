# OpenRGD Repository Map

Snapshot date: **2026-09-02**.

The GitHub organization exposed 66 accessible repositories during reconciliation. Only three contained data; 63 were empty placeholders. Repository names alone are therefore not evidence of an approved architecture.

## Active or evidence-bearing repositories

| Repository | Current role | Reconciliation classification |
|---|---|---|
| `OpenRGD/openrgd` | Standard, non-actuating CLI/reference tooling and candidate contracts | **CANONICAL ROOT** |
| `OpenRGD/actuators-registry` | Actuator schema and future canonical model registry | **SUPPORT REGISTRY — KEEP / RECONCILE** |
| `OpenRGD/demo-repository` | Private minimal web demo | **OUT OF SCOPE** |

`OpenRGD/openrgd` explicitly does not provide a physical embodied runtime. Its former bundled ROS 2 / Viam prototype is quarantined as historical evidence.

## Candidate autonomous components

These boundaries come from recovered implementation artifacts and the convergence candidate. They are not yet all represented by populated GitHub repositories.

| Component | Candidate repository | Current status |
|---|---|---|
| RGD-Physics | `rgd-physics` | independent implementation repo proposed; GitHub destination not yet populated |
| Robot Chronograf | `robot-chronograf` | independent temporal implementation repo proposed |
| Embodied Runtime | existing empty `rgd-runtime` or scoped `rgd-embodied-runtime` | **REQUIRED AS INDEPENDENT IMPLEMENTATION; final name open; canonical root status `NOT_PROVIDED_BY_CANONICAL_ROOT`** |
| LeRobot / SO-101 adapter | `rgd-lerobot` | Body Adapter repo proposed; must remain below the runtime/somatic/safety boundary |
| RGD-Ethics / Ethos | `rgd-ethics` | forensic/ethical implementation repo proposed |
| HyperKernel | historical archive name to be determined | legacy lineage, not a normative dependency |

### Embodied Runtime ownership

The independent runtime is expected to own executable orchestration for:

```text
CognitionProposal / ActionIntent
        ↓
Somatic Translator
        ↓
CapabilityPlan
        ↓
Operation Safety Gate
        ↓
DecisionTrace
        ↓
Body Adapter orchestration
        ↓
Chronon evidence and runtime lifecycle
```

This table does not claim that the empty `rgd-runtime` placeholder is the accepted destination, nor that the recovered `rgd-embodied-runtime` snapshot is already canonical. That choice belongs to the later repository reconciliation.

## Candidate material absorbed by the canonical root

| Artifact | Destination | Reason |
|---|---|---|
| OpenRGD Agent Contracts | `openrgd/contracts/` | cross-component interfaces must be discoverable beside the standard |
| Convergence Alpha | `docs/reconciliation/` plus extracted candidate contracts | transitional archaeology, not a permanent runtime product |
| Historical bundled runtime | `docs/history/runtime-prototype/` | preserve implementation evidence without shipping unsafe/incomplete execution code |
| Ecosystem aggregate bundles | provenance/archive only | aggregates must not become a competing authority |

## Empty placeholder repositories

The organization contains families such as `rgd-core`, `rgd-schema`, `rgd-synapse-*`, converters, SDKs, OS variants, fleet/network concepts and app/tool names. Until populated and explicitly adopted, they are classified:

```text
RESERVED / NON-AUTHORITATIVE
```

No code or specification should depend on a placeholder repository merely because its name exists.
