# OpenRGD — Robot Graph Definition

**OpenRGD** is an open, machine-readable standard for cognitive embodiment: a semantic bridge through which an AI system can understand a robot body, its operational limits, its capabilities, its lifecycle and its relationships with other agents.

| Artifact | Current repository version | Maturity |
|---|---:|---|
| OpenRGD standard bundle | `0.2.0` | Draft; maturity is declared per domain |
| `rgd` Python toolchain | `0.1.1` | Working alpha |
| Agent interoperability contracts | `0.1.0` | Convergence candidate |

These versions are independent. See [`VERSIONING.md`](VERSIONING.md).

## What this repository contains

- `spec/` — normative human-readable JSONC source for the OpenRGD standard and reference bundle;
- `standard/` — strict-JSON compatibility mirror validated against the specification;
- `contracts/` — cross-component interfaces with explicit maturity and provenance;
- `src/openrgd/` — the non-actuating Python CLI and current reference tooling;
- importers for URDF and USD;
- Synapse generators for ROS 2 and Isaac-oriented outputs;
- a packaged default profile synchronized from reviewed specification sources;
- examples, build tools and historical documentation.

This repository does **not** ship a physical embodied runtime or a hardware adapter implementation. The former bundled ROS 2 / Viam prototype has been preserved under `docs/history/runtime-prototype/` and removed from the installed package because it could not prove the convergent safety and execution boundary.

The repository also does not claim that a complete HyperAion512 encoder, Chronograf production signing or Rate My Ethics runtime integration are already finished.

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

The current bundle manifest marks Foundation and Operation as stable, Agency and Volition as experimental, and Evolution and Ether as proposals. The exact repository authority rules are documented in [`STRUCTURE.md`](STRUCTURE.md).

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

Typical specification workflow:

```bash
rgd init Robot
cd Robot
rgd check
rgd boot
rgd compile-spec
rgd export ros2
```

Available active CLI areas include `init`, `check`, `boot`, `alive`, `import`, `export`, `build-standard` and `compile-spec`.

The historical `run` namespace remains only as a fail-closed migration/status boundary:

```bash
rgd run status
rgd run status --output json
```

Legacy adapter commands such as `rgd run ros2` and `rgd run viam` return a deterministic blocked result and do not import middleware or actuate hardware. See [`docs/reconciliation/RUNTIME_BOUNDARY.md`](docs/reconciliation/RUNTIME_BOUNDARY.md).

## Source and derived artifacts

The reconciliation branch enforces:

```text
spec/                              normative JSONC source
        ↓ parsed equivalence
standard/                          derived strict JSON mirror
        ↓ selected byte equivalence
src/openrgd/seeds/default/spec/    derived packaged profile
```

Check the relationship with:

```bash
python tools/reconcile_artifacts.py
```

Runtime-profile divergences require an explicit, justified and hash-pinned override. The default seed currently has zero approved overrides.

## Contracts and auditability

The candidate agent contracts make the boundary between cognition and actuation explicit:

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

They also formalize Chronons as canonical historical evidence, memory as a projection, and DecisionTrace as structured audit evidence rather than private chain-of-thought. Candidate material remains non-stable until accepted through governance.

Validate the imported contract package and runtime quarantine with:

```bash
python contracts/agent/v0.1.0/validate.py
python tools/validate_runtime_boundary.py
```

GitHub Actions validates Python 3.10 and 3.12, checks canonical artifact mirrors, verifies the fail-closed runtime boundary, runs tests and builds a Windows executable artifact.

## Documentation

- [`STRUCTURE.md`](STRUCTURE.md) — authority model, domains and boundaries;
- [`LAYOUT.md`](LAYOUT.md) — actual repository directory map;
- [`GLOSSARIO.md`](GLOSSARIO.md) — shared terminology;
- [`VERSIONING.md`](VERSIONING.md) — independent version axes;
- [`docs/reconciliation/`](docs/reconciliation/) — historical reconciliation record;
- [`docs/history/`](docs/history/) — preserved non-normative 2025 documents and code evidence.

## Governance and contribution

OpenRGD follows an RFC-oriented development model. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing normative changes. A file being present in `contracts/` or `docs/reconciliation/` does not make it stable: its maturity label controls its authority.

## Author

**Pasquale Ranieri — Italia Robotica**  
Lead architect and specification author.

OpenRGD is distributed under the MIT License.
