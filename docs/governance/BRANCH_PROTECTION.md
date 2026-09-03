# Main Branch Protection

## Status

The required server-side protection for `main` was applied and verified on 2026-09-03. GitHub issue #2 was closed as completed.

```text
branch: main
protected: true
required status-check enforcement: everyone
```

## Verified configuration

The active rule requires:

```text
strict / branch up to date:       true
pull request before merge:        required
required approving reviews:       0
review conversations resolved:    true
enforce administrators:           true
force pushes allowed:             false
branch deletion allowed:          false
required linear history:          false
```

Required status-check contexts:

```text
Validate Python 3.10
Validate Python 3.12
Build Windows executable
```

This configuration preserves merge commits while blocking direct unreviewed changes to `main` and requiring the final pull-request head to pass all three checks.

## Single-maintainer mode

The required approval count remains:

```text
0
```

Reason: the repository currently has one steward and GitHub does not allow a pull-request author to approve their own pull request. Governance compensates through:

- the public pull-request checklist;
- required CI;
- strict branch freshness;
- resolved review conversations;
- a final merge-readiness record;
- explicit human merge authorization.

When a second maintainer is appointed, update protection to require:

```text
1 approval from a non-author maintainer
```

and enable required CODEOWNERS review for normative surfaces.

## Merge method

The repository default remains a merge commit so granular reviewed commits and the pull-request boundary remain reachable.

Reconciliation PR #1 must be merged with:

```text
merge method: merge commit
```

Squash merge requires an explicit future decision that intermediate commits contain no useful implementation or provenance evidence.

## Signed commits

Signed commits are not required for this historical reconciliation merge. Existing history is unsigned and the signing lifecycle has not yet been implemented.

Signing remains a stable trust-sensitive release gate under `RELEASE_POLICY.md`. The source-tree SHA-256 commitment proves content identity, not authorship.

## Verification record

Evidence is retained in:

- GitHub issue #2 and its closing comment;
- reconciliation PR #1;
- `docs/reconciliation/MERGE_READINESS.md`;
- the GitHub branch endpoint, which reports `protected: true` and the three required status-check contexts.

Any future change to these controls must follow repository governance and must not silently weaken the protections.
