# Changelog

All notable changes to the OpenRGD repository and Python toolchain are documented here. Standard, toolchain and contract versions are independent; see [`VERSIONING.md`](VERSIONING.md).

## [Unreleased] — Historical reconciliation

### Added

- Active GitHub Actions workflow validating Python 3.10 and 3.12.
- Windows executable build and artifact publication in CI.
- Versioned `contracts/` area with maturity and provenance rules.
- OpenRGD Agent Contracts `v0.1.0` imported as a **convergence candidate**.
- Explicit repository versioning, structure, glossary and reconciliation documentation.
- Machine-readable artifact authority in `docs/reconciliation/ARTIFACT_POLICY.json`.
- Deterministic `tools/reconcile_artifacts.py` checker for the normative specification, strict JSON mirror and packaged default seed.
- CI validation of 76 selected canonical leaves across `standard/` and the default seed.
- Real `rgd init` materialization test, including exact enforcement of the intentional kernel DID personalization boundary.

### Changed

- Declared minimum Python version aligned with the runtime syntax: Python 3.10+.
- Project license metadata changed to a PEP 621-compatible file reference.
- Documentation now distinguishes the standard bundle (`0.2.0`), toolchain (`0.1.1`) and candidate contracts (`0.1.0`).
- Canonical domain names restored to `Foundation / Operation / Agency / Volition / Evolution / Ether`, coordinated by `00_core`.
- Packaged default seed synchronized with all 76 selected canonical source artifacts.
- Stale seed revisions of `kernel.jsonc`, `actuation_topology.jsonc` and `surface_properties.jsonc` replaced with canonical bytes.
- Missing Agency extension-policy, installed-skill, skill-library, core-skill and skill-schema files restored to the packaged seed.

### Removed

- Tracked build products, distributions, Python bytecode, generated package metadata and the local source archive.
- Inactive `.github/build.yaml`, replaced by `.github/workflows/ci.yml`.
- Generated unified JSON/JSONC outputs from the active default seed.
- The legacy seed-only strict-JSON skill index from the active seed namespace.

### Preserved

- Original 2025 documentation is retained under `docs/history/` as non-normative evidence.
- The removed seed-only skill index is retained byte-for-byte under `docs/history/seed/`.
- Generated domain/unified bundles, benchmark snapshots and robot-instance copies remain available pending a separate aggregate-artifact reconciliation decision.

## [0.1.1] — 2025-11-26

- Renamed the Python distribution to `rgd`.
- Prepared the `v0.1.1` repository/toolchain tag.

## [0.1.0] — 2025-11-25

- Published the initial OpenRGD draft and six-domain reference specification.
- Added the first CLI, import/export tooling and project documentation.
