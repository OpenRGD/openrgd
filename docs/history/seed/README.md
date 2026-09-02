# Archived default-seed artifacts

This directory preserves files removed from the active packaged default seed during the historical reconciliation.

## `03_agency/skills_library.legacy.json`

- **Original active path:** `src/openrgd/seeds/default/spec/03_agency/skills_library.json`
- **Original Git blob:** `4b4decb50d17a7266be37e6d135eec647d50d9e8`
- **Classification:** SUPERSEDED / HISTORICAL EVIDENCE
- **Reason:** the file was a two-entry strict-JSON skill index that coexisted with, but did not represent, the normative `spec/03_agency/skills_library.jsonc` contract and its packaged core skill files.
- **Reconciliation action:** preserve the bytes here, remove the file from the active seed namespace, and mirror the complete normative JSONC skill subsystem into the seed.

The archived file is not loaded by `rgd init`, compilation, validation, or runtime code. Its retention here is documentary and does not grant it compatibility or normative status.
