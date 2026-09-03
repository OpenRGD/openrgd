# Reconciliation PR #1 — Merge Readiness

## Status

```text
technical review readiness:   YES
governance tree freeze:       COMPLETE AND CI-VALIDATED
repository hygiene:           COMPLETE AND CI-VALIDATED
external branch protection:   OPEN — ISSUE #2
pull-request state:            DRAFT
merge authorization:          NO
release authorization:        NO
```

This document records the decisions required to move the reconciliation from draft implementation to an auditable merge candidate.

## Frozen decisions

| Decision | Freeze result |
|---|---|
| Canonical repository role | `OpenRGD/openrgd` is the non-actuating canonical/tooling root |
| Normative source | modular `spec/` JSONC |
| Strict mirror | tracked `standard/` leaf mirror |
| Default seed | derived profile; no silent divergence |
| Canonical integrity | `OPENRGD_SOURCE_TREE_SHA256_V1` |
| Generated products | untracked, deterministic, non-authoritative |
| Version axes | standard, toolchain and contracts remain independent |
| New tag names | `standard-v*`, `toolchain-v*`, `contracts-agent-v*` only |
| Agent Contracts | `candidate`, non-normative, not promoted by merge |
| Physical runtime | external repository responsibility |
| AION expected archive | exact bytes unavailable; historical digest preserved |
| AION recovered backup | mismatched same-lineage variant; audited and excluded from PR #1 |
| Draft spec assertions | registered; block stable standard release, not reconciliation merge |
| Plugin ABI | disabled pending accepted contract and fail-closed loader |
| Signing | not implemented; not claimed; stable-release gate |
| Default merge method | merge commit; squash only by explicit exception |
| PR #1 merge method | merge commit to preserve reconciliation provenance |
| Merge vs release | separate decisions; merge creates no tag or release |

## Latest hygiene implementation checkpoint

```text
commit:   b614334f167b92ba3b84d0b37adc9a782c9fec1e
workflow: 33744591319 — SUCCESS
```

Required checks:

```text
Validate Python 3.10       PASS
Validate Python 3.12       PASS
Build Windows executable   PASS
```

Additional verified results:

```text
repository hygiene         PASS
governance validator       PASS
Agent Contracts candidate  PASS
pytest                     41 passed
```

Checkpoint artifact:

```text
id:     9889133457
name:   openrgd-rgd-windows
size:   12,189,099 bytes
sha256: 148a1ea8202ddeb313323ff0feee736219d0b34b5d366883d4aed98a2a0453f3
```

The final documentation-only reconciliation head must pass the same checks before review status changes.

## Governance and hygiene closure

The branch contains and validates:

- `GOVERNANCE.md`;
- `RELEASE_POLICY.md`;
- `SECURITY.md`;
- `governance/policy.json`;
- `.github/CODEOWNERS`;
- pull-request and RFC templates;
- explicit Agent Contracts maturity status;
- canonical source, mirror and seed policy;
- runtime and physical-actuation boundary;
- generated-artifact cleanup and canonical hashing;
- evidence-only URDF/USDA lifecycle;
- static profile inspection;
- `.env`/private-key/generated-debris exclusions;
- tracked-file secret and contact scanning;
- stable-release registry for unverified draft-spec assertions;
- recovered AION backup identity and security audit;
- stale/prototype surface inventory;
- governance and hygiene regression tests.

## External repository control still required

GitHub reports:

```text
main protected: false
repository rulesets: none
```

The required control is tracked in:

```text
GitHub issue #2
[GOVERNANCE] Apply required protection to main before reconciliation merge
```

Before merge:

1. apply the settings in `docs/governance/BRANCH_PROTECTION.md`;
2. verify GitHub reports `protected: true` for `main`;
3. verify these required contexts are present:
   - `Validate Python 3.10`
   - `Validate Python 3.12`
   - `Build Windows executable`;
4. require the branch to be up to date;
5. require review conversations to be resolved;
6. block force pushes and deletion of `main`;
7. close issue #2 with the verification result;
8. add the verification result to PR #1;
9. mark PR #1 ready for review;
10. re-confirm all required checks on the final head;
11. merge using a merge commit.

Until these steps are complete, PR #1 remains draft even when CI is green.

## Single-maintainer review record

While the repository has one maintainer, an independent approval cannot be required without making merge impossible. The final merge record must confirm:

- the public PR checklist was completed;
- no unresolved review conversation remains;
- the branch is current with `main`;
- all required checks passed on the final head;
- no release or contract promotion is bundled into the merge;
- known exclusions and non-actions remain visible;
- the secret-bearing local backup was not imported;
- stale/prototype surfaces remain historical rather than active.

When a second maintainer is appointed, governance and branch protection must be updated to require one non-author approval for normative changes.

## AION evidence-scope closure

The historical checksum record identifies:

```text
expected ZIP SHA-256:
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

The exact archive bytes remain unavailable.

The recovered full local backup has:

```text
observed ZIP SHA-256:
f91ad48cd6a2e8a8bff5f3c559fb8f7fc475e9c4957864aeed6aa689d07615ae
```

The backup is structurally valid and supports the same AION-ready lineage, but it is not byte-identical to the expected archive. It contains a local `.env`, generated artifacts and a post-checksum source edit. The secret value is not retained in repository evidence.

Decision:

```text
used by PR #1: no
merge blocking: no
automatic import: no
future path: sanitized post-merge AION evidence-delta PR
```

## Draft specification content closure

Unverified institutional/contact/model/dataset/citation/future-snapshot literals remain in the historical draft source and are registered in `SPEC_CONTENT_HYGIENE.json`.

```text
reconciliation merge blocking: no
stable standard release blocking: yes
```

This avoids both silent historical rewriting and accidental promotion of draft claims.

## Contract-status closure

`contracts/agent/v0.1.0/STATUS.json` freezes:

```text
maturity = candidate
normative = false
accepted = false
stable_release_allowed = false
merge_behavior = PRESERVE_CANDIDATE_STATUS
```

Therefore the existence or merge of these files cannot silently promote them into the accepted standard.

## Post-merge boundary

The merge must not create a tag or release.

A separate release pull request may prepare:

```text
Python version: 0.2.0rc1
Git tag:        toolchain-v0.2.0-rc.1
```

A separate AION evidence-delta pull request must sanitize the recovered backup, compare every source file, resolve or explicitly defer AION-H-001 through AION-H-010 and preserve the distinction between codec evidence and runtime claims.

## Work outside PR #1

The following do not block this reconciliation merge because they are explicitly out of scope:

- full OpenUSD SDK integration;
- generic seed/body compatibility certification;
- live ROS 2 or hardware-bound validation;
- embodied runtime and Body Adapter repositories;
- promotion of Agent Contracts;
- AION source integration;
- stable release signing and attestations;
- normative cleanup of registered draft-spec assertions.
