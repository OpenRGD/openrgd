# Examples and fixtures policy

## Historical examples

The historical `example/` tree remains removed from the active repository.

| Historical file | Finding | Decision |
|---|---|---|
| Berkeley Humanoid Lite URDF | generated externally; referenced absent `./assets/merged/*.stl` files | remove from active tree |
| iCub URDF | referenced absent `package://iCub/meshes/...` resources; no fixture provenance file | remove from active tree |
| UR5 URDF | generated from an external ROS package; contained a local controller IP and installation-specific paths | remove from active tree |

Original blob identities remain in `docs/history/generated-artifacts/INVENTORY.json` and Git history.

## Admitted project-owned fixture

The repository now contains one canonical **test fixture**, not a normative robot example:

```text
tests/fixtures/urdf/openrgd_minimal_arm.urdf
tests/fixtures/urdf/PROVENANCE.md
```

Properties:

- synthetic and authored for OpenRGD;
- MIT licensed;
- four links and three joints, including revolute, prismatic and fixed cases;
- no external mesh or package dependency;
- no IP address, secret or machine-local path;
- no claim of physical actuation suitability;
- assertions for exact source-derived values;
- exercised through the complete non-actuating lifecycle.

The CI path is:

```text
URDF parse
→ partial import
→ seed enrichment (compatibility remains UNVERIFIED)
→ canonical hash
→ structural check
→ boot prompt assembly
→ deterministic machine bundle
→ deterministic static ROS 2 export
```

## Admission rule for future examples and fixtures

A future file under `examples/` or `tests/fixtures/` must be:

1. authored by the project or accompanied by explicit redistribution provenance;
2. minimal enough to review;
3. hermetic, or declare every external asset dependency;
4. free of local IP addresses, secrets and machine-specific absolute paths;
5. exercised by an automated test;
6. associated with the importer/exporter version it validates;
7. non-normative unless a specification file explicitly references it;
8. clearly labelled as a fixture, illustrative example or physically validated reference body.

A source file becoming parseable does not make it safe to actuate, nor does seed enrichment prove compatibility with inherited HAL, calibration or safety modules.
