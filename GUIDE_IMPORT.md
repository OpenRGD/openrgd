# OpenRGD import guide

`rgd import` ingests facts supported by an external robot-description source. It does not automatically make that source a complete cognitive, safety or governance profile.

## Current formats

| Format | Extensions | Current status |
|---|---|---|
| URDF/XML | `.urdf`, `.xml` | Experimental; importer lineage still requires reconciliation |
| ASCII USD | `.usda`, `.usd` | Reconciled partial-evidence path |

Binary USD and USDZ are not supported by the lightweight parser.

## ASCII USD behavior

```bash
rgd import robot.usda --out ./partial-rgd
```

The importer may extract:

- stage/default robot name;
- revolute and prismatic joint names;
- lower and upper limits;
- maximum force;
- drive stiffness and damping.

It writes source-supported Foundation evidence under:

```text
partial-rgd/spec/01_foundation/description.jsonc
partial-rgd/spec/01_foundation/actuation_dynamics.jsonc
```

It does not invent:

- a kernel;
- a safety policy;
- an alignment constitution;
- hardware trust claims;
- actuator calibration not present in the source.

## Enrichment

To merge imported evidence with the reviewed default OpenRGD profile, use the separate `alive` operation:

```bash
rgd alive robot.usda --out ./my-robots/RGD-robot
```

After intentional manual changes, refresh and verify the source root:

```bash
cd ./my-robots/RGD-robot
rgd hash --write
rgd hash
```

## Examples

The historical large BHL, iCub and UR5 URDF files were removed from the active repository. They referenced missing assets or local deployment details and were not hermetic, license-audited fixtures. Future importer examples must be minimal, redistribution-audited and tested automatically.

See `docs/reconciliation/EXAMPLES_AND_FIXTURES.md`.
