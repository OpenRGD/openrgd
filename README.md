# OpenRGD — Robot Graph Definition

**OpenRGD** is an open, machine-readable standard for cognitive embodiment: a semantic bridge through which an AI system can understand a robot body, its operational limits, its capabilities, its lifecycle and its relationships with other agents.

| Artifact | Current repository version | Maturity |
|---|---:|---|
| OpenRGD standard bundle | `0.2.0` | Draft; maturity is declared per domain |
| `rgd` Python toolchain | `0.1.1` | Working alpha |
| Agent interoperability contracts | `0.1.0` | Convergence candidate |

These versions are independent. See [`VERSIONING.md`](VERSIONING.md).

## Repository role

This repository is the proposed **non-actuating canonical/tooling root** for:

- `spec/` — normative modular JSONC source;
- `standard/` — tracked strict-JSON leaf mirror;
- `contracts/` — cross-component interfaces with explicit maturity and provenance;
- `src/openrgd/` — validation, hashing, import, enrichment, deterministic compilation and static export tooling;
- `tests/fixtures/` — project-owned, non-normative test evidence;
- historical and reconciliation records.

It does **not** ship a physical embodied runtime or a Body Adapter. The former bundled ROS 2/Viam prototype is preserved under `docs/history/runtime-prototype/` and removed from the installed package because it did not implement the convergent safety and execution boundary.

The repository also does not claim that HyperAion512 encoding, Chronograf production signing, Rate My Ethics runtime integration, a complete OpenUSD composition engine or an Isaac static exporter are implemented.

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
rgd check --output json
rgd boot --output json
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

`rgd check` verifies the declared source root, canonical kernel path, safe and unique module references, module presence and JSONC object loading. It does not assess runtime or hardware readiness.

`rgd boot` builds a deterministic **non-actuating grounding context** from the integrity-verified, kernel-selected modules. It explicitly records that physical execution is neither assessed nor authorized.

## Robot-description evidence

`rgd import` extracts only source-supported Foundation evidence:

```bash
rgd import robot.urdf --out partial-robot
rgd import robot.usda --out partial-robot
```

Both active importer paths emit only:

```text
01_foundation/description.jsonc
01_foundation/actuation_dynamics.jsonc
```

The reconciled URDF importer preserves supported topology, inertials, limits, mimic relations and dynamics without inventing absent values.

The text USDA importer intentionally supports a narrow subset of `PhysicsRevoluteJoint` and `PhysicsPrismaticJoint`. It records stage metadata and source provenance, converts authored angular limits from degrees to radians, and converts linear/mass-derived values only when the stage explicitly authors the required unit metadata. It does not compose layers, resolve references or replace the OpenUSD SDK.

Neither importer creates kernel identity, constitutional alignment, safety policy, cognition, HAL drivers, bus addresses or hardware authorization.

## Seed enrichment

`rgd alive` is a separate, explicit operation:

```bash
rgd alive robot.urdf --out RGD-robot --seed default
rgd alive robot.usda --out RGD-robot --seed default
```

The resulting project is integrity-addressed, but its manifest records:

```text
seed_compatibility_status = UNVERIFIED
```

A valid hash proves content identity, not that inherited calibration, HAL or safety assumptions fit the imported body.

Project-owned fixtures are maintained under:

```text
tests/fixtures/urdf/openrgd_minimal_arm.urdf
tests/fixtures/usd/openrgd_minimal_arm.usda
```

Both are synthetic, MIT-licensed, hermetic, non-normative and exercised end to end in CI.

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
- [`GUIDE_IMPORT.md`](GUIDE_IMPORT.md) — evidence-only URDF/USDA import and enrichment boundary;
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
