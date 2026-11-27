# CORE-CAL-01A — Source Integrity Assessment & Verifier Boundary

**2026-11-27 · candidate · non-normative · read-only.** Responds to [CAL-021-C handoff](https://github.com/OpenRGD/rgd-calibration/blob/646dbc05bcefd15942b25bb55b3c99096f0cccc9/docs/handoffs/CAL-021-C-TO-CORE.md) / [CAL #9](https://github.com/OpenRGD/rgd-calibration/pull/9), now merged. Independent of EXT-01B.3D and the existing registry, EVOL, RI and COG candidates.

## Exact ownership and compatibility

Baseline Core `afe1a831b950a4e6560f0285a0103fc4eaa343b7`, toolchain distribution `rgd 0.1.1`. Use the actual `openrgd.core.canonical.compute_integrity(spec_dir)` and its returned index. Existing `rgd hash <project-or-spec> --output json` exposes only the summary; do not use --write for verification. `rgd check` / inspect_profile are the existing kernel-selected loading checks, not full schema or semantic validation. The master rgd_schema.jsonc is a meta-schema. No change to these tools or their outputs. No change to V1 source selection, index serialization or normalization, canonical.py, utils.py, spec, strict mirror, seed, model identity, profile bindings, runtime or installer.

This opt-in assessment uses the exact four Core source blob pins also used by CAL-021-B, checking the local Python module files before use. This is version-consistency evidence within a trusted Python runtime, not an installed-code attestation, signature, source-commit proof, import sandbox or proof against a concurrent modification. Core still owns V1; no alternative root algorithm. The candidate has its own independent version. The historical V1 accepts certain ambiguous inputs; this **separate stricter assessment may reject them** without assigning a new root. A different preimage/normalization or new grammar requires explicit versioned migration and vectors, not a silent V1 rewrite.

## Independent observations

| Field | Exact scope |
|---|---|
| input_status | Private bounded snapshot created, unavailable, or rejected |
| manifest_status | Conservative strict manifest preflight, not a full manifest schema |
| integrity_status | Actual Core V1 root matches / mismatches, not assessed, or verification failed |
| source_index | Exact V1 index as returned by compute_integrity; null if not computed |
| raw_file_commitments | Exact raw bytes and size of each indexed file from same private snapshot; manifest is NOT normalized here |
| indexed_jsonc_syntax_status | Each indexed JSONC document parsed as an object using conservative JSONC subset and legacy parser agreement; does not validate field schemas |
| required_paths_status | Presence relative to **externally selected** versioned path requirements, or missing/version mismatch/not assessed |
| remaining authority flags | Always false: schema, semantic consistency, kernel selection, publisher, robot binding, CAL model hash binding, physical certification, actuation and grants |

No combined "VALID" or complete-robot claim. MATCH can coexist with syntax FAIL and missing required paths. MISMATCH can coexist with paths present; it must not imply authentic contents. Profile selection is an explicit trusted consumer policy input, not proof of governance approval; its exact raw SHA-256 is reported. No policy inferred from manifest, domain lists or kernel selection. The BHL genesis fixture contains the 76 paths from the exact baseline source tree: it is **only a reference fixture for inventory**, not universal mandatory files or normative completeness. Different robots may use different requirements. Presence doesn't validate content, role coverage, optional modules, or cross-file references. The declared standard version must match the selected profile. No schema/semantic assessment in this increment.

## Syntax / manifest admission

UTF-8 JSON objects, // and /* */ comments treated as whitespace with preserved line breaks, correct escape parity, strict JSON, duplicate decoded keys rejected at every level, finite numbers, no unpaired surrogate strings, no trailing commas, no raw control characters inside strings, no unterminated block comments. Compare semantic parse to the existing V1 parser for all indexed JSONC; reject disagreement rather than repair. For manifest, require one literal occurrence each of integrity_hash_str and integrity_profile_str, one decoded key each in the entire object, actual meta_group fields and the pinned V1 literal regex matching those exact uncommented values. Conservative rejection even for a duplicate literal in a comment (as in CAL); no escaped-key rewrite, nested decoy or alternative profile. This is a subset, not a new accepted JSONC grammar. The existing V1 normalizer is unchanged. Unknown profile => no substituted hash. If manifest preflight cannot establish the exact interpretation, no root/index reported. If another indexed document has invalid syntax, root calculation remains independent. Never rehash or mutate a supplied source.

## API / CLI candidate

Use a trusted checkout and trusted interpreter with the pinned Core dependencies. Run from this repository (not an installed stable command):
```bash
PYTHONPATH=src python contracts/source-assessment/v0.1.0/assessment.py --bundle /path/to/rgd-project
PYTHONPATH=src python contracts/source-assessment/v0.1.0/assessment.py --bundle /path/to/rgd-project --required-profile contracts/source-assessment/v0.1.0/fixtures/bhl-genesis-required-paths.json
```
Python `assess_source(bundle, required_profile_raw=None)` returns a structured record. CLI stdout JSON only; exit 0 iff integrity MATCH, indexed syntax PASS, and if a profile was supplied REQUIRED_PATHS_PRESENT. Exit 2 for a completed negative or invalid policy; argument errors also exit 2. No exit code establishes complete model validity. Invalid external policy rejected before assessment (no report). No network, source writes, CAL invocation, source repairs or hardware. Bound entries (256), raw files (4MiB each), total copied bytes (16MiB), depth/node limits and bounded portable path names; refuse symlinks/special files/ambiguous paths. Requires a stable operator-controlled tree and trusted parents/temp directory, not protection against a hostile concurrent filesystem. Only copy to private temporary storage. Standard mirror alone is not source. Excluded generated files do not enter the V1 index.

## Consumers / evidence

CAL may independently compare its passive report role/path/raw digest to these exact raw commitments and V1 index for the same stable snapshot; no automatic assignment of model_sha256 or reseal. The raw manifest digest differs from its normalized V1 entry. ZIP, release, executable, report stdout, raw file and source-tree hashes are distinct. CAL-021-D consumer/Registry version migration remains independent. The new API is an opt-in prototype; no production Console route, no package installation or changes to CAL. For the cross-repo test the actual CAL wrapper and Rust binary run on a controlled identical fixture (separate private copies); this is compatibility evidence, not runtime same-snapshot integration. Future composition must bind both to one private snapshot.

## Follow-ups

CORE-CAL-01B: independently selected completeness profile, strict field/schema and reference validation, kernel selection scope, accepted grammar/migration and tests. CORE-CAL-01C: review existing joint and sensor references, path and empty-digest placeholders, MAJOR calibration_validity policy conflict. No implicit aliases or normative safety changes here. EXT-01B.3D source/build provenance and existing shared manager plan remain active; model source digest is not software artifact provenance. No merge/deploy/automatic promotion.
