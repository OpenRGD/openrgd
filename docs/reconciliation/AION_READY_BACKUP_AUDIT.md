# AION-ready recovered backup audit

## Verdict

The uploaded backup is **not byte-identical to the archive represented by the historical checksum record**.

```text
Historical expected ZIP SHA-256:
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d

Uploaded backup ZIP SHA-256:
f91ad48cd6a2e8a8bff5f3c559fb8f7fc475e9c4957864aeed6aa689d07615ae
```

The evidence strongly supports that it is a later local backup of the same AION-ready working lineage, but the difference is **not only `.env`** and identity with the historical archive cannot be proved without the original bytes.

## Why the ZIP hash differs

A ZIP digest commits to the complete archive byte stream, including file contents, entry order, timestamps and attributes, compression choices, extra fields and filenames. Even a clean re-compression of the same logical tree can therefore change the ZIP digest.

In this case there are also observable content differences after the historical checksum time.

The checksum record was created at:

```text
2026-08-30T23:03:49Z
2026-08-31 01:03:49 CEST
```

The uploaded backup contains 41 file entries with later archive timestamps:

| Category | Count |
|---|---:|
| Python bytecode/cache | 33 |
| `src/rgd.egg-info/` package metadata | 6 |
| local `.env` | 1 |
| later source file | 1 |

The later source file is:

```text
src/openrgd/main.py
timestamp: 2026-08-31 01:24:44
```

It registers AION/Oracle/plugin commands that are not part of the historical public baseline. This is a substantive source delta, not ZIP metadata.

## Archive integrity

The uploaded ZIP itself is structurally valid:

```text
ZIP integrity: PASS
path traversal check: PASS
symlink check: PASS
total entries: 814
regular files: 654
directory entries: 160
uncompressed regular bytes: 28,634,118
```

## Secret contamination

The backup contains a local `.env` with a non-empty OpenAI API credential.

The credential value and any derivative fingerprint are deliberately absent from this audit.

Verified scope inside the uploaded archive:

```text
exact credential occurrences: 1
location: .env only
```

The repository snapshot itself says that `.env` should not be shipped and that users should copy `.env.example`, which confirms that this is local backup contamination rather than intended source.

Current GitHub evidence:

```text
.env in main tree: no
.env in reconciliation branch tree: no
.env in PR #1 changed paths: no
```

This supports the conclusion that the credential did not enter the current GitHub repository or PR. It does not remove the need to revoke it after exposure in the uploaded backup.

## Content-level commitments

To distinguish archive packaging from logical content, two deterministic inventory commitments were computed from relative path, byte length and file SHA-256:

```text
All regular files except .env
files: 653
bytes: 28,633,834
tree SHA-256:
6288bcd8ef4e14f1518da65cc32e2ed701b61dc298af6f83734d211f7ea944da
```

```text
Source-like tree excluding .env, Python bytecode/cache and egg-info
files: 614
bytes: 28,435,456
tree SHA-256:
1ca51bc0ec5f8c486e5fd078206ee53fad189d99625f088df2017d560f6c46cd
```

These commitments identify the inspected backup variant. They do not prove equality with the unavailable historical ZIP.

## AION evidence found

The backup contains a coherent experimental AION integration:

```text
docs/AION_V0_2.md
spec/00_core/aion_structs.jsonc
spec/00_core/kernel_modules_registry.jsonc
spec/00_core/kernel-modules/...
spec/04_volition/hyper_aion_semantic_map.jsonc
src/openrgd/core/aion.py
src/openrgd/commands/aion.py
tests/test_aion.py
```

Local inspection produced:

```text
pytest: 6 passed
AION structural validation errors: 0
T-512 64-byte roundtrip: PASS
HyperAion 2080-byte roundtrip: PASS
```

The strongest defensible classification is:

```text
IMPLEMENTED:
experimental binary codec, roundtrip tests and structural validator

SPECIFIED:
AION layouts, semantic map and module registry

NOT IMPLEMENTED BY THIS SNAPSHOT:
production microkernel
shared-memory zero-copy transport
real-time scheduler
Chronograf runtime bridge
hardware middleware bridge
```

Several comments overstate implementation maturity—for example deterministic real-time guarantees, isolated processes, zero-copy transport and “100% integrity”. Those claims require hardening before any AION code is proposed upstream.

## Reconciliation decision

This recovered backup does not enter reconciliation PR #1.

Reasons:

1. its archive identity does not match the historical checksum;
2. it contains local secret and generated-file contamination;
3. it contains a source edit after the checksum time;
4. AION codec/spec claims require independent hardening;
5. the current governance already requires recovered excluded evidence to enter through a separate delta PR.

After PR #1 is merged:

```text
main
  ↓
new AION evidence-delta branch
  ↓
sanitized source-only inventory
  ↓
file-by-file comparison
  ↓
codec and claim hardening
  ↓
independent CI
  ↓
separate review
```

No content is promoted merely because it appears in the backup.
