# OpenRGD Static Export Guide

`rgd export` generates **static interoperability configuration files** from a verified OpenRGD machine bundle. It does not start middleware, connect to hardware or actuate a robot.

## Active targets

| Target | Status | Output |
|---|---|---|
| `ros2` | Implemented and lifecycle-tested | controller configuration, limits, export manifest; hardware Xacro only with complete explicit HAL evidence |
| `isaac` | Not implemented | command fails explicitly with exit code `2` |

The historical Isaac generator was a placeholder and is not advertised as an active target.

## Required sequence

From an OpenRGD project root:

```bash
rgd hash
rgd compile-spec
rgd export ros2 --out export/ros2
```

Export fails if:

- the canonical source-tree root does not match the manifest;
- the deterministic machine bundle is missing;
- the machine bundle was generated from a different source root;
- required modules are missing or duplicated;
- the destination would overwrite the canonical `spec/` tree.

## Generated ROS 2 artifacts

Every successful ROS 2 export produces:

```text
ros2_control.yaml
rgd_limits.xacro
export_manifest.json
```

`rgd_hardware.xacro` is generated only when every exported joint has explicit HAL interfaces and the complete joint set resolves to exactly one system driver plugin.

The export manifest declares one of:

```text
CONFIGURATION_ONLY
HARDWARE_BOUND
```

`CONFIGURATION_ONLY` means that physical limits and controller structure were exported, but hardware bindings are incomplete or intentionally withheld. It is a successful static export, not permission to execute.

## Imported-body isolation

A body created from imported partial evidence cannot inherit actuator mappings, driver plugins, bus IDs or interfaces from the selected seed merely because a joint name happens to match.

For imported bodies:

```text
source-derived joint topology and limits
              ↓
static configuration export

seed actuator/HAL bindings
              ✕ not inherited by name collision
```

Hardware bindings must be reviewed and added explicitly.

## Determinism and provenance

The ROS 2 output is path-independent and deterministic for the same machine bundle. `export_manifest.json` records:

- canonical source-tree root;
- machine-bundle SHA-256;
- robot identity;
- exported joint set;
- units and limits;
- hardware-binding completeness;
- missing bindings and reason;
- generated filenames.

## Non-actuating boundary

The generated files are build artifacts. They may be consumed by a separately reviewed ROS 2 package or embodied runtime, but this repository does not launch `ros2_control`, publish commands or open device buses.

A complete execution path still belongs below the canonical contracts:

```text
ActionIntent
→ Somatic Translator
→ CapabilityPlan
→ Operation Safety Gate
→ DecisionTrace
→ Body Adapter
→ hardware
```
