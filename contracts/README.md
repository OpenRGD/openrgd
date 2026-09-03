# OpenRGD Cross-Component Contracts

This directory is the canonical repository location for interfaces shared across OpenRGD components.

Contract maturity is explicit and machine-readable:

- **candidate** — recovered or converged material under review; non-normative and subject to breaking change;
- **accepted** — approved through the OpenRGD governance process and normative within its declared version;
- **deprecated** — retained for compatibility and provenance, but no longer recommended;
- **historical** — evidence only and never current authority.

The current `agent/v0.1.0` package is a **convergence candidate**. Its status is frozen in:

```text
contracts/agent/v0.1.0/STATUS.json
```

Its presence in this repository does not imply that its decisions existed in the 2025 lineage, does not silently promote open questions and does not make it part of a stable standard or release.

Promotion to `accepted` requires the process defined in `GOVERNANCE.md`, including complete normative text, compatibility rules, producer/consumer conformance tests, a validated reference flow and an explicit accepted RFC or governance decision.
