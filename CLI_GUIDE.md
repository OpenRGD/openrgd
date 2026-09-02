# OpenRGD CLI Guide

The `rgd` command in this repository manages OpenRGD specifications, contracts and interoperability artifacts. It is **not** a physical robot runner.

Python 3.10 or newer is required.

```bash
python -m pip install -e .
rgd --help
```

## Global options

```text
--quiet, -q     disable cinematic output for automation
--verbose, -v   enable diagnostic logging
```

Global options precede the command:

```bash
rgd --quiet check
rgd --verbose export ros2
```

## Specification lifecycle

### `rgd init`

Create a new profile from the packaged default seed:

```bash
rgd init my_robot
```

The seed is validated against the normative `spec/` source in CI. The command copies the selected canonical modules and personalizes only the project DID in:

```text
spec/00_core/kernel.jsonc
```

It does not copy stale unified/compiled products into the new profile.

### `rgd check`

Validate the kernel and its declared module references:

```bash
cd my_robot
rgd check
```

A specific kernel may be supplied:

```bash
rgd check spec/00_core/kernel.jsonc
```

### `rgd boot`

Load the modules referenced by a kernel and emit the current grounding representation:

```bash
rgd boot
rgd boot --output json
```

`boot` prepares structured context. It does not start a physical runtime or issue actuator commands.

### `rgd compile-spec`

Build the unified human/machine specification products:

```bash
rgd compile-spec
```

Unified artifacts are generated products, not independent sources of truth. The canonical source remains the modular JSONC under `spec/`.

### `rgd build-standard`

Generate the strict-JSON compatibility mirror from JSONC sources:

```bash
rgd build-standard
```

Repository maintainers must additionally run:

```bash
python tools/reconcile_artifacts.py
```

to prove leaf-level equivalence among `spec/`, `standard/` and the packaged default seed.

## Import and profile convergence

### `rgd import`

Import only facts supported by an external robot description:

```bash
rgd import robot.urdf --out RGD-robot
rgd import robot.usda --out RGD-robot
```

The result is a **partial** OpenRGD specification under one `spec/` root. Importers must not invent constitutional, safety or cognitive policy absent from the source description.

### `rgd alive`

Merge a partial URDF/USD import with the reviewed packaged seed:

```bash
rgd alive robot.urdf
```

This is the explicit full-profile convergence step. It is distinct from physical runtime execution.

## Interoperability exporters

### `rgd export`

Generate target-ecosystem artifacts from an OpenRGD specification:

```bash
rgd export ros2
rgd export isaac
```

Synapse exporters are static generators. Their existence does not mean that a bidirectional runtime or hardware connection has been started.

## Runtime compatibility boundary

The historical ROS 2 / Viam runtime prototype has been quarantined and removed from the installed package. The old `run` namespace remains only so existing scripts receive a deterministic migration result.

### `rgd run status`

```bash
rgd run status
rgd run status --output json
```

This command reports:

```text
status: NOT_PROVIDED_BY_CANONICAL_ROOT
historical prototype: QUARANTINED
physical actuation: disabled
```

### Legacy adapter names

```bash
rgd run ros2
rgd run viam
rgd run hybrid
```

These commands:

- never import ROS 2, Viam, serial or CAN libraries;
- never open hardware or network connections;
- never issue actuator commands;
- return `BLOCKED` with exit code `2`.

A conformant physical runtime belongs to an independently versioned repository and must consume the candidate/accepted contracts:

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

See:

```text
docs/reconciliation/RUNTIME_BOUNDARY.md
docs/reconciliation/RUNTIME_STATUS.json
```

## Validation for maintainers

```bash
python tools/validate_repository.py
python tools/reconcile_artifacts.py
python tools/validate_runtime_boundary.py
python contracts/agent/v0.1.0/validate.py
python -m pytest -q
```

The runtime-boundary validator proves that historical source blobs remain intact in the archive, no active bundled runtime survives, and the compatibility CLI fails closed.
