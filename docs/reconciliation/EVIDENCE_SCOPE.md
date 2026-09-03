# Reconciliation evidence scope

## AION-ready archive identity

The historical checksum record identifies:

```text
openrgd-v0.2-aion-ready.zip
sha256:
8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

The exact ZIP bytes represented by that checksum are still unavailable.

A full local backup was recovered and inspected on 2026-09-03:

```text
uploaded backup SHA-256:
f91ad48cd6a2e8a8bff5f3c559fb8f7fc475e9c4957864aeed6aa689d07615ae
```

The digests do not match.

The recovered file is classified as:

```text
EXPECTED_IDENTITY_UNAVAILABLE
+
RECOVERED_BACKUP_VARIANT_MISMATCH
```

It strongly supports the same AION-ready working lineage, but it is not relabelled as the historical archive.

## Why the variant is not treated as identical

The backup contains file timestamps after the checksum record, including:

- Python bytecode/cache;
- `src/rgd.egg-info/`;
- a later edit to `src/openrgd/main.py`;
- a local `.env`.

The `.env` includes a non-empty credential and is excluded from all source/evidence imports. The secret value is not recorded in repository documentation.

The complete technical audit is:

- `AION_READY_BACKUP_AUDIT.md`
- `AION_READY_BACKUP_AUDIT.json`

## PR #1 decision

Neither the unavailable expected archive nor the mismatched backup variant is used as a source for reconciliation PR #1.

```text
used as PR #1 source: no
merge blocking: no
automatic import: no
```

This prevents a late recovered artifact from rewriting the already-audited reconciliation history.

## Future handling

After PR #1 is merged:

1. create a separate AION evidence-delta branch from the merged `main`;
2. remove `.env`, caches, bytecode, package metadata and generated workspaces;
3. preserve a source-only inventory commitment;
4. compare every remaining source file with the merged canonical root;
5. harden validation and implementation claims;
6. add independent tests;
7. open a separate pull request.

If the exact historical ZIP is later recovered, verify it against the recorded `8c8f4a7f…` digest and compare it independently. Do not overwrite the backup-variant record.
