# Examples and fixtures policy

## Historical examples

The historical `example/` tree remains removed from the active repository.

| Historical file | Finding | Decision |
|---|---|---|
| Berkeley Humanoid Lite URDF | generated externally; referenced absent `./assets/merged/*.stl` files | remove from active tree |
| iCub URDF | referenced absent `package://iCub/meshes/...` resources; no fixture provenance file | remove from active tree |
| UR5 URDF | generated from an external ROS package; contained a local controller IP and installation-specific paths | remove from active tree |

Original blob identities remain in `docs/history/generated-artifacts/INVENTORY.json` and Git history.

## Admitted project-owned fixtures

The repository contains two canonical **test fixtures**, not normative robot examples.

### URDF

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
- exact source-derived assertions in CI.

### USDA

```text
tests/fixtures/usd/openrgd_minimal_arm.usda
tests/fixtures/usd/PROVENANCE.md
```

Properties:

- synthetic and authored for OpenRGD;
- MIT licensed;
- text USDA with revolute and prismatic UsdPhysics joints;
- explicit `metersPerUnit`, `kilogramsPerUnit`, `upAxis` and `defaultPrim` metadata;
- no referenced layer, payload, external asset or package dependency;
- no IP address, secret or machine-local path;
- no claim of physical actuation suitability;
- exact angular, linear and effort conversion assertions in CI.

## Verified lifecycle

Both fixture families are exercised through:

```text
source parse
→ partial import
→ seed enrichment (compatibility remains UNVERIFIED)
→ canonical hash
→ integrity-aware profile check
→ deterministic non-actuating grounding context
→ deterministic machine bundle
→ deterministic static ROS 2 export
```

## Admission rule for future examples and fixtures

A future file under `examples/` or `tests/fixtures/` must be:

1. authored by the project or accompanied by explicit redistribution provenance;
2. minimal enough to review;
3. hermetic, or declare every external asset/layer dependency;
4. free of local IP addresses, secrets and machine-specific absolute paths;
5. exercised by an automated test;
6. associated with the importer/exporter version and subset it validates;
7. non-normative unless a specification file explicitly references it;
8. clearly labelled as a fixture, illustrative example or physically validated reference body.

A source file becoming parseable does not make it safe to actuate. Seed enrichment, profile hashing, structural validation and grounding-context generation do not prove hardware compatibility.
