# Historical import/export prototype lineage

This directory records source identities for importer and static-export implementations superseded during the 2026 reconciliation. The bytes remain recoverable through Git history and are not duplicated here.

| Historical path | Git blob | Classification | Finding |
|---|---|---|---|
| `src/openrgd/importers/base.py` | `8ad64558ce53aef5f06a5cc25096b5b016c2d2a4` | SUPERSEDED BASE CONTRACT | no content-addressed provenance or safe declared-name normalization |
| `src/openrgd/importers/urdf/parser.py` | `44e34adca19203226a3737c6ac0ef61632cd51d7` | SUPERSEDED IMPORTER | invented kernel and default alignment; silently substituted physical defaults |
| `src/openrgd/commands/synapse.py` | `3fb3b139aff973d5f6f8e1611f1a095930676a00` | BROKEN COMMAND BOUNDARY | constructed Synapse classes with arguments incompatible with the active base class |
| `src/openrgd/synapses/base.py` | `03d7c989a3bd94ef7fb823e527458ff678501fd3` | SUPERSEDED BASE CONTRACT | no source-root or machine-bundle verification |
| `src/openrgd/synapses/ros2/generator.py` | `2f43d40a66e6dc2fed2a462be8d137d097f4cd68` | SUPERSEDED STATIC GENERATOR | used fallback driver/address values, lacked deterministic manifest and could fail without a non-zero result |
| `src/openrgd/synapses/isaac/generator.py` | `a3478b83f1a580a93c640b9c3437d69f5a5e2072` | PLACEHOLDER, NOT IMPLEMENTATION | contained comments promising omitted logic and generated no artifact |

The reconciled active boundary is evidence-first and fail-closed:

```text
source description
→ partial Foundation evidence
→ explicit seed enrichment
→ canonical source-tree hash
→ deterministic machine bundle
→ static export with explicit completeness status
```

No historical file in this lineage is evidence of a complete physical runtime or Body Adapter.
