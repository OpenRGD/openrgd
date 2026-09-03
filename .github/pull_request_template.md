## Change classification

- [ ] Normative specification or governance
- [ ] Candidate / experimental contract
- [ ] Toolchain / validator / importer / static exporter
- [ ] Documentation only
- [ ] Historical evidence / reconciliation
- [ ] Security or safety fix

## Problem and evidence

Describe the concrete problem, the evidence used and the scope deliberately left unchanged.

## Authority impact

- Normative source paths changed:
- Contract maturity changed:
- Repository ownership boundary changed:
- Canonical source-tree root changed:
- Version axis affected:

## Compatibility and migration

Describe compatibility, breaking changes, migration steps and external repository impact. Write `NONE` when there is no impact.

## Safety boundary

- [ ] This change does not enable physical actuation in the canonical repository.
- [ ] Observations do not silently mutate actuation state.
- [ ] Missing hardware/safety evidence fails closed.
- [ ] Any physical-runtime delta is marked `EXPERIMENTAL` or `PROPOSED_UPSTREAM` and linked.

## Generated artifacts

- [ ] No generated bundle, robot workspace, export, build output or machine-local file was committed as source.
- [ ] `standard/` and the packaged seed were regenerated only from the canonical source policy.
- [ ] Canonical hashing was updated intentionally when selected source bytes changed.

## Contracts and reasoning evidence

- [ ] Candidate contracts remain labelled candidate unless an accepted RFC promotes them.
- [ ] Audit evidence is structured; private chain-of-thought is neither requested nor persisted.

## Validation

List commands and CI runs. For code changes, include the final commit tested.

```text
commands:
result:
workflow:
```

## Governance checklist

- [ ] Relevant RFC or decision record is linked, or the change explains why none is required.
- [ ] Documentation and changelog are updated.
- [ ] All required CI checks pass on the final head.
- [ ] Review conversations are resolved.
- [ ] Release is handled separately; this PR does not create an implicit release.
