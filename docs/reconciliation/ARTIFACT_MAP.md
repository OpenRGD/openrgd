# Canonical artifact map

## Authority

| Artifact | Repository path | Authority | Comparison rule |
|---|---|---|---|
| Human-readable standard | `spec/` | Normative source | Authored JSONC and selected static files |
| Strict compatibility mirror | `standard/` | Derived | Parsed JSON equivalence with `spec/` |
| Packaged default runtime profile | `src/openrgd/seeds/default/spec/` | Derived runtime seed | Byte-identical with selected `spec/` files unless an approved override is hash-pinned |
| Domain and unified bundles | root `*_spec.*`, `openrgd_unified_spec.*`, `standard/benchmarks/` | Generated | Outside the leaf-mirror contract until the aggregate generator is reconciled separately |

The machine-readable policy is `ARTIFACT_POLICY.json`.

## Reconciliation performed on 2026-09-02

### Missing default-seed material

The following normative Agency material existed under `spec/` but was absent from the packaged seed and has now been mirrored byte-for-byte:

- `03_agency/extension_permissions_policy.jsonc`
- `03_agency/installed_skill_packages.jsonc`
- `03_agency/skills_library.jsonc`
- `03_agency/skills/index.jsonc`
- four core skill definitions
- two core skill schemas

**Classification before repair:** IMPLEMENTATION DIVERGENCE / STALE DERIVED COPY.  
**Classification after repair:** DERIVED MIRROR, VERIFIED BY CI.

### Stale default-seed copies

| Path | Seed evidence | Canonical evidence | Decision |
|---|---|---|---|
| `00_core/kernel.jsonc` | header labelled the same kernel body as `v0.2` | normative source labels the kernel profile `v0.1`; body metadata remains `0.1.0` and targets standard `0.2.0` | replace seed copy with canonical bytes |
| `01_foundation/actuation_topology.jsonc` | topology `1.1.0`, limited joint map | topology `1.4.0`, reusable control profiles and expanded joint mapping | classify seed copy as SUPERSEDED and replace |
| `01_foundation/surface_properties.jsonc` | profile `1.0.0`, legacy `surface_map` | profile `1.2.0`, material catalog, link bindings and domain-randomization policy | classify seed copy as SUPERSEDED and replace |

No evidence supported treating these three files as intentional runtime-profile overrides.

### Legacy and generated files removed from the active seed

- `03_agency/skills_library.json` was a separate two-entry legacy index. Its original bytes and Git blob identity are preserved under `docs/history/seed/03_agency/skills_library.legacy.json`.
- `openrgd_unified_spec.json` and `openrgd_unified_spec.jsonc` were generated aggregate outputs. They were removed from the seed so a newly initialized profile starts from source modules rather than stale compiled products.

## Override governance

The active default seed currently has **zero approved overrides**.

A future intentional difference is allowed only when `ARTIFACT_POLICY.json` declares all of:

1. relative path;
2. classification `RUNTIME_PROFILE_OVERRIDE`;
3. semantic reason;
4. decision or governance reference;
5. SHA-256 of the canonical source;
6. SHA-256 of the seed override.

Changing either side invalidates the approval until the policy is reviewed and updated. This prevents runtime-specific values from becoming silent forks of the standard.

## Reconciliation command

Check without mutation:

```bash
python tools/reconcile_artifacts.py
```

Regenerate leaf mirrors:

```bash
python tools/reconcile_artifacts.py --write
```

Prune undeclared files from the active default-seed namespace only after historical material has been archived:

```bash
python tools/reconcile_artifacts.py --write --prune-seed
```

The command deliberately does not regenerate or normalize domain/unified aggregate bundles. Those remain a separately auditable convergence step.
