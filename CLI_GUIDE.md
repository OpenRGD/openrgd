# OpenRGD CLI guide

The `rgd` CLI manages OpenRGD specification profiles and derived tooling artifacts. The canonical package is non-actuating.

## Install

```bash
python -m pip install -e .
rgd --help
```

## Core lifecycle

### `rgd init NAME`

Creates a project from the packaged default profile:

```bash
rgd init my_robot
```

The command:

1. copies the reconciled modular seed;
2. assigns `did:rgd:my_robot`-style identity;
3. recalculates `spec/manifest.jsonc` using `OPENRGD_SOURCE_TREE_SHA256_V1`;
4. fails atomically if personalization or hashing fails.

### `rgd hash`

Verifies the declared canonical source root:

```bash
rgd hash
rgd hash --output json
```

After an intentional source edit:

```bash
rgd hash --write
```

A mismatch exits non-zero.

### `rgd check`

Checks kernel references and JSONC loading:

```bash
rgd check
rgd check spec/00_core/kernel.jsonc
```

Canonical source-tree integrity is a separate explicit check through `rgd hash`.

### `rgd boot`

Loads the project through the kernel and emits the current grounding/system-prompt representation:

```bash
rgd boot
rgd boot --output json
```

This command does not actuate hardware.

## Derived artifacts

### `rgd build-standard`

Rebuilds the strict JSON leaf mirror from the selected canonical source files:

```bash
rgd build-standard
rgd build-standard --src ./Robot --dest ./Robot/standard
```

The destination is replaced deterministically. It cannot be the source tree or an ancestor/descendant that would delete the source.

### `rgd compile-spec`

Creates one deterministic machine bundle:

```bash
rgd compile-spec
rgd compile-spec --out ./artifacts/robot.json
rgd compile-spec --output json
```

Default output:

```text
spec/openrgd_unified_spec.json
```

The output contains the source-tree root and source index. It has no generation timestamp and is ignored by Git.

The former `--domain` and `--full-definition` modes were removed because their generator could recursively ingest previously generated bundles and stored volatile benchmark copies.

## Import and profile enrichment

### `rgd import`

Imports source-supported facts into a partial OpenRGD specification:

```bash
rgd import robot.usda --out ./partial-rgd
```

The reconciled ASCII USD path writes under exactly one `spec/` root and emits only Foundation evidence. It does not create safety or alignment policy.

### `rgd alive`

Merges partial imported evidence with the reviewed default profile:

```bash
rgd alive robot.usda --out ./my-robots/RGD-robot
```

Generated robot workspaces are local artifacts and are ignored by this repository.

The URDF importer lineage remains under reconciliation and must not be treated as a normative full-profile generator.

## Static interoperability export

```bash
rgd export ros2 --out ./export
rgd export isaac --out ./export
```

Synapse output is generated, non-normative and untracked. It is not a physical runtime path.

## Runtime compatibility boundary

```bash
rgd run status
rgd run status --output json
```

The historical commands:

```bash
rgd run ros2
rgd run viam
rgd run hybrid
```

fail closed with a blocked result and exit code `2`. The embodied runtime belongs in an independent implementation repository.

## Automation

Use `--quiet` for machine-readable or CI operation:

```bash
rgd --quiet hash --output json
rgd --quiet compile-spec --output json
```

Use `--verbose` for additional toolchain diagnostics.
