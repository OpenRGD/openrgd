# Reconciliation Evidence Scope

## Purpose

This record closes the ambiguity around evidence mentioned during the historical reconciliation but not available as inspectable bytes.

## `openrgd-v0.2-aion-ready.zip`

Available evidence:

```text
checksum record: openrgd-v0.2-aion-ready.sha256
expected SHA-256: 8c8f4a7f9c3ff67504962fb255dd9652e60264538c97fb6a1a037a256d98351d
```

Unavailable evidence:

```text
archive bytes
file tree
individual file contents
independent archive verification
```

Classification:

```text
DIGEST_ONLY_BYTES_UNAVAILABLE
```

## Decision for reconciliation PR #1

The archive is explicitly excluded from PR #1.

The checksum proves that an archive with the stated name and digest was produced or referenced. It does not reveal the archive contents and cannot support claims about files, architecture or implementation.

Therefore:

- no content is reconstructed from the filename;
- no diff is inferred from the checksum;
- no current file is attributed to this archive;
- the missing bytes do not block merging the evidence already inspected;
- the exclusion is disclosed in the audit and pull request.

## Future recovery

If the archive is recovered later:

1. verify its SHA-256 against the recorded digest;
2. inspect it independently;
3. classify every relevant delta against the merged baseline;
4. open a separate evidence-delta pull request;
5. preserve non-retroactivity: newly recovered material may correct the historical record but must not be described as having been reviewed in PR #1.

The machine-readable record is `EVIDENCE_SCOPE.json`.
