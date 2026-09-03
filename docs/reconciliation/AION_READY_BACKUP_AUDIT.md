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
| other | 0 |

The later source file is:

```text
src/openrgd/main.py
timestamp: 2026-08-31 01:24:44
```

It registers AION, Oracle and plugin command groups that are not part of the historical public baseline. This is a substantive source delta, not ZIP metadata.

## Archive integrity

The uploaded ZIP itself is structurally valid:

```text
ZIP integrity: PASS
path traversal check: PASS
symlink check: PASS
embedded .git metadata: none
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
.env.example real credential: no
```

The backup's `.gitignore` already excludes `.env`, and its own reconciliation note says that `.env` should not be shipped. This supports classification as local backup contamination rather than intended source.

Current GitHub evidence:

```text
.env in main tree: no
.env in reconciliation branch tree: no
.env in PR #1 changed paths: no
```

Therefore **no evidence was found that this credential entered the current GitHub repository or PR**. That is not a proof about every external cache or historical copy, and the exposed credential still requires revocation.

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

## Local contamination inventory

| Category | Files |
|---|---:|
| `.env` | 1 |
| Python bytecode/cache | 33 |
| `egg-info` metadata | 6 |
| generated robot workspaces | 227 |
| generated exports | 4 |
| historical external examples | 5 |
| incomplete MSIX material | 1 |

These items must not be imported into a future evidence-delta branch.

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
Python: 3.13.5
full snapshot pytest: 6 passed
AION test module: 3 passed
AION structural validation errors: 0
T-512 64-byte roundtrip: PASS
HyperAion 2080-byte roundtrip: PASS
```

The strongest defensible classification is:

```text
IMPLEMENTED:
experimental binary codec, roundtrip tests,
semantic-dimension lookup and limited structural validator

SPECIFIED:
AION layouts, 512D semantic map and module registry

NOT IMPLEMENTED BY THIS SNAPSHOT:
production microkernel
shared-memory zero-copy transport
real-time scheduler or latency enforcement
process/kernel-space isolation
dynamic priority runtime
semantic engine for unmapped hard invariants
Chronograf runtime bridge
hardware middleware bridge
text/vision/VLA → HyperAion encoder
HyperAion → ActionIntent / somatic translation
```

Aion4096 is specified in JSONC but has no corresponding codec or roundtrip test in the recovered Python module.

## Hardening findings

### AION-H-001 — Non-finite and out-of-range HyperAion values

`pack_hyper_aion` accepts:

```text
NaN
+Infinity
-Infinity
values outside [-1, 1]
```

even though the semantic map declares normalized `FLOAT32_NORMALIZED_MINUS_ONE_TO_ONE` values.

Future action: reject non-finite values and decide explicitly whether range enforcement belongs to the codec profile or semantic validation layer.

### AION-H-002 — Lossy uint64 coercion

Header and payload fields pass through `int(value)`. The current implementation therefore accepts and converts values such as:

```text
1.5  → 1
True → 1
"7"  → 7
```

Future action: require a real integer type, decide boolean handling and reject lossy coercion.

### AION-H-003 — Incomplete semantic-map validation

The validator still reports success after removing one of the core dimensions and changing the reserved-dimension count to an inconsistent value.

Future action: require the complete 0–7 octant, validate exact indices, reserved range, numeric profile and all source references.

### AION-H-004 — Invalid hard-invariant mappings fail open

Malformed threshold expressions, absent mappings and out-of-range dimension indices are silently skipped by `evaluate_alignment_vector`.

Future action: validate the mapping configuration separately and fail closed for mapped hard-invariant errors.

### AION-H-005 — Semantic-first authority is not implemented

The executable evaluator checks only explicitly vector-mapped thresholds. It does not implement the documented semantic hard invariants that lack vector mappings.

Future action: keep this evaluator non-authoritative until it sits behind the deterministic constitutional and Operation Safety contracts.

### AION-H-006 — “100% integrity” overclaim

`rgd aion check` reports:

```text
AION integrity: 100%
```

after a limited structural validation.

Future action: report an exact validation profile and checks performed, not a readiness percentage.

### AION-H-007 — Runtime claims without runtime evidence

The module registry declares shared-memory zero-copy IPC, process isolation, dynamic priorities, kernel-space isolation and microsecond latency budgets. The recovered code does not implement or measure these properties.

Future action: classify them as requirements or proposals until a runtime and benchmark evidence exist.

### AION-H-008 — Direct HyperAion-to-actuation conflicts with convergence

The recovered Work kernel describes translation from HyperAion directly to low-level actuation commands. That conflicts with the converged boundary:

```text
ActionIntent
→ Somatic Translator
→ CapabilityPlan
→ Operation Safety Gate
→ Body Adapter
```

Future action: do not import the module architecture wholesale; resolve it through a contract delta.

### AION-H-009 — Anchor semantics conflict

One source calls `anchor:uint64` a Chronograf timestamp; another calls it an opaque clock/causal anchor.

Future action: align the future profile with `ChronografAnchorRef64` and never treat its handle as a timestamp.

### AION-H-010 — Packet type/header consistency is unverified

The codec does not prove that `meta_data` type identifiers match the selected packet layout.

Future action: define the type-ID encoding and add incompatible-header/layout tests.

## Reconciliation decision

This recovered backup does not enter reconciliation PR #1.

Reasons:

1. its archive identity does not match the historical checksum;
2. it contains local secret and generated-file contamination;
3. it contains a source edit after the checksum time;
4. AION validation and maturity claims require independent hardening;
5. some module semantics conflict with the converged embodied boundary;
6. the current governance requires recovered excluded evidence to enter through a separate delta PR.

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
AION-H-001 ... AION-H-010 resolution/defer record
  ↓
independent CI
  ↓
separate review
```

No content is promoted merely because it appears in the backup.
