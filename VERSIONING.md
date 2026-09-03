# OpenRGD Versioning Model

OpenRGD contains independently versioned artifacts. A version from one layer MUST NOT be silently projected onto another layer.

## Current version axes

| Axis | Source of truth | Current value | Meaning |
|---|---|---:|---|
| Standard bundle | `spec/manifest.jsonc` | `0.2.0` | Version targeted by the reference OpenRGD bundle |
| Kernel profile | `spec/00_core/kernel.jsonc` | `0.1.0` | Version of that kernel profile, not of the whole standard |
| Python distribution | `pyproject.toml` | `0.1.1` | Version of the installable `rgd` toolchain |
| Agent contracts | `contracts/agent/v0.1.0/STATUS.json` | `0.1.0 candidate` | Non-normative convergence-candidate package |

## Rules

1. The standard version describes the data model and normative bundle.
2. The toolchain version describes Python code and packaging.
3. A profile or contract version describes only that profile or contract.
4. Compatibility MUST be declared explicitly; matching numbers are not sufficient evidence.
5. Merge is not release.
6. Candidate contracts do not become accepted merely because the repository or CLI is released.
7. A source-tree root change does not, by itself, determine the semantic version increment.
8. New unscoped tags are prohibited.

## Historical tags

The existing unscoped tags:

```text
v0.1.0
v0.1.1
```

belong to the public repository/toolchain lineage. They do not establish that the OpenRGD standard bundle is version `0.1.1`; the bundle itself declares `0.2.0`.

They remain historical and must not be moved or reused.

## Frozen scoped tag names

Future tags use one of these prefixes:

```text
standard-vMAJOR.MINOR.PATCH
toolchain-vMAJOR.MINOR.PATCH
contracts-agent-vMAJOR.MINOR.PATCH
```

Pre-release identifiers follow SemVer-style syntax, for example:

```text
toolchain-v0.2.0-rc.1
contracts-agent-v0.1.0-candidate.1
```

A candidate contract cannot receive a stable contract tag.

## Toolchain release preparation

The reconciliation branch intentionally retains Python distribution version `0.1.1` until a separate release pull request.

Because the CLI behavior and artifact boundaries changed materially, the next proposed toolchain release candidate is:

```text
pyproject version: 0.2.0rc1
Git tag:           toolchain-v0.2.0-rc.1
```

This is a release-plan decision, not a release performed by the reconciliation merge.

## Standard release behavior

A `standard-v*` tag may be created only by an explicit standard release pull request that identifies:

- normative semantic changes;
- canonical source-tree root;
- compatibility and migration impact;
- maturity of every bundled domain and contract.

## Contract release behavior

Contract maturity remains independent from version. The current `agent/v0.1.0` package remains `candidate` and non-normative. Promotion requires the process in `GOVERNANCE.md` and a machine-readable status update.

See `RELEASE_POLICY.md` for artifact, signing and publication rules.
