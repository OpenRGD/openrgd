# Changelog

All notable changes to the **OpenRGD** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
*Changes currently in the `main` branch, targeting v0.2.0.*

### Added
- **CLI Toolchain:** Complete refactoring of the `rgd` command line interface using `typer` and `rich`.
  - Added `rgd init`: Interactive scaffolding with "Gold Standard" templates.
  - Added `rgd check`: Semantic validation of the Kernel and module links.
  - Added `rgd boot`: Cognitive BIOS simulation and LLM Prompt generation.
  - Added `rgd compile-spec`: Generation of Human (.jsonc) and Machine (.json) digital twins.
- **Interoperability Bridges:**
  - **Import:** New `rgd import` command supporting URDF and USD (ASCII/Zip).
  - **Export:** New `rgd export` command for ROS2 (`ros2_control` + `xacro`) and Isaac Lab (Python Configs).
- **OpenRGD Studio:** Added `studio.html`, a single-page web application for visual configuration and cognitive simulation.
- **Windows Integration:** Added `assets/windows/setup.bat` for native .rgd file association and icons.
- **Security:** Added `SECURITY.md` and PGP keys structure for vulnerability reporting.

### Changed
- **Architecture:** Moved core specifications from `src/` to a dedicated `spec/` directory to separate code from data.
- **Kernel:** Updated to v0.3 schema to support `cognitive_expansion_engine` and `oneiric_cycle`.
- **Foundation:** Updated `actuation_topology.jsonc` to support Control Profiles (inheritance) and Isaac Lab impedance parameters.

---

## [0.1.0] - 2025-11-25
*Initial Public Alpha Release.*

### Added
- **Core Specification:** Definition of the 6 Domains (Foundation, Operation, Agency, Volition, Evolution, Ether).
- **Kernel Architecture:** Introduced `kernel.jsonc` as the semantic orchestrator.
- **Reference Implementation:** Full JSONC schema examples for the "Berkeley Humanoid Lite".
- **Documentation:** Added `README.md`, `CONTRIBUTING.md`, `CLI_GUIDE.md`, and `STRUCTURE.md`.
- **License:** Released under MIT License.

### Security
- Established the `vulnerabilities.openrgd.org` disclosure program structure.