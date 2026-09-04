# Contributing to OpenRGD

Welcome. OpenRGD is an open standard and open playground for cognitive embodiment, and contributions from roboticists, software engineers, researchers, designers, writers, students and curious builders are welcome.

The easiest way to understand the project is to try it:

```bash
python -m pip install -e .
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

## Where to contribute

- `spec/` — improve the OpenRGD standard and reference profile.
- `src/openrgd/` — improve the CLI, importers, validators and static bridges.
- `example/` — add safe, redistributable examples that help people learn.
- `contracts/` — explore cross-component interfaces that need shared agreement.
- docs — make OpenRGD easier to understand and more welcoming.

## A few principles

### Evidence before certainty
If a robot file does not tell us a torque, calibration, device ID or certification status, do not invent one. Unknown and approximate values are valid states.

### Targets are allowed to be ambitious
A target such as a 1 kHz safety loop belongs in the project when it is clearly labelled as an engineering target. Measured results must be reported separately.

### Safety boundaries stay explicit
Static validation, a successful `rgd alive`, or a generated ROS 2 configuration is not permission to actuate hardware. Physical execution belongs to a compatible embodied runtime and Body Adapter.

### Generated files are generated
Do not commit local robot workspaces, compiled bundles, exports, bytecode, `.env`, private keys or build products as source.

## Examples

Public examples under `example/` should be:

- owned by the project or clearly redistributable;
- small enough to understand;
- free of secrets, local network addresses and machine-specific paths;
- runnable with documented commands;
- useful for learning or testing a real OpenRGD workflow.

## Development workflow

1. branch or fork from `main`;
2. make one coherent change;
3. add or update tests;
4. update docs when user-visible behavior changes;
5. if `spec/` changes, update its canonical hash and strict mirror;
6. run the validation suite;
7. open a pull request and explain what the change enables.

Recommended checks:

```bash
python -m pip install -e . pytest
python tools/validate_repository.py
python tools/validate_hygiene.py
python tools/validate_artifacts.py
python tools/validate_canonical_hash.py
python tools/validate_runtime_boundary.py
python contracts/agent/v0.1.0/validate.py
python -m pytest -q
```

After an intentional standard change:

```bash
rgd hash --write
rgd build-standard
```

Review the resulting diff before committing it.

## RFCs

Large or breaking standard changes should begin as an RFC using the GitHub issue template. Explain:

- the problem;
- the proposed idea;
- compatibility impact;
- safety implications;
- how we can test it.

An RFC can be ambitious. Just distinguish what exists today from what we want to build next.

## Pull requests

Keep PRs focused and readable. Tell us what changed, why it matters, and how you tested it.

`main` is protected and changes land through pull requests.

## Security

Please follow `SECURITY.md` for vulnerabilities. Never put credentials or exploitable details in public examples or issues.

## Most importantly

Open standards grow because people care enough to make them better. Try something, ask questions, challenge assumptions, and bring your own perspective.

**Let's build a common language between intelligence and physical reality.**
