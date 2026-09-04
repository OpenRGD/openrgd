# Changelog

## Unreleased

### Added
- `rgd alive` as the one-command Golden Loop from URDF/USDA to validated OpenRGD profile, grounding, deterministic bundle and static ROS 2 output.
- Ready-to-run minimal URDF and USDA examples under `example/`.
- Actuator lineage/model schema, richer actuation topology, rigid-body dynamics and calibration data in Foundation.
- Experimental AION packet and HyperAion projection specifications.
- Explicit engineering-target semantics for low-level safety/control goals, including the 1 kHz safety/reflex target.
- Docker and community/onboarding guides restored as public project documentation.

### Changed
- Safety, real-time and standards-related fields now distinguish measured/implemented behavior from engineering targets and certification claims.
- Repository documentation is focused on the public project rather than internal development notes.

### Removed
- Generated build outputs, duplicate robot workspaces and internal development/audit notes from the public source tree.

## 0.1.1 — 2025-11-26
- Renamed the Python distribution to `rgd`.

## 0.1.0 — 2025-11-25
- First public OpenRGD draft and CLI/tooling baseline.
