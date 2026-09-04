# OpenRGD Project Layout

OpenRGD is deliberately easy to navigate.

At the center are two things:

1. **`spec/`** — the standard and reference profile.
2. **`src/`** — the Python toolchain that reads, validates, imports and exports it.

```text
openrgd/
├── spec/              # OpenRGD standard / reference profile
├── src/openrgd/       # CLI and tooling
├── example/           # Ready-to-run URDF and USDA examples
├── tests/             # Automated tests and fixtures
├── contracts/         # Candidate cross-component contracts
├── standard/          # Derived strict-JSON mirror
├── tools/             # Repository validation helpers
├── assets/            # Branding and platform resources
├── .github/           # CI and contribution templates
├── README.md          # Vision + fastest path to try OpenRGD
├── ONBOARDING.md      # Friendly getting-started guide
├── ENTHUSIAST.md      # Ways to participate
├── CLI_GUIDE.md       # Full CLI reference
├── GUIDE_IMPORT.md
├── GUIDE_EXPORT.md
├── GUIDE_DOCKER.md
├── PLUGIN_GUIDE.md
├── STRUCTURE.md       # Technical architecture
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── SECURITY.md
└── LICENSE
```

## `spec/` — The Standard

The six domains remain the heart of OpenRGD:

```text
00_core
01_foundation
02_operation
03_agency
04_volition
05_evolution
06_ether
```

The v0.2 reference profile now also contains explicit actuator lineage/data-quality structures, AION packet/projection definitions and engineering control targets. Targets such as a 1 kHz safety loop are goals for compatible embodied runtimes, not claims that the canonical CLI itself performs physical control.

## `src/openrgd/` — The Toolchain

The CLI is intentionally layered:

- `rgd alive` — high-level one-command workflow;
- importers — URDF and lightweight USDA evidence extraction;
- profile/hash tooling — integrity and grounding;
- compiler — deterministic machine bundle;
- synapses — static interoperability outputs.

## Generated Files

Robot workspaces, machine bundles and exports are generated on demand and should not be committed back into the core repository.
