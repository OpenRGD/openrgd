# OpenRGD Repository Layout

This file describes the directories that actually exist after the current reconciliation pass.

```text
openrgd/
├── .github/workflows/       # Active CI workflows
├── assets/                  # Branding and platform assets
├── contracts/               # Versioned cross-component contracts and provenance
├── docs/
│   ├── history/
│   │   ├── runtime-prototype/ # Byte-preserved quarantined runtime evidence
│   │   └── seed/              # Superseded packaged-seed evidence
│   └── reconciliation/      # Decisions, status, artifact and repository maps
├── example/                 # Source robot-description examples
├── export/                  # Legacy/example generated outputs; non-authoritative
├── plugins/                 # Bundled plugin prototypes
├── RGD-ur5/                 # Legacy/reference generated robot bundle
├── my-robots/               # Legacy local-style generated robot bundle
├── spec/                    # Normative human-readable JSONC source
├── standard/                # Derived strict-JSON compatibility mirror
├── src/
│   ├── openrgd/
│   │   ├── commands/        # CLI verbs; `run` is fail-closed compatibility only
│   │   ├── core/            # Shared loading, compilation and plugin logic
│   │   ├── importers/       # URDF and USD ingestion
│   │   ├── seeds/           # Packaged scaffold copied by `rgd init`
│   │   └── synapses/        # Static interoperability generators
│   └── cli.py               # Legacy parallel CLI module pending review
├── tests/                   # Repository, artifact, runtime-boundary and contract tests
├── tools/                   # Repository, artifact and specification utilities
├── CHANGELOG.md
├── GLOSSARIO.md
├── LICENSE
├── README.md
├── STRUCTURE.md
├── VERSIONING.md
└── pyproject.toml
```

There is intentionally no active `src/openrgd/runtime/` package on the reconciliation branch. The old implementation is historical evidence; a conformant embodied runtime belongs to a separately reconciled repository.

## Where to make changes

- Change the reference standard in `spec/`, then regenerate and review derived mirrors.
- Change non-actuating Python tooling in `src/openrgd/`.
- Add cross-component interfaces under `contracts/` with a maturity label and provenance.
- Add historical evidence under `docs/history/`; do not rewrite it as if it were current.
- Record reconciliation choices under `docs/reconciliation/`.
- Implement hardware execution only in a versioned embodied-runtime or Body Adapter repository consuming the contracts.

Generated `build/`, `dist/`, bytecode and packaging metadata are excluded by `.gitignore` and MUST NOT be committed.
