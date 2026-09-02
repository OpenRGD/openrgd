# Changelog

All notable changes to the OpenRGD repository and Python toolchain are documented here. Standard, toolchain and contract versions are independent; see [`VERSIONING.md`](VERSIONING.md).

## [Unreleased] — Historical reconciliation

### Added

- Active GitHub Actions validation for Python 3.10 and 3.12.
- Windows executable build and CI artifact publication.
- Versioned `contracts/` area and Agent Contracts `v0.1.0` as a convergence candidate.
- Repository structure, versioning, provenance and reconciliation documentation.
- Machine-readable source/derived policy in `docs/reconciliation/ARTIFACT_POLICY.json`.
- Deterministic reconciliation of 76 canonical leaves across `spec/`, `standard/` and the packaged default seed.
- Canonical source-tree integrity profile `OPENRGD_SOURCE_TREE_SHA256_V1`.
- `rgd hash` verification/update command.
- Deterministic single machine-bundle compiler without wall-clock metadata.
- Runtime quarantine and fail-closed `rgd run` compatibility boundary.
- Generated-artifact and removed-example inventory with original Git identities.
- Project-owned, MIT-licensed hermetic URDF fixture under `tests/fixtures/urdf/`.
- Content-addressed URDF importer provenance using source filename, format, byte count and SHA-256.
- Deterministic ROS 2 static export manifest with explicit `CONFIGURATION_ONLY` / `HARDWARE_BOUND` status.
- End-to-end non-actuating URDF lifecycle and seed-HAL collision tests.
- Tests for real `rgd init`, source-tree hashing, deterministic bundles and mirrors, runtime quarantine, partial import and SO-101 causal ordering.

### Changed

- Minimum Python version aligned with actual syntax: Python 3.10+.
- License metadata changed to a PEP 621-compatible file reference.
- Standard `0.2.0`, Python toolchain `0.1.1` and candidate contracts `0.1.0` treated as independent axes.
- Canonical domain names restored to Foundation, Operation, Agency, Volition, Evolution and Ether under `00_core`.
- Packaged default seed synchronized with the selected canonical source set.
- `rgd init` now rehashes the project after DID personalization and fails atomically on integrity errors.
- `rgd compile-spec` now emits one deterministic machine bundle instead of human/domain/benchmark copies.
- `rgd build-standard` now mirrors only the canonical source set with destructive-path guards.
- URDF import is treated as a source-evidence operation rather than a policy generator.
- URDF import now preserves supported type-correct revolute/prismatic units, link inertials, topology, source dynamics and mimic data when present.
- Missing URDF physical values remain absent; invalid and non-finite values fail instead of receiving silent defaults.
- `rgd alive` personalizes profile identity, records source provenance and marks seed/body compatibility `UNVERIFIED`.
- `rgd export` now validates the source-tree root and machine-bundle root before generating files.
- Imported bodies are isolated from seed actuator/HAL mappings until explicit review.
- The canonical repository is explicitly non-actuating; physical runtime ownership is external.
- Quiet-mode CLI errors now use deterministic plain stderr output.

### Removed

- Tracked builds, distributions, bytecode, package metadata and local archives.
- Inactive `.github/build.yaml`.
- Stale and recursive domain/unified specification bundles and benchmark snapshots.
- Duplicate generated UR5 profiles and checked-in export outputs.
- Three unverified, non-hermetic external URDF examples.
- Incomplete MSIX shell-integration placeholder.
- Competing Node bundle builder, duplicate Python unifier, old benchmark integrity command and unreachable parallel `src/cli.py`.
- Redundant stale `requirements.txt` and its generator.
- Historical bundled ROS 2/Viam runtime from the installed package.
- Historical Isaac static generator placeholder from the active target registry.
- URDF-generated kernel and default-alignment policy.
- Generic fallback driver/address behavior from the ROS 2 static exporter.

### Preserved

- Contradictory 2025 documentation under `docs/history/`.
- Historical runtime source with verified Git blob identities.
- Superseded seed skill index.
- Original tree/blob identities for removed generated artifacts, workspaces, packaging prototypes and external examples.
- Historical importer/exporter prototype identities under `docs/history/import-export-prototypes/`.

## [0.1.1] — 2025-11-26

- Renamed the Python distribution to `rgd`.
- Prepared the `v0.1.1` repository/toolchain tag.

## [0.1.0] — 2025-11-25

- Published the initial OpenRGD draft and six-domain reference specification.
- Added the first CLI, import/export tooling and project documentation.
