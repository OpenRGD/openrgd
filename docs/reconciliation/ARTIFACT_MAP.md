# Canonical artifact map

## Authority

| Artifact | Path | Authority | Validation |
|---|---|---|---|
| Human-readable standard | `spec/` | Normative source | Source-tree root and JSONC parsing |
| Strict compatibility mirror | `standard/` | Derived and tracked | Parsed JSON equivalence with selected `spec/` leaves |
| Packaged default profile | `src/openrgd/seeds/default/spec/` | Derived and tracked | Byte-identical with selected sources unless an approved override is hash-pinned |
| Machine bundle | `spec/openrgd_unified_spec.json` by default | Generated and untracked | Deterministic output bound to the declared source root |
| Interoperability exports | commonly `export/` | Generated and untracked | Exporter-owned evidence, not standard source |
| Robot workspaces | commonly `RGD-*` or `my-robots/` | Generated and untracked | Local implementation artifacts |

Rules are machine-readable in [`ARTIFACT_POLICY.json`](ARTIFACT_POLICY.json). Hashing is specified in [`CANONICAL_HASHING.md`](CANONICAL_HASHING.md).

## Canonical closure

The repository selects 76 source artifacts: modular JSONC under `spec/` plus `spec/MANIFESTO.md`, excluding generated domain and unified names.

CI requires:

```text
STANDARD: 76 expected, 0 missing, 0 mismatched, 0 unexpected
DEFAULT SEED: 76 expected, 0 missing, 0 mismatched,
0 approved overrides, 0 unexpected
```

## Canonical hashing

`meta_group.integrity_profile_str` declares:

```text
OPENRGD_SOURCE_TREE_SHA256_V1
```

The root commits each selected relative path, normalized byte count and SHA-256 file digest. Only `integrity_hash_str` in the manifest is replaced with `sha256:SELF` while calculating the root.

```bash
rgd hash
rgd hash --write
```

## Removed generated material

The active tree no longer contains:

- recursive domain bundles `01_spec` through `06_spec`;
- recursive or volatile unified JSON/JSONC bundles;
- strict-JSON domain bundles and benchmark duplicates;
- duplicate generated UR5 profiles;
- checked-in ROS 2 and Isaac export outputs;
- unverified non-hermetic external URDF examples;
- the incomplete MSIX placeholder;
- competing bundle generators and the parallel legacy CLI.

Original paths and Git tree/blob identities are retained in:

```text
docs/history/generated-artifacts/INVENTORY.json
```

## Commands

```bash
python tools/reconcile_artifacts.py
python tools/validate_canonical_hash.py
rgd build-standard
rgd compile-spec
```
