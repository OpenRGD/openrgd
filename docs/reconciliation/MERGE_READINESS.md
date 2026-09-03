# Reconciliation PR #1 — Merge Readiness

## Status

```text
technical review readiness:  YES
repository governance freeze: ADOPTED ON BRANCH
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
| New tag names | scoped prefixes only |
| Agent contracts | `candidate`, non-normative, not promoted by merge |
| Physical runtime | external repository responsibility |
| AION-ready archive | digest-only evidence; explicitly excluded from PR #1 |
| Signing | not implemented; not claimed; required before stable trust-sensitive release |
| PR #1 merge method | merge commit to preserve reconciliation provenance |

## Technical closure

The final head must pass all required checks:

```text
Validate Python 3.10
Validate Python 3.12
Build Windows executable
```

The pull-request description must identify the final workflow, artifact digest and unresolved items that remain outside merge scope.

## Governance closure

Repository-tree governance is complete when the final head contains and validates:

- `GOVERNANCE.md`;
- `RELEASE_POLICY.md`;
- `SECURITY.md`;
- `governance/policy.json`;
- `.github/CODEOWNERS`;
- pull-request and RFC templates;
- explicit contract maturity status;
- evidence-scope exclusion record;
- branch-protection target policy.

## External repository control still required

GitHub currently reports `main` as unprotected and no repository ruleset exists.

Before merge:

1. apply the settings in `docs/governance/BRANCH_PROTECTION.md`;
2. verify `protected: true` for `main`;
3. close the repository-control issue;
4. update this document or the PR conversation with the verification result;
5. mark the pull request ready for review;
6. re-confirm the final required checks;
7. merge using a merge commit.

Until these steps are complete, PR #1 remains draft even when CI is green.

## Single-maintainer review record

While the repository has one maintainer, an independent approval cannot be required without making merge impossible. The final merge record must therefore confirm:

- the public PR checklist was completed;
- no unresolved review conversation remains;
- the branch is current with `main`;
- all required checks passed on the final head;
- no release or contract promotion is bundled into the merge;
- known exclusions and non-actions remain visible.

When a second maintainer is appointed, governance and branch protection must be updated to require one non-author approval for normative changes.

## Post-merge boundary

The merge must not create a tag or release.

A separate release pull request may prepare:

```text
Python version: 0.2.0rc1
Git tag:        toolchain-v0.2.0-rc.1
```

That release remains subject to its own migration notes, final CI, artifact inventory and unsigned/signed provenance disclosure.

## Remaining work outside PR #1

The following do not block this reconciliation merge because they are explicitly out of scope:

- full OpenUSD SDK integration;
- generic seed/body compatibility certification;
- live ROS 2 or hardware-bound validation;
- embodied runtime and Body Adapter repositories;
- promotion of Agent Contracts;
- recovery and inspection of the excluded AION-ready archive;
- stable release signing and attestations.
