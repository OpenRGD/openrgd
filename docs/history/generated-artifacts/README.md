# Removed generated artifacts and examples

**Classification:** historical evidence, non-normative  
**Reconciliation date:** 2026-09-02

This directory records the generated, duplicated, incomplete or externally sourced material removed from the active OpenRGD repository during the canonical-artifact reconciliation.

The removed bytes remain recoverable from Git history. Large generated bundles and third-party URDF files are not copied again into this directory because duplication would add repository weight without adding provenance. Their original Git tree/blob identifiers are recorded in [`INVENTORY.json`](INVENTORY.json).

## Why the old aggregates were removed

The old domain and unified JSONC files were not clean snapshots. The generator scanned previously generated `*_spec.jsonc` files as source. A domain bundle therefore included older copies of itself, and the unified bundle then included those already recursive domain bundles. Volatile timestamps and multiple competing generator implementations prevented reproducible byte identity.

They are classified **SUPERSEDED_RECURSIVE_GENERATED_OUTPUT**, not specification source.

## Why the old examples were removed

The `example/` directory contained three large externally produced URDF files:

- Berkeley Humanoid Lite, referencing absent local mesh assets;
- iCub, referencing absent package meshes;
- UR5, containing a local robot-controller IP and installation-specific paths.

None was a small, hermetic, license-audited test fixture. Their presence did not prove importer compatibility. OpenRGD will add owned, minimal and automatically tested fixtures only after the relevant importer contract is reconciled.

## Why generated robot profiles and exports were removed

`RGD-ur5/` and `my-robots/RGD-ur5/` carried the exact same generated specification tree and differed only in metadata timestamps. `export/` contained unasserted generated ROS 2 and Isaac outputs. Generated project and export directories now belong in local workspaces or CI artifacts, not in the canonical source tree.

## Integrity replacement

The old benchmark-copy mechanism has been replaced by the versioned `OPENRGD_SOURCE_TREE_SHA256_V1` profile. It commits the canonical modular source tree directly and generates deterministic machine bundles on demand.
