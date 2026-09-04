# OpenRGD Versioning Model

OpenRGD versions different artifacts independently. Matching version numbers are never assumed to imply compatibility.

| Axis | Source of truth | Current value |
|---|---|---:|
| Standard bundle | `spec/manifest.jsonc` | `0.2.0` |
| Kernel profile | `spec/00_core/kernel.jsonc` | `0.1.0` |
| Python toolchain | `pyproject.toml` | `0.1.1` |
| Agent contracts | `contracts/agent/v0.1.0/STATUS.json` | `0.1.0 candidate` |

## Tag namespaces

```text
standard-vMAJOR.MINOR.PATCH
toolchain-vMAJOR.MINOR.PATCH
contracts-agent-vMAJOR.MINOR.PATCH
```

Historical unscoped `v0.1.0` and `v0.1.1` tags remain untouched.

## Rules

1. Standard versions describe normative data semantics.
2. Toolchain versions describe installable code and packaging.
3. Profile and contract versions describe only that profile or contract.
4. Candidate material remains candidate until explicitly promoted.
5. A merge is not automatically a release.
6. A source-tree hash identifies content; it does not choose the semantic version for us.

See `RELEASE_POLICY.md` for publication rules.
