# OpenRGD — Robot Graph Definition

**OpenRGD** is an open, machine-readable standard for cognitive embodiment: a semantic bridge through which an AI system can understand a robot body, its operational limits, its capabilities, its lifecycle and its relationships with other agents.

| Artifact | Repository version | Maturity |
|---|---:|---|
| OpenRGD standard bundle | `0.2.0` | Draft; maturity declared per domain |
| `rgd` Python toolchain | `0.1.1` | Working alpha |
| Agent interoperability contracts | `0.1.0` | Convergence candidate |

These version axes are independent. See [`VERSIONING.md`](VERSIONING.md).

## Repository scope

This repository is the non-actuating canonical and tooling root. It contains:

- `spec/` — normative, modular JSONC source;
- `standard/` — tracked strict-JSON leaf mirror;
- `contracts/` — versioned cross-component contracts with explicit maturity;
- `src/openrgd/` — CLI, import/export and validation tooling;
- `src/openrgd/seeds/default/` — reconciled default profile used by `rgd init`;
- `docs/reconciliation/` — current decisions and audit evidence;
- `docs/history/` — preserved non-normative historical material.

It does **not** ship a physical embodied runtime or hardware adapter. The former bundled ROS 2/Viam prototype is preserved under `docs/history/runtime-prototype/` and removed from the installed package. `rgd run` remains only as a fail-closed compatibility/status boundary.

## Canonical domains

```text
00_core         coordination, manifests and kernel metadata
01_foundation   physical body and hardware reality
02_operation    runtime constraints, safety and physiological operation
03_agency       capabilities, world model and action interfaces
04_volition     values, alignment and decision governance
05_evolution    lifecycle, wear, adaptation and continuity
06_ether        collective, social and inter-agent protocols
```

The bundle manifest marks Foundation and Operation as stable, Agency and Volition as experimental, and Evolution and Ether as proposals.

## Installation

Python **3.10 or newer** is required.

```bash
git clone https://github.com/OpenRGD/openrgd.git
cd openrgd
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
rgd --help
```

## Specification workflow

```bash
rgd init Robot
cd Robot
rgd hash
rgd check
rgd boot
rgd compile-spec
```

`rgd init` personalizes the project DID and immediately recalculates the project's canonical source-tree root.

`rgd compile-spec` creates one deterministic, untracked machine bundle at:

```text
spec/openrgd_unified_spec.json
```

Use `rgd build-standard` to rebuild the strict JSON leaf mirror.

## Canonical integrity

The profile:

```text
OPENRGD_SOURCE_TREE_SHA256_V1
```

commits the path, normalized byte count and SHA-256 digest of every selected modular source file. JSONC comments and formatting are included. Only the manifest's own hash field is replaced with `sha256:SELF` while calculating the root.

```bash
rgd hash          # verify
rgd hash --write  # update manifest after an intentional source change
```

Detailed rules: [`docs/reconciliation/CANONICAL_HASHING.md`](docs/reconciliation/CANONICAL_HASHING.md).

## Source and derived artifacts

```text
spec/                              normative source
        │
        ├── standard/              tracked strict-JSON leaf mirror
        ├── machine bundle         generated on demand, untracked
        └── seed profile           tracked, byte-aligned default scaffold
```

Old recursive domain bundles, unified copies, benchmark snapshots, duplicate UR5 workspaces and checked-in exports were removed from active authority. Their Git identities remain in `docs/history/generated-artifacts/INVENTORY.json`.

The three former external URDF examples were also removed because they were not hermetic, license-audited test fixtures and referenced absent assets or local deployment details. Future examples must satisfy [`docs/reconciliation/EXAMPLES_AND_FIXTURES.md`](docs/reconciliation/EXAMPLES_AND_FIXTURES.md).

## Import, enrichment and export

`rgd import` ingests source-supported evidence. For the reconciled ASCII USD path, it produces a partial Foundation description and does not invent policy.

`rgd alive` is the explicit operation that merges partial imported evidence with the reviewed default profile.

`rgd export` remains experimental static Synapse tooling. Generated output belongs in a caller-selected local directory and is ignored by the canonical repository.

## Cognition-to-body boundary

The convergence-candidate contracts define:

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

These contracts store structured commitments and audit evidence, not private chain-of-thought. HyperAion is a cognitive representation/ranking input, not permission to actuate.

## Validation

```bash
python tools/validate_repository.py
python tools/reconcile_artifacts.py
python tools/validate_canonical_hash.py
python tools/validate_runtime_boundary.py
python contracts/agent/v0.1.0/validate.py
python -m pytest -q
```

GitHub Actions runs the suite on Python 3.10 and 3.12 and builds a Windows executable artifact.

## Documentation

- [`STRUCTURE.md`](STRUCTURE.md) — authority, domains and component boundaries;
- [`LAYOUT.md`](LAYOUT.md) — actual directory map;
- [`GLOSSARIO.md`](GLOSSARIO.md) — terminology;
- [`VERSIONING.md`](VERSIONING.md) — independent version axes;
- [`CLI_GUIDE.md`](CLI_GUIDE.md) — current command behavior;
- [`docs/reconciliation/`](docs/reconciliation/) — reconciliation record;
- [`docs/history/`](docs/history/) — non-normative historical evidence.

## Governance

OpenRGD follows an RFC-oriented process. A file being present in `contracts/` or `docs/reconciliation/` does not make it stable; its maturity label controls its authority.

## Author

**Pasquale Ranieri — Italia Robotica**  
Lead architect and specification author.

OpenRGD is distributed under the MIT License.
