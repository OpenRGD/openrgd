# OpenRGD Import Guide

`rgd import` extracts facts from an external robot description into a **partial, non-actuating OpenRGD Foundation profile**.

It does not create identity, constitutional alignment, safety policy, cognition, skills or hardware authorization. Those elements are not established by URDF or USD source data and must not be invented by an importer.

## Supported inputs

| Input | Current status | Boundary |
|---|---|---|
| URDF (`.urdf`, `.xml`) | Implemented and lifecycle-tested | XML robot topology/inertials/limits/dynamics subset |
| USDA (`.usda`, UTF-8 text `.usd`) | Implemented and lifecycle-tested narrow subset | Text stage metadata plus revolute/prismatic UsdPhysics joint subset |
| Binary USD/USDC | Not supported by this parser | Convert to USDA or use a future OpenUSD SDK adapter |

Both paths emit only:

```text
spec/01_foundation/description.jsonc
spec/01_foundation/actuation_dynamics.jsonc
```

Both record source filename, format, byte length and SHA-256 without embedding a machine-local absolute path.

## URDF evidence boundary

The URDF importer may extract:

- robot name;
- links;
- inertial mass, origin and complete inertia tensor when present;
- joint name and type;
- parent/child connectivity;
- origin and axis;
- declared limits with type-correct units;
- source damping and friction;
- mimic relationships.

It does not infer transmissions, controllers, vendor plugins, bus addresses or calibration.

Missing numeric values remain absent. Malformed and non-finite values fail the import instead of receiving silent defaults.

## USDA evidence boundary

The text USDA importer intentionally implements a restricted, auditable profile:

```text
OPENUSD_USDA_LIGHTWEIGHT_V1
```

It currently recognizes:

- stage `defaultPrim`;
- stage `metersPerUnit`;
- stage `kilogramsPerUnit`;
- stage `upAxis`;
- `PhysicsRevoluteJoint`;
- `PhysicsPrismaticJoint`;
- `physics:body0` and `physics:body1` relationships;
- X/Y/Z joint axis tokens;
- authored lower/upper limits;
- local joint frames when directly authored;
- angular/linear drive `maxForce`, stiffness and damping when directly authored.

The parser preserves `body0` and `body1` as source relationships. It does not reinterpret them as a universal parent/child direction, because joint relationship ordering and scene composition require fuller USD semantics.

### Unit rules

UsdPhysics uses degrees as its angular unit, stage distance units scaled by `metersPerUnit`, and stage mass units scaled by `kilogramsPerUnit`. The importer therefore applies only conversions justified by authored stage metadata:

```text
revolute lower/upper:
    degrees → radians

prismatic lower/upper:
    stage distance × metersPerUnit → metres

linear drive maxForce:
    source value × kilogramsPerUnit × metersPerUnit → newtons

angular drive maxForce:
    source value × kilogramsPerUnit × metersPerUnit² → newton-metres
```

Rules:

1. prismatic SI limits are rejected when `metersPerUnit` is absent;
2. drive effort is converted to SI only when both `metersPerUnit` and `kilogramsPerUnit` are authored;
3. raw authored values remain in `source_usd_joint_map` even when SI effort cannot be derived;
4. absent values remain absent;
5. duplicate ambiguous attributes, inverted limits and malformed/non-finite numbers fail closed.

External standards basis: the OpenUSD UsdPhysics specification defines the unit system and stage-level scaling behavior. The lightweight importer deliberately implements only the subset listed above.

### Deliberate limitations

This parser does not:

- compose multiple USD layers;
- resolve references or payloads;
- evaluate variants;
- resolve inherited opinions;
- evaluate complete transform stacks;
- discover all schema APIs applied to arbitrary prims;
- compute body mass properties;
- implement schema fallback/sentinel behavior comprehensively;
- replace the OpenUSD SDK.

A source requiring any of those semantics must use a future full OpenUSD adapter rather than silently accepting incomplete interpretation.

## Partial import

```bash
rgd import robot.urdf --out partial-robot
rgd import robot.usda --out partial-robot
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
rgd alive robot.usda --out RGD-robot --seed default
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

## Project-owned fixtures

```text
tests/fixtures/urdf/openrgd_minimal_arm.urdf
tests/fixtures/usd/openrgd_minimal_arm.usda
```

Each fixture has provenance documented beside it. Both are synthetic, MIT-licensed, hermetic, free of network and machine-local references, and exercised through import, enrichment, hashing, profile inspection, deterministic compilation and static ROS 2 export.

## Profile inspection after enrichment

```bash
cd RGD-robot
rgd check --output json
rgd boot --output json
```

`check` validates source integrity and every kernel-selected JSONC module. `boot` creates a deterministic non-actuating grounding context. Neither command validates physical compatibility or authorizes hardware execution.
