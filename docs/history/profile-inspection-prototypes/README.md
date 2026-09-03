# Historical profile-inspection prototype lineage

This directory records the identities and disposition of the original `check` and `boot` commands. Their bytes remain recoverable from Git history and are not duplicated here.

| Historical path | Git blob | Classification | Finding |
|---|---|---|---|
| `src/openrgd/commands/check.py` | `10693e291b2a7505f91700f7681c17c8a42c90e9` | SUPERSEDED STRUCTURAL CHECK | tested mostly for referenced path existence, did not verify the canonical source-tree root or parse every selected module, and concluded with runtime-like “I am ready” language |
| `src/openrgd/commands/boot.py` | `9567ba51797d58d278c858e94744d64ad90f8f05` | SUPERSEDED GROUNDING COMMAND | swallowed module-loading failures as warnings, did not verify source integrity, built a partial ad-hoc prompt and used “boot”/“grounding complete” language without a runtime or actuation boundary |

The reconciled boundary is:

```text
OPENRGD_SOURCE_TREE_SHA256_V1
              ↓
canonical kernel path
              ↓
safe, unique module references
              ↓
module existence + JSONC object validation
              ↓
OPENRGD_PROFILE_VALIDATION
              ↓
OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT
```

`rgd check` does not assess hardware or runtime readiness.

`rgd boot` does not initialize an embodied runtime, evaluate the Operation Safety Gate or authorize physical execution.
