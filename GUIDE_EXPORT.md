# OpenRGD static export guide

`rgd export` is experimental static Synapse tooling. It generates interoperability configuration; it is not an embodied runtime or a direct cognition-to-hardware path.

## Prepare a machine bundle

```bash
rgd hash
rgd compile-spec
```

The default machine bundle is generated at:

```text
spec/openrgd_unified_spec.json
```

It is deterministic and untracked.

## Generate output

```bash
rgd export ros2 --out ./export
rgd export isaac --out ./export
```

Historically produced ROS 2 files included:

- `ros2_control.yaml`;
- `rgd_limits.xacro`;
- `rgd_hardware.xacro`.

The Isaac generator produced a Python configuration artifact.

Generated export directories are ignored by Git. A generated file becomes a maintained fixture only when it has explicit provenance and an automated assertion.

## Boundary

```text
OpenRGD specification
        ↓
static Synapse generator
        ↓
configuration artifact
```

This must not be confused with:

```text
ActionIntent
→ Somatic Translator
→ CapabilityPlan
→ Operation Safety Gate
→ Body Adapter
→ hardware
```

The latter belongs to the independent embodied runtime and body-adapter repositories.

## Current maturity

The exporter lineage remains experimental and still requires dedicated fixture and lifecycle tests. No checked-in `export/` directory is presented as canonical output.
