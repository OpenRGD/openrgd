# Reconciliation PR #1 — Merge Readiness

## Status

```text
technical review readiness:   YES
governance tree freeze:       COMPLETE AND CI-VALIDATED
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
| AION-ready archive | digest-only evidence; explicitly excluded from PR #1 |
| Signing | not implemented; not claimed; stable-release gate |
| Default merge method | merge commit; squash only by explicit exception |
| PR #1 merge method | merge commit to preserve reconciliation provenance |
| Merge vs release | separate decisions; merge creates no tag or release |

## Technical closure

Governance implementation checkpoint:

```text
02222e88a4e5f5026d828e3f5d174ae65a0a2428
```

Pull-request workflow:

```text
33735707622 — SUCCESS
```

Required checks:

```text
Validate Python 3.10       PASS
Validate Python 3.12       PASS
Build Windows executable   PASS
```

Additional verified results:

```text
governance validator       PASS
Agent Contracts candidate  PASS
pytest                     35 passed
```

Checkpoint artifact:

```text
id:     9885693022
name:   openrgd-rgd-windows
size:   12,190,774 bytes
sha256: bb1303549910927f9e1f04c9709fe54ca179ac8404139ab5c534c33073a0d966
```

## Governance-tree closure

The branch contains and validates:

- `GOVERNANCE.md`;
- `RELEASE_POLICY.md`;
- `SECURITY.md`;
- `governance/policy.json`;
- `.github/CODEOWNERS`;
- pull-request and RFC templates;
- explicit Agent Contracts maturity status;
- evidence-scope exclusion record;
- branch-protection target policy;
- governance validator and tests;
- decisions R-041 through R-049.

The tree-level governance freeze is complete.

## External repository control still required

GitHub reported at freeze time:

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
   - `Build Windows executable`
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

While the repository has one maintainer, an independent approval cannot be required without making merge impossible. The final merge record must therefore confirm:

- the public PR checklist was completed;
- no unresolved review conversation remains;
- the branch is current with `main`;
- all required checks passed on the final head;
- no release or contract promotion is bundled into the merge;
- known exclusions and non-actions remain visible.

When a second maintainer is appointed, governance and branch protection must be updated to require one non-author approval for normative changes.

## Evidence-scope closure

`openrgd-v0.2-aion-ready.zip` is not an unresolved hidden dependency of this merge.

Only its checksum record was available:

```text
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

Its bytes were unavailable, so its contents were not inspected or inferred. The archive is explicitly excluded from PR #1. Later recovery requires digest verification and a separate evidence-delta pull request.

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

That release remains subject to its own migration notes, final CI, artifact inventory and unsigned/signed provenance disclosure.

## Work outside PR #1

The following do not block this reconciliation merge because they are explicitly out of scope:

- full OpenUSD SDK integration;
- generic seed/body compatibility certification;
- live ROS 2 or hardware-bound validation;
- embodied runtime and Body Adapter repositories;
- promotion of Agent Contracts;
- recovery and inspection of the excluded AION-ready archive;
- stable release signing and attestations.
