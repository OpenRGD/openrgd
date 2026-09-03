# OpenRGD Release Policy

## 1. Release axes

OpenRGD contains independently versioned artifacts. A release must identify exactly which axis it publishes.

| Axis | Source of truth | Tag prefix |
|---|---|---|
| Standard | `spec/manifest.jsonc` | `standard-v` |
| Python toolchain | `pyproject.toml` | `toolchain-v` |
| Agent contracts | `contracts/agent/<version>/STATUS.json` | `contracts-agent-v` |

New unscoped tags such as `v0.3.0` are prohibited. Existing `v0.1.0` and `v0.1.1` tags remain historical toolchain/repository evidence.

## 2. Tag syntax

Stable releases use:

```text
standard-vMAJOR.MINOR.PATCH
toolchain-vMAJOR.MINOR.PATCH
contracts-agent-vMAJOR.MINOR.PATCH
```

Pre-releases use SemVer pre-release identifiers, for example:

```text
toolchain-v0.2.0-rc.1
contracts-agent-v0.1.0-candidate.1
```

A candidate contract must not receive a stable contract tag.

## 3. Merge is not release

Merging a pull request:

- does not create a tag;
- does not publish a standard version;
- does not promote candidate contracts;
- does not authorize physical execution;
- does not imply that generated CI artifacts are supported releases.

Every release is prepared by a separate release pull request.

## 4. Version behavior

### Standard

The standard version changes only when normative specification semantics change. A source-tree root change alone is not sufficient evidence of a semantic version change; the release PR must classify the change.

### Toolchain

The Python version follows PEP 440 in `pyproject.toml`. The tag uses the equivalent SemVer-style spelling where practical.

The reconciliation branch keeps the historical `0.1.1` value until a dedicated release PR. Because the CLI and artifact behavior changed materially, the next toolchain release candidate should be prepared as:

```text
Python version: 0.2.0rc1
Git tag:        toolchain-v0.2.0-rc.1
```

This policy does not create that release.

### Contracts

Contract package maturity is independent from its version. `contracts/agent/v0.1.0` remains `candidate` and non-normative after merge unless a separate promotion decision changes `STATUS.json`.

## 5. Required release evidence

A release pull request must include:

- exact axis and version;
- changelog and migration notes;
- final source commit;
- all required CI checks on that commit;
- compatibility statement;
- declared source-tree root when the standard/profile is involved;
- artifact inventory and SHA-256 values;
- maturity labels for bundled contracts;
- explicit non-actuation and safety scope where applicable.

## 6. Signing and attestations

The canonical source-tree hash is an integrity commitment, not an authorship signature.

Release candidates may be published with digest-only provenance only when they are clearly labelled `UNSIGNED`.

A stable trust-sensitive release requires:

- a signed tag or signed release commit;
- verifiable provenance for produced artifacts;
- SHA-256 digests;
- disclosure of the signing identity and verification method.

Until that lifecycle is implemented, releases must not claim cryptographic authorship or production-grade supply-chain attestation.

## 7. CI release behavior

All scoped tags may run validation. Only `toolchain-v*` tags may publish the Windows CLI executable from this repository.

Standard and contract tags must not automatically attach a toolchain executable merely because the artifacts share one repository.

## 8. Revocation and supersession

A faulty release is not silently replaced. Publish a new version and document whether the previous release is:

- superseded;
- deprecated;
- withdrawn for security or safety reasons.

Published tags must not be force-moved.
