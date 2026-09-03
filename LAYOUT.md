# OpenRGD repository layout

This file describes the active tree after canonical-artifact, runtime-boundary, import/export, profile-inspection, governance and hygiene reconciliation.

```text
openrgd/
├── .github/
│   ├── workflows/                 # Active CI
│   ├── ISSUE_TEMPLATE/rfc.md      # Normative RFC intake
│   ├── CODEOWNERS                 # Current stewardship
│   └── pull_request_template.md   # Evidence and governance checklist
├── assets/branding/               # Selected project branding only
├── contracts/                     # Versioned cross-component contracts
│   └── agent/v0.1.0/
│       └── STATUS.json            # Machine-readable candidate maturity
├── governance/
│   └── policy.json                # Machine-readable repository governance
├── docs/
│   ├── governance/
│   │   └── BRANCH_PROTECTION.md   # Required external GitHub controls
│   ├── history/
│   │   ├── stale-prototypes/          # Removed stale/prototype identities
│   │   ├── generated-artifacts/       # Removed artifact/example inventory
│   │   ├── import-export-prototypes/  # Superseded importer/exporter identities
│   │   ├── profile-inspection-prototypes/ # Superseded check/boot identities
│   │   ├── runtime-prototype/         # Quarantined runtime source evidence
│   │   └── seed/                      # Superseded seed evidence
│   └── reconciliation/
│       ├── AION_READY_BACKUP_AUDIT.json
│       ├── AI_HYGIENE_AUDIT.md
│       ├── DECISIONS.md
│       ├── DECISIONS_HYGIENE.md
│       ├── EVIDENCE_SCOPE.json
│       ├── MERGE_READINESS.md
│       ├── SPEC_CONTENT_HYGIENE.json
│       └── policies, boundaries and audit reports
├── spec/                          # Normative modular JSONC source
├── src/openrgd/
│   ├── commands/                  # Non-actuating CLI commands
│   ├── core/                      # Hashing, profile inspection and shared tooling
│   ├── importers/                 # Evidence-only URDF and text USDA ingestion
│   ├── seeds/                     # Packaged default profile
│   └── synapses/                  # Static interoperability generators
├── standard/                      # Tracked strict-JSON leaf mirror
├── tests/
│   ├── fixtures/
│   │   ├── urdf/                  # Owned hermetic URDF evidence
│   │   └── usd/                   # Owned hermetic USDA evidence
│   └── test_*.py                  # Automated contracts, lifecycle and hygiene checks
├── tools/
│   ├── validate_governance.py
│   ├── validate_hygiene.py
│   └── reconciliation and validation tools
├── .gitattributes
├── .gitignore
├── CHANGELOG.md
├── CLI_GUIDE.md
├── CONTRIBUTING.md
├── GLOSSARIO.md
├── GOVERNANCE.md
├── GUIDE_EXPORT.md
├── GUIDE_IMPORT.md
├── LICENSE
├── README.md
├── RELEASE_POLICY.md
├── SECURITY.md
├── STRUCTURE.md
├── VERSIONING.md
├── pyproject.toml
├── rgd.spec                       # Windows PyInstaller recipe
└── run.py                         # PyInstaller entry point
```

## Deliberately absent from the active tree

The following are generated, stale, unaccepted or quarantined and must not be committed as current authority:

```text
.env and private key material
spec/01_spec.jsonc ... spec/06_spec.jsonc
spec/openrgd_unified_spec*.json*
standard/01_spec.json ... standard/06_spec.json
standard/openrgd_unified_spec*.json
standard/benchmarks/
RGD-*/
my-robots/
export/
example/ historical external robot files
src/openrgd/runtime/ historical prototype
plugins/ and permissive plugin-loader prototypes
unselected branding proposals
stale promotional, onboarding, Docker and maintenance drafts
```

Original Git identities are recorded under `docs/history/`.

## Authority map

| Path | Authority |
|---|---|
| `spec/` | Normative draft standard source; known unverified assertion literals are registered separately |
| `standard/` | Derived strict-JSON mirror |
| `contracts/` | Explicitly versioned/maturity-labelled interfaces |
| `governance/` and root governance documents | Repository governance and release policy |
| `src/openrgd/` | Non-actuating reference toolchain |
| `tests/fixtures/` | Owned, non-normative evidence |
| `docs/reconciliation/` | Current reconciliation decisions, evidence scope and hygiene registries |
| `docs/history/` | Non-normative historical evidence |

## Where to make changes

- Change the standard in modular `spec/` source files.
- Run `rgd hash --write` after an intentional selected-source change.
- Rebuild `standard/` through `rgd build-standard` and review the diff.
- Change non-actuating toolchain behavior in `src/openrgd/`.
- Add cross-component interfaces under `contracts/` with machine-readable maturity and provenance.
- Change governance through a normative pull request and, where required, an RFC.
- Put test-owned inputs under `tests/fixtures/` only when they are minimal, hermetic and exercised by tests.
- Record historical evidence under `docs/history/` and current decisions under `docs/reconciliation/`.
- Never commit local credentials, `.env`, private keys, bytecode, package metadata or generated workspaces.

Generated build products, machine bundles, robot workspaces and export outputs are excluded by `.gitignore` and checked by `tools/validate_hygiene.py`.

Server-side protection of `main` is not represented by the Git tree. Its required configuration is documented under `docs/governance/BRANCH_PROTECTION.md` and tracked separately in GitHub issue #2.
