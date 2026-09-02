# OpenRGD Versioning Model

OpenRGD is a repository containing several independently versioned artifacts. A version from one layer MUST NOT be silently projected onto another layer.

## Current version axes

| Axis | Source of truth | Current value | Meaning |
|---|---|---:|---|
| Standard bundle | `spec/manifest.jsonc` | `0.2.0` | Version targeted by the reference OpenRGD bundle |
| Kernel profile | `spec/00_core/kernel.jsonc` | `0.1.0` | Version of that kernel profile, not of the whole standard |
| Python distribution | `pyproject.toml` | `0.1.1` | Version of the installable `rgd` toolchain |
| Agent contracts | `contracts/agent/v0.1.0/` | `0.1.0` | Version of a convergence-candidate interface package |

## Rules

1. The standard version describes the data model and normative bundle.
2. The toolchain version describes Python code and packaging.
3. A profile or contract version describes only that profile or contract.
4. Compatibility MUST be declared explicitly; matching numbers are not sufficient evidence of compatibility.
5. A Git tag MUST NOT be interpreted as a standard release unless its scope is explicit in the release notes.
6. Candidate contracts do not become stable merely because the repository or CLI is released.

## Historical tags

The existing unscoped tags `v0.1.0` and `v0.1.1` belong to the public repository/toolchain lineage. They do not establish that the OpenRGD standard bundle is version `0.1.1`; the bundle itself declares `0.2.0`.

## Future release naming

Scoped tags are recommended for future releases, for example:

```text
standard-v0.2.0
toolchain-v0.1.2
contracts-agent-v0.1.0
```

This naming recommendation is not yet a frozen governance rule. It should be confirmed before the next public release.
