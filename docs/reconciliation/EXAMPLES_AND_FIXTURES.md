# Examples and fixtures policy

## Decision

The historical `example/` tree is removed from the active repository.

The three files were useful during exploratory importer work, but none satisfied the requirements for a canonical public fixture:

| Historical file | Finding | Decision |
|---|---|---|
| Berkeley Humanoid Lite URDF | generated externally; references absent `./assets/merged/*.stl` files | remove from active tree |
| iCub URDF | references absent `package://iCub/meshes/...` resources; no fixture provenance file | remove from active tree |
| UR5 URDF | generated from an external ROS package; contains a local controller IP and installation-specific paths | remove from active tree |

Original blob identities remain in `docs/history/generated-artifacts/INVENTORY.json` and in Git history.

## Admission rule for future examples

A future file under `examples/` or `tests/fixtures/` must be:

1. authored by the project or accompanied by explicit redistribution provenance;
2. minimal enough to review;
3. hermetic, or declare every external asset dependency;
4. free of local IP addresses, secrets and machine-specific absolute paths;
5. exercised by an automated test;
6. associated with the importer/exporter version it validates;
7. non-normative unless a specification file explicitly references it.

Until the URDF importer lineage is reconciled, the repository uses an inline minimal USDA fixture in tests and does not claim a canonical URDF example.
