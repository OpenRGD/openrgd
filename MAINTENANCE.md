# Annual Maintenance & Renewal Rituals

A small open-source project stays healthy because someone periodically checks the boring things too.

> **Goal:** signal to the world — and to ourselves — that OpenRGD is alive, maintained and safe to build on.

## 🛡️ 1. Security

- [ ] Review repository/admin access.
- [ ] Review GitHub branch protection and required CI checks.
- [ ] Review dependency advisories and run a Python dependency audit.
- [ ] Verify that `.env`, credentials and private keys remain excluded from Git.
- [ ] Review the private vulnerability-reporting path documented in `SECURITY.md`.
- [ ] If signing infrastructure is introduced, verify key ownership and expiry before relying on it.

## ⚖️ 2. License & Project Metadata

- [ ] Review dependency licenses for compatibility with the project.
- [ ] Update project metadata when maintainers, supported Python versions or distribution channels change.
- [ ] Check that README claims still match what the toolchain actually does.

## 🗺️ 3. Roadmap & Vision

- [ ] Archive completed milestones into `CHANGELOG.md`.
- [ ] Review engineering targets: safety-loop frequency, latency, interoperability, simulation fidelity and runtime separation.
- [ ] Make sure ambitious targets remain labelled as targets until measured.

## 🏗️ 4. Technical Hygiene

- [ ] Run the full CI matrix.
- [ ] Exercise `rgd alive` on the included URDF and USDA examples.
- [ ] Check canonical hash generation and deterministic compilation.
- [ ] Remove generated build debris that should not be tracked.
- [ ] Review deprecated CLI surfaces.

## 📢 5. Community Signal

Once a year, publish a short “State of OpenRGD” update:

- what worked;
- what broke;
- what became real;
- what is still a target;
- where help is most useful.

*Keep the standard technically serious and the project human.*
