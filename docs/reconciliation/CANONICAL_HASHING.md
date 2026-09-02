# Canonical hashing and generated artifacts

## Status

**Decision status:** adopted on the reconciliation branch, pending review and merge.  
**Profile:** `OPENRGD_SOURCE_TREE_SHA256_V1`  
**Digest:** SHA-256

## Authority boundary

```text
spec/ modular JSONC + MANIFESTO.md
              │
              ├── canonical source-tree hash
              ├── strict JSON mirror in standard/
              └── deterministic machine bundle on demand
```

Generated domain bundles, unified JSONC copies and benchmark snapshots are not source and are not tracked.

## Canonical source set

The profile commits, in lexicographic POSIX-path order:

1. every modular `*.jsonc` file under `spec/`;
2. `spec/MANIFESTO.md` when present;
3. excluding the reserved generated top-level names:
   - `01_spec.jsonc` through `06_spec.jsonc`;
   - `openrgd_unified_spec.jsonc`;
   - `openrgd_unified_spec_document.jsonc`.

Symlinks are rejected.

## File commitments

For every selected path the source index stores:

```json
{
  "media_type": "application/jsonc",
  "path": "01_foundation/description.jsonc",
  "sha256": "<64 lowercase hex characters>",
  "size_bytes": 1234
}
```

JSONC files are hashed as their exact UTF-8 source bytes. Comments, spelling and formatting are therefore committed. `.gitattributes` fixes tracked text files to LF line endings.

## Manifest self-reference

`spec/manifest.jsonc` stores the resulting root in `meta_group.integrity_hash_str`. To avoid a recursive hash equation, exactly that field is normalized to:

```text
sha256:SELF
```

before the manifest file digest is calculated. Every other manifest byte, including `integrity_profile_str`, remains committed.

## Root preimage

The path-sorted file entries are wrapped in:

```json
{
  "files": [],
  "hash_algorithm": "SHA-256",
  "manifest_self_value": "sha256:SELF",
  "profile": "OPENRGD_SOURCE_TREE_SHA256_V1",
  "source_root": "spec"
}
```

This index is serialized as UTF-8 canonical JSON with:

```text
sort_keys = true
separators = (",", ":")
allow_nan = false
ensure_ascii = false
```

The canonical bundle root is:

```text
sha256( canonical_index_bytes )
```

and is stored as lowercase `sha256:<hex>`.

## Commands

Verify without mutation:

```bash
rgd hash
```

Write or refresh the manifest commitment:

```bash
rgd hash --write
```

Build the strict JSON leaf mirror:

```bash
rgd build-standard
```

Build one deterministic machine bundle:

```bash
rgd compile-spec
```

Default generated output:

```text
spec/openrgd_unified_spec.json
```

This output is ignored by Git and can be regenerated. It contains no wall-clock generation timestamp.

## Scope limits

The root commits only the OpenRGD standard/profile source tree under `spec/`. It does not commit:

- implementation code;
- Agent Contracts, which have an independent version axis;
- external runtime repositories;
- generated exports;
- local robot workspaces;
- signatures or release attestations.

Cryptographic signing remains a separate release-hardening decision. SHA-256 integrity does not by itself establish authorship, approval or moral correctness.
