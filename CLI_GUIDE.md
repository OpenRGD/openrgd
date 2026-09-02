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

Checks kernel module references and JSONC loading:

```bash
rgd check
rgd check spec/00_core/kernel.jsonc
```

This is a structural check, not hardware certification. Source-tree integrity remains a separate explicit `rgd hash` check.

### `rgd boot`

Loads modules selected by the kernel and emits the current prompt/grounding representation:

```bash
rgd boot
rgd boot --output json
```

It does not actuate hardware.

## Import and enrichment

### `rgd import`

Imports only facts supported by the source description:

```bash
rgd import robot.urdf --out partial-robot
rgd import robot.usda --out partial-robot
```

Current importers emit partial Foundation evidence. They do not create kernel identity, safety, alignment or cognition.

The reconciled URDF path preserves supported link inertials, joint topology, type-correct limits, source dynamics and mimic relations. Absent URDF values remain absent; malformed or non-finite physical values fail.

### `rgd alive`

Explicitly enriches imported evidence with a selected packaged seed:

```bash
rgd alive robot.urdf --out RGD-robot --seed default
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

## Verified non-actuating lifecycle

CI exercises the owned URDF fixture through:

```text
import → alive → hash → check → boot → compile-spec → export ros2
```

This verifies mechanics, provenance and determinism. It does not prove seed/body compatibility or physical safety.
