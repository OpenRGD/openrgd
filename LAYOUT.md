# OpenRGD Repository Layout

This file describes the directories that actually exist after the first reconciliation pass.

```text
openrgd/
├── .github/workflows/       # Active CI workflows
├── assets/                  # Branding and platform assets
├── contracts/               # Versioned cross-component contracts and provenance
├── docs/
│   ├── history/             # Preserved non-normative historical documents
│   └── reconciliation/      # Decisions, status and repository map
├── example/                 # Source robot-description examples
├── export/                  # Legacy/example generated outputs; non-authoritative
├── plugins/                 # Bundled plugin prototypes
├── RGD-ur5/                 # Legacy/reference generated robot bundle
├── my-robots/               # Legacy local-style generated robot bundle
├── spec/                    # Human-readable JSONC specification source
├── standard/                # Generated strict-JSON mirror
├── src/
│   ├── openrgd/
│   │   ├── commands/        # CLI verbs and command groups
│   │   ├── core/            # Shared loading, compilation and plugin logic
│   │   ├── importers/       # URDF and USD ingestion
│   │   ├── runtime/         # Experimental engine and runtime adapters
│   │   ├── seeds/           # Packaged scaffold copied by `rgd init`
│   │   └── synapses/        # Interoperability generators
│   └── cli.py               # Legacy parallel CLI module pending review
├── tools/                   # Repository and specification build utilities
├── CHANGELOG.md
├── GLOSSARIO.md
├── LICENSE
├── README.md
├── STRUCTURE.md
├── VERSIONING.md
└── pyproject.toml
```

## Where to make changes

- Change the reference standard in `spec/`, then regenerate and review derived mirrors.
- Change Python behavior in `src/openrgd/`.
- Add cross-component interfaces under `contracts/` with a maturity label and provenance.
- Add historical evidence under `docs/history/`; do not rewrite it as if it were current.
- Record reconciliation choices under `docs/reconciliation/`.

Generated `build/`, `dist/`, bytecode and packaging metadata are excluded by `.gitignore` and MUST NOT be committed.
