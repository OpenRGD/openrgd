# Contributing to OpenRGD

OpenRGD is an open standard and toolchain for cognitive embodiment. Contributions are welcome, but source evidence, normative decisions, generated artifacts and physical execution must remain clearly separated.

Read these files before proposing a change:

- `GOVERNANCE.md`
- `RELEASE_POLICY.md`
- `STRUCTURE.md`
- `docs/reconciliation/DECISIONS.md`
- `docs/reconciliation/EXAMPLES_AND_FIXTURES.md`

## Choose the change class

### Normative specification or governance

Changes to `spec/`, accepted contracts, canonical hashing, governance, conformance or repository ownership are normative.

Open an RFC for breaking or cross-component changes using:

```text
.github/ISSUE_TEMPLATE/rfc.md
```

The pull request must include evidence, compatibility impact, migration notes, tests and a decision-record update.

### Candidate contract or experiment

Candidate material must declare its maturity and provenance. Its implementation must not silently alter accepted behavior.

A candidate becomes accepted only through the promotion process in `GOVERNANCE.md`.

### Toolchain

Toolchain code lives under:

```text
src/openrgd/
```

Importers extract source-supported evidence. Static exporters generate non-actuating interoperability artifacts. Tooling must fail closed when required evidence is missing and must not redefine the standard privately.

### Fixture or example

Test-owned fixtures belong under:

```text
tests/fixtures/
```

A fixture or example must be:

- owned by the project or explicitly redistribution-audited;
- minimal and reviewable;
- hermetic or explicit about external dependencies;
- free of secrets, local IP addresses and machine-specific paths;
- used by an automated test;
- clearly labelled non-normative unless the specification explicitly says otherwise.

Do not commit generated robot workspaces, exports, compiled bundles or build products as source.

## Development workflow

1. fork or branch from the current protected default branch;
2. make the smallest coherent change;
3. add or update tests;
4. update documentation and the changelog;
5. update the canonical source root and strict mirror only when selected `spec/` bytes change;
6. run the validation suite;
7. open a pull request and complete the template.

Recommended local checks:

```bash
python -m pip install -e .
python tools/validate_repository.py
python tools/reconcile_artifacts.py
python tools/validate_canonical_hash.py
python tools/validate_runtime_boundary.py
python tools/validate_governance.py
python contracts/agent/v0.1.0/validate.py
python -m pytest -q
```

## Source-tree changes

After an intentional selected `spec/` change:

```bash
rgd hash --write
rgd build-standard
```

Review every resulting diff. The packaged default seed must remain aligned unless an explicit digest-pinned `RUNTIME_PROFILE_OVERRIDE` is approved.

## Import and static export changes

Importer changes must distinguish source evidence from inferred policy. Missing physical values remain unknown; malformed or non-finite values fail closed.

Static exporters must:

- remain non-actuating;
- verify the canonical source and machine-bundle roots;
- expose incomplete hardware binding explicitly;
- avoid generic drivers, fake addresses and convenient physical defaults.

## Physical-runtime changes

This repository does not implement physical execution. Changes that belong to an embodied runtime or Body Adapter should be proposed there and, when they expose a missing OpenRGD contract, returned here as a documented Contract Delta or RFC.

Do not connect cognition directly to motors, middleware publishers or device buses from this repository.

## Pull requests

All changes enter `main` through pull requests. Direct and force pushes to `main` are prohibited by policy.

During the current single-maintainer phase, the public checklist, required CI, resolved conversations and final merge-readiness record substitute for an impossible self-approval. When a second maintainer is appointed, normative changes require one non-author approval.

## Security and safety

Do not disclose exploitable vulnerabilities in public issues. Follow `SECURITY.md`.

Do not use a repository/tooling test as permission to actuate hardware. A valid hash, successful import, `rgd check`, `rgd boot` or static export does not certify physical safety.

## Commit messages

Use clear, scoped messages such as:

```text
feat(import): ...
fix(integrity): ...
docs(governance): ...
test(export): ...
```

Historical evidence must not be rewritten to match later decisions.
