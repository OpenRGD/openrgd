# OpenRGD Release Policy

OpenRGD versions its public artifacts independently:

| Axis | Source | Tag prefix |
|---|---|---|
| Standard | `spec/manifest.jsonc` | `standard-v` |
| Python toolchain | `pyproject.toml` | `toolchain-v` |
| Agent contracts | `contracts/agent/<version>/STATUS.json` | `contracts-agent-v` |

Existing historical `v0.1.0` and `v0.1.1` tags remain untouched. New releases use the scoped prefixes above.

## A merge is not a release

Merging work into `main` does not automatically publish a new standard or toolchain version. Releases are deliberate, reviewed events.

## What a release should include

- the version being released;
- a clear changelog;
- green CI on the release commit;
- compatibility/migration notes when behavior changes;
- hashes for distributed artifacts;
- maturity labels for experimental/candidate material.

The canonical source-tree SHA-256 proves content identity. Signing and provenance attestations are separate capabilities and must only be claimed when actually implemented.
