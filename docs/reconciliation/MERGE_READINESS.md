# Reconciliation PR #1 — Merge Readiness

## Status

```text
technical review readiness:   YES
governance tree freeze:       COMPLETE AND CI-VALIDATED
repository hygiene:           COMPLETE AND CI-VALIDATED
main branch protection:       COMPLETE AND VERIFIED
repository-control issue:     #2 CLOSED / COMPLETED
pull-request transition:      READY AFTER FINAL-HEAD CI
merge authorization:          CONDITIONAL ON REQUIRED CHECKS
release authorization:        NO
```

This document records the conditions for merging reconciliation PR #1. Merge and release remain separate decisions.

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
| Merge vs release | merge creates no tag, release or contract promotion |

## Verified repository control

On 2026-09-03, the repository steward applied the required `main` branch-protection rule. GitHub independently reports:

```text
main protected: true
required status-check enforcement: everyone
```

The verified configuration is:

```text
strict / branch up to date:       true
required approving reviews:       0
review conversations resolved:    true
enforce administrators:           true
force pushes allowed:             false
branch deletion allowed:          false
required linear history:          false
```

Required contexts:

```text
Validate Python 3.10
Validate Python 3.12
Build Windows executable
```

GitHub issue #2 was closed as completed after verification. The configuration is also recorded in `docs/governance/BRANCH_PROTECTION.md`.

## Final merge procedure

The final pull-request head may be merged only after all of the following are true:

1. PR #1 is marked ready for review;
2. the branch remains current with `main`;
3. all three required checks pass on the final head;
4. no unresolved review thread exists;
5. the public single-maintainer checklist is satisfied;
6. the merge uses a merge commit;
7. no tag or GitHub Release is created;
8. Agent Contracts retain `candidate` status;
9. the recovered AION backup remains excluded from this PR.

Branch protection now enforces the freshness and required-check conditions server-side.

## Single-maintainer review record

During the current single-maintainer phase, an independent approval count of zero is intentional and documented. The final merge record must confirm:

- required checks passed on the final head;
- no unresolved review conversation remains;
- the branch is current with `main`;
- no release or contract promotion is bundled into the merge;
- known exclusions and non-actions remain visible;
- the secret-bearing local backup was not imported;
- stale/prototype surfaces remain historical rather than active.

When a second maintainer is appointed, governance and protection must require one non-author approval for normative changes.

## Latest complete validation before protection record

The final hygiene implementation head before this documentation update passed:

```text
commit:   176634a5667ceab84f0244b426a4f2caa9c7e7f9
workflow: 33746410489 — SUCCESS
pytest:   41 passed
```

Required checks:

```text
Validate Python 3.10       PASS
Validate Python 3.12       PASS
Build Windows executable   PASS
```

Artifact:

```text
id:     9889827297
name:   openrgd-rgd-windows
size:   12,191,301 bytes
sha256: bb806ee6794b089d78b1c2c54a7679ecccdd9807299a8d35d7860b25632aa372
```

The branch-protection documentation commit and this merge-readiness commit must pass the same required checks before merge.

## AION evidence-scope closure

The historical expected ZIP and the recovered local backup retain separate identities:

```text
expected historical ZIP:
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d

recovered backup variant:
f91ad48cd6a2e8a8bff5f3c559fb8f7fc475e9c4957864aeed6aa689d07615ae
```

The recovered backup is not used by PR #1, is not merge-blocking, and requires a sanitized post-merge AION evidence-delta pull request.

## Contract-status closure

`contracts/agent/v0.1.0/STATUS.json` remains:

```text
maturity = candidate
normative = false
accepted = false
stable_release_allowed = false
merge_behavior = PRESERVE_CANDIDATE_STATUS
```

The merge cannot silently promote these contracts.

## Post-merge boundary

No tag or release is created by this merge. Separate future work may prepare:

```text
Python version: 0.2.0rc1
Git tag:        toolchain-v0.2.0-rc.1
```

A separate AION evidence-delta PR must sanitize the recovered backup, compare every source file, and resolve or explicitly defer AION-H-001 through AION-H-010.

## Work outside PR #1

The following are explicitly out of scope and do not block this reconciliation merge:

- full OpenUSD SDK integration;
- generic seed/body compatibility certification;
- live ROS 2 or hardware-bound validation;
- embodied runtime and Body Adapter repositories;
- promotion of Agent Contracts;
- AION source integration;
- stable release signing and attestations;
- normative cleanup of registered draft-spec assertions.
