# Static profile inspection and grounding

## Status

**Decision status:** implemented on the reconciliation branch, pending review and merge.  
**Execution status:** non-actuating.  
**Implementation:** `src/openrgd/core/profile.py`.

## Purpose

OpenRGD needs to distinguish three different claims:

```text
content identity
structural readability
physical/runtime readiness
```

They are not equivalent.

| Operation | What it establishes | What it does not establish |
|---|---|---|
| `rgd hash` | selected source files match the declared canonical root | that kernel references are usable or body assumptions are valid |
| `rgd check` | source root matches and every kernel-selected module is safely located and readable as a JSON object | hardware compatibility, operational safety or runtime readiness |
| `rgd boot` | deterministic grounding context can be assembled from the inspected profile | physical safety, runtime initialization or actuation authority |

## Shared inspector

`check` and `boot` use one shared profile inspector. It requires:

1. kernel path exactly under `spec/00_core/kernel.jsonc`;
2. matching `OPENRGD_SOURCE_TREE_SHA256_V1` declaration;
3. kernel root and every selected module to be JSON objects;
4. non-empty kernel identity;
5. non-empty module-loading list;
6. relative POSIX-style JSONC references;
7. no absolute path, parent traversal, nested `spec/` prefix or duplicate reference;
8. every selected module to exist;
9. no non-finite JSON values.

Any failure returns non-zero. Partial success and warning-only module omission are not allowed.

## `OPENRGD_PROFILE_VALIDATION`

`rgd check --output json` returns a deterministic artifact containing:

```text
artifact_type
status
robot_id
kernel_ref
integrity
modules[]
modules_count
physical_execution_assessed = false
runtime_readiness = NOT_ASSESSED
```

Each module record commits its canonical relative path, exact byte count and SHA-256.

## `OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT`

`rgd boot --output json` returns:

```text
artifact_type
robot_id
integrity
module_loading_order[]
modules{}
summary
physical_execution
```

The summary may expose deterministic, source-derived views such as:

- described joint identifiers/types/limits;
- active alignment profile identifier;
- declared hard-invariant count.

It does not produce hidden reasoning, motor commands or a physical action plan.

Mandatory physical-execution state:

```text
assessed = false
authorized = false
status = NOT_AUTHORIZED_BY_BOOT
```

## Naming compatibility

The historical command name `boot` is retained for CLI continuity. Its current semantics are explicitly **grounding-only**.

A future embodied-runtime startup command belongs to the independently reconciled runtime repository and must not inherit authority from this command name.

## Determinism

Given the same integrity-verified profile, JSON validation and grounding output must be byte-stable across repeated invocations in the same toolchain version.

No wall-clock timestamp, random identifier or host path is included.

## Security boundary

The inspector prevents module-path traversal and does not import or execute module code. JSONC module content remains data.

This is not a complete adversarial content policy, schema validation for every domain or proof that a module's semantic claims are true. Those remain separate validation layers.
