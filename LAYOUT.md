# OpenRGD repository layout

This file describes the active tree after the canonical-artifact and runtime-boundary reconciliation.

```text
openrgd/
├── .github/workflows/       # Active CI
├── assets/                  # Branding and packaging assets
├── contracts/               # Versioned cross-component contracts
├── docs/
│   ├── history/
│   │   ├── generated-artifacts/  # Removed artifact/example inventory
│   │   ├── runtime-prototype/    # Quarantined runtime source evidence
│   │   └── seed/                 # Superseded seed evidence
│   └── reconciliation/      # Decisions, policies and audit reports
├── plugins/                 # Bundled plugin prototypes
├── spec/                    # Normative modular JSONC source
├── src/openrgd/
│   ├── commands/            # CLI commands
│   ├── core/                # Loading, canonical hashing and shared tooling
│   ├── importers/           # URDF and USD ingestion
│   ├── seeds/               # Packaged default profile
│   └── synapses/            # Static interoperability generators
├── standard/                # Tracked strict-JSON leaf mirror
├── tests/                   # Automated contract and toolchain tests
├── tools/                   # Reconciliation and validation tools
├── .gitattributes
├── .gitignore
├── CHANGELOG.md
├── CLI_GUIDE.md
├── GLOSSARIO.md
├── LICENSE
├── README.md
├── STRUCTURE.md
├── VERSIONING.md
├── pyproject.toml
├── rgd.spec                 # Windows PyInstaller recipe
└── run.py                   # PyInstaller entry point
```

## Deliberately absent from the active tree

The following are generated or quarantined and must not be committed as current authority:

```text
spec/01_spec.jsonc ... spec/06_spec.jsonc
spec/openrgd_unified_spec*.json*
standard/01_spec.json ... standard/06_spec.json
standard/openrgd_unified_spec*.json
standard/benchmarks/
RGD-*/
my-robots/
export/
example/ historical external URDF files
src/openrgd/runtime/ historical prototype
```

Original Git identities are recorded under `docs/history/`.

## Where to make changes

- Change the standard in modular `spec/` source files.
- Run `rgd hash --write` after an intentional source change.
- Rebuild `standard/` through `rgd build-standard` and review the diff.
- Change toolchain behavior in `src/openrgd/`.
- Add cross-component interfaces under `contracts/` with maturity and provenance.
- Put test-owned inputs under `tests/fixtures/` only when they are minimal, hermetic and exercised by tests.
- Record historical evidence under `docs/history/` and current decisions under `docs/reconciliation/`.

Generated build products, machine bundles, robot workspaces and export outputs are excluded by `.gitignore`.
