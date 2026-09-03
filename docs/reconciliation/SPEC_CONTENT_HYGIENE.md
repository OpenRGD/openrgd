# Draft specification content hygiene

## Status

The historical OpenRGD v0.2 draft contains contact, institutional, model, dataset, citation and future-snapshot values that were not independently verified during reconciliation.

They remain visible because silently replacing historical normative content would be a substantive specification change. Their presence does not make them factual, operational or approved.

Machine-readable registry:

```text
docs/reconciliation/SPEC_CONTENT_HYGIENE.json
```

## Current classification

The registered values include:

- `OpenRGD Foundation`;
- named councils or review panels;
- `@openrgd.org` and selected `@italiarobotica.it` contact endpoints;
- an asserted constitutional-alignment model identifier;
- dataset-style URIs;
- future-dated alignment snapshots;
- an unmaterialized `SHA3-512::<hex>` placeholder;
- an unverified `et al.` citation.

These are classified as **known draft assertions requiring review**.

## Authority

Until reviewed:

- contact strings are not operational disclosure channels;
- institutional names do not prove that a legal entity or governing body exists;
- model and dataset identifiers do not prove that the referenced artifacts exist;
- future snapshots are illustrative, not historical evidence;
- a placeholder hash is not integrity evidence;
- an unverified citation is not bibliographic proof.

## Merge and release treatment

This registry is not a blocker for the historical reconciliation merge because PR #1 preserves and classifies the draft rather than promoting it to a stable standard.

It is a blocker for a stable standard release.

Resolution requires a dedicated normative content audit that either:

1. verifies a value and records evidence;
2. replaces it through an approved specification change; or
3. removes it while preserving the prior bytes in history.

CI prevents new unregistered contact or assertion literals from being added silently.
