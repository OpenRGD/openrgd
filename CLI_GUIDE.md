# OpenRGD CLI guide

The `rgd` CLI manages OpenRGD specification profiles and derived static artifacts. The canonical package is non-actuating.

## Install

```bash
python -m pip install -e .
rgd --help
```

Use the global `--quiet` flag for deterministic machine-readable output and stderr-only errors.

## Core profile lifecycle

### `rgd init NAME`

Creates a project from the packaged default profile, personalizes its DID and recalculates `OPENRGD_SOURCE_TREE_SHA256_V1`.

```bash
rgd init my_robot
```

### `rgd hash`

```bash
rgd hash
rgd hash --output json
rgd hash --write
```

Without `--write`, a mismatch exits non-zero. `--write` is for an intentional source change.

### `rgd check`

```bash
rgd check
rgd check --output json
rgd check spec/00_core/kernel.jsonc --output json
```

`check` is an integrity-aware static profile validator. It requires:

- the canonical kernel path `spec/00_core/kernel.jsonc`;
- a matching `OPENRGD_SOURCE_TREE_SHA256_V1` root;
- a non-empty kernel identity;
- safe, unique, relative JSONC module references;
- every selected module to exist;
- every selected module to parse as a JSON object without non-finite values.

It returns a structured `OPENRGD_PROFILE_VALIDATION` artifact in JSON mode.

It does **not** assess:

- hardware compatibility;
- operational safety;
- embodied-runtime readiness;
- permission to actuate.

### `rgd boot`

```bash
rgd boot
rgd boot --output json
rgd boot spec/00_core/kernel.jsonc --output json
```

`boot` reuses the same integrity and module-loading checks, then builds a deterministic:

```text
OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT
```

The JSON context contains the selected modules, source-root commitment, physical/joint summary and alignment summary. It always records:

```text
physical_execution.assessed = false
physical_execution.authorized = false
physical_execution.status = NOT_AUTHORIZED_BY_BOOT
```

`boot` is not a hardware bootloader, runtime startup command, safety authorization or claim that the robot is ready.

## Import and enrichment

### `rgd import`

Imports only facts supported by a source description:

```bash
rgd import robot.urdf --out partial-robot
rgd import robot.usda --out partial-robot
```

Both current importers emit partial Foundation evidence only:

```text
spec/01_foundation/description.jsonc
spec/01_foundation/actuation_dynamics.jsonc
```

They do not create kernel identity, safety, alignment, cognition, HAL or hardware authorization.

#### URDF

The reconciled URDF path preserves supported:

- link inertials;
- joint topology and type;
- revolute/prismatic limits with type-correct units;
- source dynamics;
- mimic relationships.

Absent values remain absent. Malformed and non-finite physical values fail closed.

#### Text USDA

The USDA path is deliberately narrow. It accepts UTF-8 text beginning with `#usda` and currently extracts supported `PhysicsRevoluteJoint` and `PhysicsPrismaticJoint` declarations.

It records source and stage provenance, including authored `metersPerUnit`, `kilogramsPerUnit`, `upAxis` and `defaultPrim` when present.

Conversion rules:

```text
revolute position     authored degrees → radians
prismatic position    stage distance × metersPerUnit → metres
drive maxForce        converted to N/Nm only when both
                      metersPerUnit and kilogramsPerUnit are authored
```

Raw source values remain available in `source_usd_joint_map`. Missing values are never replaced with convenience defaults. Ambiguous duplicate attributes, malformed values and non-finite values fail closed.

The lightweight parser does not perform USD layer composition, reference/payload resolution, variant evaluation, transform-stack evaluation or full schema fallback processing. Use a full OpenUSD-based adapter when those capabilities are required.

### `rgd alive`

Explicitly enriches imported evidence with a selected packaged seed:

```bash
rgd alive robot.urdf --out RGD-robot --seed default
rgd alive robot.usda --out RGD-robot --seed default
```

It personalizes kernel/bundle identity and recalculates the source root. The project manifest retains:

```text
seed_compatibility_status = UNVERIFIED
```

Review inherited physical, HAL, safety and behavioral modules before hardware use.

## Derived artifacts

### `rgd build-standard`

Builds a deterministic strict-JSON leaf mirror:

```bash
rgd build-standard
rgd build-standard --src ./Robot --dest ./Robot/standard
```

Destructive source/ancestor/descendant destinations are rejected.

### `rgd compile-spec`

Creates one deterministic machine bundle:

```bash
rgd compile-spec
rgd compile-spec --out ./artifacts/robot.json
rgd compile-spec --output json
```

Default output:

```text
spec/openrgd_unified_spec.json
```

The output contains the source root and source index, has no wall-clock timestamp and is ignored by Git.

## Static interoperability

### `rgd export ros2`

```bash
rgd export ros2 --out export/ros2
rgd export ros2 --out export/ros2 --output json
```

Prerequisites:

```bash
rgd hash
rgd compile-spec
```

The exporter verifies both the source tree and the compiled bundle. It generates deterministic non-actuating files and reports either `CONFIGURATION_ONLY` or `HARDWARE_BOUND`.

Hardware Xacro is omitted unless all exported joints have complete explicit HAL interfaces and one system driver plugin.

### Unavailable target

`rgd export isaac` fails explicitly with exit code `2`: the historical Isaac generator was a placeholder and is not an active implementation.

## Runtime compatibility boundary

```bash
rgd run status
rgd run status --output json
```

Historical physical adapter commands fail closed:

```bash
rgd run ros2
rgd run viam
rgd run hybrid
```

They return exit code `2`; the embodied runtime belongs in an independent implementation repository.

## Verified non-actuating lifecycles

CI exercises project-owned URDF and USDA fixtures through:

```text
import
→ alive
→ hash
→ check
→ boot
→ compile-spec
→ export ros2
```

This verifies evidence extraction, provenance, integrity, module loading and deterministic static output. It does not prove seed/body compatibility or physical safety.
