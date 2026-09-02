# Historical OpenRGD runtime prototype

**Classification:** SUPERSEDED / QUARANTINED IMPLEMENTATION EVIDENCE  
**Source baseline:** `OpenRGD/openrgd` at and before commit `4776e637b4d575d14d55f06423c87cfe1ec0de87`  
**Quarantine decision:** reconciliation branch, 2026-09-02

This directory preserves the source files of the first bundled ROS 2 / Viam runtime experiment exactly as they existed before quarantine. The files are historical evidence, not executable package code and not a conformant implementation of the later embodied contracts.

The related in-memory `core/templates.py` generator is preserved here as well because it independently generated the same missing `02_operation/safety_supervisor.jsonc` path. The active CLI had already superseded that generator with the packaged default seed.

## Why it was quarantined

Direct inspection found that the prototype:

1. loaded `02_operation/safety_supervisor.jsonc`, a file absent from the specification;
2. reduced command validation to a generic scalar comparison unrelated to the typed safety artifacts already present;
3. exposed `publish_intent()` as a direct adapter operation without the convergent `ActionIntent → Somatic Translator → CapabilityPlan → Operation Safety Gate → DecisionTrace → Body Adapter` boundary;
4. called an undefined `engine.ingest_sense()` method from the ROS 2 adapter;
5. left ROS 2 actuation unimplemented;
6. left Viam think/act dispatch and `publish_intent()` unimplemented;
7. described hardware execution through a CLI surface even though the implementation could not prove safe or complete execution;
8. coexisted with an unused alternative template generator that could recreate the missing safety-module dependency.

No existing safety file was renamed or treated as an equivalent replacement without evidence.

## Preserved Git blob identities

| Historical path | Preserved path | Original Git blob |
|---|---|---|
| `src/openrgd/commands/run.py` | `commands/run.py` | `2dc8fc2f846f2903d8e69e77c709a49f0d841f87` |
| `src/openrgd/runtime/__init__.py` | `runtime/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `src/openrgd/runtime/core/__init__py` | `runtime/core/__init__py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `src/openrgd/runtime/core/engine.py` | `runtime/core/engine.py` | `29884908c47639f10999181683bb3da213d9af66` |
| `src/openrgd/runtime/adapters/__init__.py` | `runtime/adapters/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `src/openrgd/runtime/adapters/base.py` | `runtime/adapters/base.py` | `78082934ac714341462b5398bf09d1d92f0a5054` |
| `src/openrgd/runtime/adapters/ros2/node.py` | `runtime/adapters/ros2/node.py` | `a790d786c4bc2ca170dac7a294896195e4e6fcdb` |
| `src/openrgd/runtime/adapters/viam/__init__.py` | `runtime/adapters/viam/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `src/openrgd/runtime/adapters/viam/node.py` | `runtime/adapters/viam/node.py` | `fddc0f0a42aff487fef85faca9cc9ed4ad07752a` |
| `src/openrgd/core/templates.py` | `related/core/templates.py` | `24339ee9531397b61decafbbc441a4c5eb1a2030` |

The repository validator recomputes Git blob identities for these files. Any modification destroys the evidence match and fails CI.
