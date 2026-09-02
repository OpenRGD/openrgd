# OpenRGD Import Guide

`rgd import` extracts facts from an external robot description into a **partial, non-actuating OpenRGD Foundation profile**.

It does not create identity, constitutional alignment, safety policy, cognition, skills or hardware authorization. Those elements are not present in URDF/USD and must not be invented by an importer.

## Supported inputs

| Input | Current status | Notes |
|---|---|---|
| URDF (`.urdf`, `.xml`) | Tested | XML root must be `<robot>` |
| ASCII USD (`.usda`, text `.usd`) | Tested lightweight path | Binary USD must be converted before import |

## Evidence boundary

The reconciled URDF importer may extract:

- robot name;
- links;
- inertial mass, origin and complete inertia tensor when present;
- joint name and type;
- parent/child connectivity;
- origin and axis;
- declared limits with type-correct units;
- source damping and friction;
- mimic relationship.

It emits only:

```text
spec/01_foundation/description.jsonc
spec/01_foundation/actuation_dynamics.jsonc
```

It does **not** emit:

```text
spec/00_core/kernel.jsonc
spec/02_operation/*
spec/03_agency/*
spec/04_volition/alignment.jsonc
```

Missing URDF numeric values remain absent. Invalid or non-finite numeric values fail the import instead of being replaced by silent defaults.

## Provenance

Reconciled URDF evidence records:

```text
source filename
source format
source byte length
source SHA-256
```

Machine-local absolute paths are not embedded in the generated URDF profile.

## Partial import

```bash
rgd import robot.urdf --out partial-robot
```

The result is intentionally incomplete:

```text
partial-robot/
└── spec/
    └── 01_foundation/
        ├── description.jsonc
        └── actuation_dynamics.jsonc
```

This is the preferred operation when reviewing what the source file actually proves.

## Seed enrichment

```bash
rgd alive robot.urdf --out RGD-robot --seed default
```

`rgd alive` performs a separate, explicit operation:

```text
source-derived Foundation evidence
              +
reviewed packaged seed
              ↓
full integrity-addressed profile
```

The output project records:

```text
profile_kind = SEED_ENRICHED_IMPORTED_EVIDENCE
seed_compatibility_status = UNVERIFIED
```

The current default seed contains reference assumptions. Successful enrichment and a valid source-tree hash do not prove that inherited calibration, HAL, safety or behavioral modules match the imported body. Review them before any hardware use.

## Project-owned fixture

A minimal hermetic fixture is provided at:

```text
tests/fixtures/urdf/openrgd_minimal_arm.urdf
```

Its provenance is documented beside it. The fixture has no mesh assets, package references, network addresses or machine-local paths and is exercised by CI through import, enrichment, hashing, structural checks, boot prompt assembly, deterministic compilation and static ROS 2 export.

## Current limitations

- Geometry and mesh conversion is outside the lightweight importer contract.
- Transmissions, controllers, vendor plugins and bus addresses are not inferred from URDF.
- Imported evidence cannot authorize hardware execution.
- Seed/body semantic compatibility remains an explicit review task.
- The ASCII USD parser is lightweight and remains a separate hardening surface; it does not replace a full USD SDK.
