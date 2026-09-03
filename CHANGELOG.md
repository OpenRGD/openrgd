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
- Project-owned, MIT-licensed hermetic URDF and USDA fixtures.
- Content-addressed robot-description provenance using source filename, format, byte count and SHA-256.
- Narrow text USDA evidence profile with authored stage-unit conversion and raw-source preservation.
- Shared integrity-aware profile inspector used by `rgd check` and `rgd boot`.
- Deterministic `OPENRGD_PROFILE_VALIDATION` and `OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT` JSON artifacts.
- Deterministic ROS 2 static export manifest with explicit `CONFIGURATION_ONLY` / `HARDWARE_BOUND` status.
- End-to-end non-actuating URDF/USDA lifecycles and seed-HAL collision tests.
- Human-accountable governance model in `GOVERNANCE.md` and `governance/policy.json`.
- Scoped release and tag rules in `RELEASE_POLICY.md`.
- Security and physical-safety reporting policy.
- CODEOWNERS, pull-request template and normative RFC template.
- Machine-readable candidate status for Agent Contracts.
- Explicit digest-only evidence exclusion for `openrgd-v0.2-aion-ready.zip`.
- Merge-readiness record and documented server-side branch-protection gate.
- CI-enforced governance validator and regression tests.

### Changed

- Minimum Python version aligned with actual syntax: Python 3.10+.
- License metadata changed to a PEP 621-compatible file reference.
- Standard `0.2.0`, Python toolchain `0.1.1` and candidate contracts `0.1.0` treated as independent axes.
- Canonical domain names restored to Foundation, Operation, Agency, Volition, Evolution and Ether under `00_core`.
- Packaged default seed synchronized with the selected canonical source set.
- `rgd init` now rehashes the project after DID personalization and fails atomically on integrity errors.
- `rgd compile-spec` now emits one deterministic machine bundle instead of human/domain/benchmark copies.
- `rgd build-standard` now mirrors only the canonical source set with destructive-path guards.
- URDF and USDA import are treated as source-evidence operations rather than policy generators.
- URDF import now preserves supported type-correct units, link inertials, topology, source dynamics and mimic data when present.
- USDA import now preserves directly authored stage metadata, joint relationships, raw limits, local frames and drive values.
- USD revolute limits are converted from degrees to radians; prismatic and drive values are converted to SI only when required stage unit metadata is authored.
- Missing importer values remain absent; invalid/non-finite and ambiguous values fail instead of receiving silent defaults.
- `rgd alive` personalizes profile identity, records source provenance and marks seed/body compatibility `UNVERIFIED`.
- `rgd check` now validates source-tree integrity and every kernel-selected JSONC object instead of testing file existence alone.
- `rgd boot` now emits deterministic non-actuating grounding data and explicitly denies runtime/actuation authority.
- `rgd export` now validates the source-tree root and machine-bundle root before generating files.
- Imported bodies are isolated from seed actuator/HAL mappings until explicit review.
- The canonical repository is explicitly non-actuating; physical runtime ownership is external.
- Quiet-mode CLI errors use deterministic plain stderr output.
- New release tags are scoped to `standard-v*`, `toolchain-v*` or `contracts-agent-v*`.
- Windows release assets are published only from `toolchain-v*` tags.
- Merge commits are the default to preserve granular reviewed history; squash requires an explicit exception.
- Agent Contracts validation now proves that candidate/non-normative status has not been silently promoted.
- Single-maintainer review requirements are explicit and must become one non-author approval when a second maintainer is appointed.

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
- USD convenience defaults and machine-local source paths.
- Generic fallback driver/address behavior from the ROS 2 static exporter.
- `check`/`boot` readiness language, warning-only module failures and integrity-blind loading.
- Generic future tag trigger `v*.*.*` from the active workflow.

### Preserved

- Contradictory 2025 documentation under `docs/history/`.
- Historical runtime source with verified Git blob identities.
- Superseded seed skill index.
- Original tree/blob identities for removed generated artifacts, workspaces, packaging prototypes and external examples.
- Historical importer/exporter and profile-inspection prototype identities under `docs/history/`.
- Existing unscoped `v0.1.0` and `v0.1.1` tags as historical repository/toolchain evidence.
- The granular reconciliation commit sequence for merge by merge commit.

### Governance status

- Repository-tree governance: frozen and CI-validated.
- Agent Contracts: remain `candidate`, non-normative.
- AION-ready archive: explicitly excluded as digest-only evidence; later recovery requires a separate delta PR.
- Signing: not implemented and not claimed; remains a stable-release gate.
- `main` protection: required before merge and tracked in issue #2.
- Merge and release: separate; no tag or release is created by reconciliation PR #1.

## [0.1.1] — 2025-11-26

- Renamed the Python distribution to `rgd`.
- Prepared the `v0.1.1` repository/toolchain tag.

## [0.1.0] — 2025-11-25

- Published the initial OpenRGD draft and six-domain reference specification.
- Added the first CLI, import/export tooling and project documentation.
