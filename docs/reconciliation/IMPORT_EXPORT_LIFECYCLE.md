# Robot-description evidence and static ROS 2 lifecycle

## Status

**Decision status:** implemented on the reconciliation branch, pending review and merge.  
**Execution status:** non-actuating.  
**Reference fixtures:**

```text
tests/fixtures/urdf/openrgd_minimal_arm.urdf
tests/fixtures/usd/openrgd_minimal_arm.usda
```

## Canonical flow

```text
owned/source robot description
          ↓
source-derived partial Foundation evidence
          ↓
optional explicit seed enrichment
(seed/body compatibility remains UNVERIFIED)
          ↓
OPENRGD_SOURCE_TREE_SHA256_V1
          ↓
integrity-aware static profile inspection
          ↓
deterministic non-actuating grounding context
          ↓
deterministic machine bundle
          ↓
deterministic static ROS 2 export
```

This lifecycle validates evidence extraction, provenance, file contracts and deterministic derived output. It does not launch middleware, assess the physical body or authorize execution.

## Importer boundary

Both active importers output only:

```text
01_foundation/description.jsonc
01_foundation/actuation_dynamics.jsonc
```

Both record source filename, format, byte count and SHA-256 and omit machine-local absolute paths.

They do not create:

- OpenRGD identity/kernel policy;
- safety limits absent from the source;
- alignment or ethical policy;
- cognitive capabilities;
- HAL drivers, bus addresses or actuator authorization.

### URDF

The URDF path may extract source-supported links, inertials, joint types, connectivity, origins, axes, limits, source dynamics and mimic relationships.

Missing values remain absent. Malformed and non-finite values fail closed.

### Text USDA

The text USDA path is explicitly a narrow profile, not a full OpenUSD implementation. It currently extracts stage unit metadata and directly authored revolute/prismatic UsdPhysics joint properties.

Conversion rules are evidence-bound:

```text
angular joint limits   degree → radian
linear joint limits    stage distance × metersPerUnit → metre
drive effort           converted only with authored
                       metersPerUnit + kilogramsPerUnit
```

`body0` and `body1` remain source relationship paths. The lightweight parser does not infer a universal parent/child direction, compose layers, resolve references/payloads or evaluate variants.

## Seed enrichment boundary

`rgd alive` personalizes the seed kernel DID and bundle identifier, overlays exact-path imported evidence and recalculates the profile root.

The project-level manifest records:

```text
profile_kind = SEED_ENRICHED_IMPORTED_EVIDENCE
seed_profile = <selected seed>
seed_compatibility_status = UNVERIFIED
```

A valid hash proves which files are present. It does not prove that inherited seed calibration, HAL, safety or behavioral assumptions are correct for the imported body.

## Profile inspection boundary

### `rgd check`

`check` requires:

1. canonical source-tree integrity to match;
2. the kernel to live at `spec/00_core/kernel.jsonc`;
3. non-empty identity and module-loading list;
4. safe, unique, relative JSONC references;
5. every selected file to exist;
6. every selected file to parse as a JSON object without non-finite values.

JSON output is a deterministic:

```text
OPENRGD_PROFILE_VALIDATION
```

It records:

```text
physical_execution_assessed = false
runtime_readiness = NOT_ASSESSED
```

### `rgd boot`

`boot` applies the same inspection and creates:

```text
OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT
```

The artifact contains the selected modules, source-root commitment, joint summary and alignment summary. It always records:

```text
physical_execution.assessed = false
physical_execution.authorized = false
physical_execution.status = NOT_AUTHORIZED_BY_BOOT
```

The command does not start an embodied runtime and does not claim “ready” state.

## Static ROS 2 export boundary

`rgd export ros2` requires a matching canonical root and a deterministic machine bundle generated from that root.

Every successful export writes:

```text
ros2_control.yaml
rgd_limits.xacro
export_manifest.json
```

`rgd_hardware.xacro` is emitted only when all exported joints have explicit HAL interfaces and resolve to one system driver plugin.

Export status:

```text
CONFIGURATION_ONLY
HARDWARE_BOUND
```

An imported partial body ignores inherited seed actuator/HAL mappings during export. Joint-name equality is not proof that a seed driver belongs to the imported mechanism.

## Target maturity

| Target | Status |
|---|---|
| URDF evidence import | IMPLEMENTED / TESTED |
| text USDA evidence import | IMPLEMENTED / TESTED NARROW PROFILE |
| full OpenUSD composition adapter | NOT IMPLEMENTED |
| ROS 2 static export | IMPLEMENTED / TESTED |
| Isaac static export | NOT IMPLEMENTED; historical placeholder removed |
| physical runtime | EXTERNAL TO THIS REPOSITORY |

## Verified assertions

CI verifies:

1. fixture ownership, licensing and hermeticity;
2. exact URDF-derived topology, inertials, units and limits;
3. exact USDA stage metadata and source provenance;
4. degree-to-radian and stage-unit-to-SI conversion rules;
5. absence of invented physical defaults;
6. rejection of malformed/non-finite values and ambiguous attributes;
7. absence of invented kernel/alignment/HAL policy;
8. one-root partial import;
9. seed-enriched identity and bundle personalization;
10. `UNVERIFIED` seed/body compatibility status;
11. matching canonical source-tree hash;
12. rejection of stale source trees;
13. rejection of unsafe, duplicate, missing or non-object modules;
14. deterministic validation and grounding JSON;
15. explicit non-authorization of physical execution;
16. deterministic machine compilation;
17. deterministic static ROS 2 output;
18. fixed-joint exclusion;
19. omission of hardware Xacro without complete HAL evidence;
20. rejection of the unimplemented Isaac target;
21. protection against accidental seed HAL inheritance by joint-name collision.

## Remaining limits

- No generic seed/body compatibility proof exists.
- The text USDA parser does not replace an OpenUSD SDK-based composition adapter.
- Static ROS 2 output has not been validated against a live controller stack in this repository.
- A full hardware-bound fixture requires an independently reviewed HAL/body-adapter profile.
- Physical execution remains owned by the separate embodied runtime and Body Adapter.
