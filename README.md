# OpenRGD — Robot Graph Definition

**OpenRGD** is an open, machine-readable standard for cognitive embodiment: a semantic bridge through which an AI system can understand a robot body, its operational limits, its capabilities, its lifecycle and its relationships with other agents.

| Artifact | Current repository version | Maturity |
|---|---:|---|
| OpenRGD standard bundle | `0.2.0` | Draft; maturity is declared per domain |
| `rgd` Python toolchain | `0.1.1` | Working alpha |
| Agent interoperability contracts | `0.1.0` | Convergence candidate |

These versions are independent. See [`VERSIONING.md`](VERSIONING.md).

## What this repository contains

- `spec/` — normative modular JSONC source;
- `standard/` — tracked strict-JSON leaf mirror;
- `contracts/` — cross-component interfaces with explicit maturity and provenance;
- `src/openrgd/` — non-actuating CLI and reference tooling;
- a source-evidence URDF importer and lightweight ASCII USD importer;
- a deterministic static ROS 2 Synapse exporter;
- a packaged default profile synchronized from reviewed specification sources;
- project-owned hermetic test fixtures;
- historical and reconciliation records.

This repository does **not** ship a physical embodied runtime or a Body Adapter. The former bundled ROS 2/Viam prototype is preserved under `docs/history/runtime-prototype/` and removed from the installed package because it did not implement the convergent safety and execution boundary.

The repository also does not claim that HyperAion512 encoding, Chronograf production signing, Rate My Ethics runtime integration or an Isaac static exporter are complete.

## Canonical domain model

```text
00_core         coordination, manifests and kernel metadata
01_foundation   physical body and hardware reality
02_operation    runtime constraints, safety and physiological operation
03_agency       capabilities, world model and action interfaces
04_volition     values, alignment and decision governance
05_evolution    lifecycle, wear, adaptation and continuity
06_ether        collective, social and inter-agent protocols
```

The current bundle manifest marks Foundation and Operation as stable, Agency and Volition as experimental, and Evolution and Ether as proposals. Repository authority rules are documented in [`STRUCTURE.md`](STRUCTURE.md).

## Install the toolchain

Python **3.10 or newer** is required.

```bash
git clone https://github.com/OpenRGD/openrgd.git
cd openrgd
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
rgd --help
```

## Standard and profile workflow

```bash
rgd init Robot
cd Robot
rgd hash
rgd check
rgd boot
rgd compile-spec
```

Authority:

```text
spec/                              normative JSONC source
        ↓ parsed equivalence
standard/                          tracked strict-JSON leaf mirror
        ↓ selected byte equivalence
src/openrgd/seeds/default/spec/    tracked derived default profile
```

`OPENRGD_SOURCE_TREE_SHA256_V1` commits the selected modular source tree. Verify or intentionally update it with:

```bash
rgd hash
rgd hash --write
```

## Import and enrichment

`rgd import` extracts source-supported physical evidence only:

```bash
rgd import robot.urdf --out partial-robot
```

The reconciled URDF path does not invent kernel identity, safety, cognition or alignment. It emits only:

```text
01_foundation/description.jsonc
01_foundation/actuation_dynamics.jsonc
```

`rgd alive` is the separate, explicit seed-enrichment operation:

```bash
rgd alive robot.urdf --out RGD-robot --seed default
```

The resulting project is integrity-addressed, but its manifest records:

```text
seed_compatibility_status = UNVERIFIED
```

A valid hash proves content identity, not that inherited calibration, HAL or safety assumptions fit the imported body.

A synthetic project-owned fixture is available at `tests/fixtures/urdf/openrgd_minimal_arm.urdf` and is exercised end to end in CI.

## Static interoperability export

After compiling a verified profile:

```bash
rgd export ros2 --out export/ros2
```

The active ROS 2 Synapse is deterministic and non-actuating. It produces controller/limit configuration and an `export_manifest.json` with explicit completeness status.

`rgd_hardware.xacro` is emitted only when every exported joint has explicit HAL interfaces and the joint set resolves to one system driver plugin. Imported bodies cannot inherit seed driver bindings through a coincidental joint-name match.

The historical Isaac generator was a placeholder and is not active. `rgd export isaac` fails explicitly.

## Runtime boundary

```bash
rgd run status
rgd run status --output json
```

Legacy adapter commands such as `rgd run ros2` and `rgd run viam` return a deterministic blocked result and do not import middleware or actuate hardware. See [`docs/reconciliation/RUNTIME_BOUNDARY.md`](docs/reconciliation/RUNTIME_BOUNDARY.md).

The candidate cognitive-to-physical contract remains:

```text
CognitionProposal
      ↓
ActionIntent
      ↓
Somatic Translator
      ↓
CapabilityPlan
      ↓
Operation Safety Gate
      ↓
DecisionTrace
      ↓
Body Adapter
      ↓
Hardware
```

## Documentation

- [`CLI_GUIDE.md`](CLI_GUIDE.md) — current command behavior;
- [`GUIDE_IMPORT.md`](GUIDE_IMPORT.md) — evidence-only import and enrichment boundary;
- [`GUIDE_EXPORT.md`](GUIDE_EXPORT.md) — deterministic static ROS 2 output;
- [`STRUCTURE.md`](STRUCTURE.md) — authority model and component boundaries;
- [`LAYOUT.md`](LAYOUT.md) — active repository tree;
- [`GLOSSARIO.md`](GLOSSARIO.md) — shared terminology;
- [`VERSIONING.md`](VERSIONING.md) — independent version axes;
- [`docs/reconciliation/`](docs/reconciliation/) — current decisions and audits;
- [`docs/history/`](docs/history/) — preserved non-normative history.

## Governance and contribution

OpenRGD follows an RFC-oriented development model. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing normative changes. A file being present in `contracts/` or `docs/reconciliation/` does not make it stable: its maturity label controls its authority.

## Author

**Pasquale Ranieri — Italia Robotica**  
Lead architect and specification author.

OpenRGD is distributed under the MIT License.
