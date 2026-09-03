# Main Branch Protection

## Observed repository state

At the governance freeze checkpoint, GitHub reports:

```text
branch: main
protected: false
repository rulesets: none
```

Repository files cannot enforce server-side branch protection. These settings must be applied in GitHub before reconciliation PR #1 is merged.

## Required protection for `main`

Configure a branch protection rule or repository ruleset targeting exactly:

```text
main
```

Required settings:

1. require a pull request before merging;
2. require the branch to be up to date before merging;
3. require status checks:
   - `Validate Python 3.10`
   - `Validate Python 3.12`
   - `Build Windows executable`
4. require all review conversations to be resolved;
5. block force pushes;
6. block deletion of `main`;
7. apply the rule to administrators where operationally possible;
8. do not permit direct pushes as the normal workflow.

## Approval count during single-maintainer mode

Current required approvals:

```text
0
```

Reason: the repository currently has one steward and GitHub does not allow a pull-request author to approve their own pull request. Governance compensates through a public self-review checklist, required CI, resolved conversations and a final merge-readiness record.

When a second maintainer is appointed, update protection to require:

```text
1 approval from a non-author maintainer
```

and enable required CODEOWNERS review for normative surfaces.

## Signed commits

Do not enable a signed-commit requirement as part of this merge unless the existing unsigned history and contributor workflow have first been migrated deliberately.

Signing remains a stable-release gate under `RELEASE_POLICY.md`; it is not represented as already implemented.

## Merge method

The repository default is a merge commit so granular reviewed commits and the pull-request boundary remain in history. Squash merge requires an explicit decision that the intermediate commits contain no useful provenance.

Reconciliation PR #1 must use a merge commit.

## Verification

After applying the settings, verify that GitHub reports:

```text
protected: true
```

and that the three required status-check contexts are present. Record the completed repository-control issue in `docs/reconciliation/MERGE_READINESS.md` before merging PR #1.
