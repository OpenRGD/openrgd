# URDF import and static ROS 2 lifecycle

## Status

**Decision status:** implemented on the reconciliation branch, pending review and merge.  
**Execution status:** non-actuating.  
**Reference fixture:** `tests/fixtures/urdf/openrgd_minimal_arm.urdf`.

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
structural check and boot prompt assembly
          ↓
deterministic machine bundle
          ↓
deterministic static ROS 2 export
```

This flow validates file contracts and provenance. It does not launch middleware or authorize physical execution.

## URDF importer boundary

The reconciled importer outputs only:

```text
01_foundation/description.jsonc
01_foundation/actuation_dynamics.jsonc
```

It records source filename, format, byte count and SHA-256. It does not persist a machine-local absolute path.

It may extract only values present in the source. Missing values remain absent. Malformed and non-finite numeric values fail closed.

It does not create:

- OpenRGD identity/kernel policy;
- safety limits not present in the source;
- alignment or ethical policy;
- cognitive capabilities;
- HAL drivers, bus addresses or actuator mappings.

## Seed enrichment boundary

`rgd alive` personalizes the seed kernel DID and bundle identifier, merges exact-path Foundation evidence and recalculates the profile root.

The project-level manifest records:

```text
profile_kind = SEED_ENRICHED_IMPORTED_EVIDENCE
seed_profile = <selected seed>
seed_compatibility_status = UNVERIFIED
```

A valid hash proves which files are present. It does not prove that inherited seed calibration, HAL, safety or behavioral assumptions are correct for the imported body.

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
| ROS 2 static export | IMPLEMENTED / TESTED |
| Isaac static export | NOT IMPLEMENTED; historical placeholder removed from active registry |
| Physical runtime | EXTERNAL TO THIS REPOSITORY |

## Verified lifecycle assertions

CI verifies:

1. fixture provenance and hermeticity;
2. exact URDF-derived link, topology, units and limits;
3. absence of invented kernel/alignment policy;
4. rejection of non-finite physical values;
5. one-root partial import;
6. seed-enriched identity and bundle personalization;
7. `UNVERIFIED` seed/body compatibility status;
8. matching canonical source-tree hash;
9. successful structural `check`;
10. successful non-actuating boot prompt assembly;
11. deterministic machine compilation;
12. deterministic static ROS 2 output across independent directories;
13. fixed-joint exclusion;
14. omission of hardware Xacro without complete HAL evidence;
15. rejection of the unimplemented Isaac target;
16. protection against accidental seed HAL inheritance through a joint-name collision.

## Remaining limits

- No generic seed/body compatibility proof exists yet.
- Static ROS 2 output has not been validated against a live ROS 2 controller stack in this repository.
- A full hardware-bound fixture requires an independently reviewed HAL/body-adapter profile.
- Physical execution remains owned by the separate embodied runtime and body adapter.
