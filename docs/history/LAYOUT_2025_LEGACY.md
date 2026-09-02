# OpenRGD Project Layout

This document describes the directory structure of the OpenRGD repository.
It helps contributors locate the core logic, the standard definitions, and the tooling modules.

## 📂 High-Level Overview

The repository is divided into two main realms:
1.  **`spec/`**: The **Data** (The Standard, Reference Implementation, and Templates).
2.  **`src/`**: The **Code** (The CLI, Compilers, and Bridges).

```text
openrgd/
├── assets/                 # Static resources (Icons, Wallpapers, Logos)
├── spec/                   # The Reference Implementation (JSONC)
├── src/                    # The Python Package Source Code
├── .gitignore              # Git configuration
├── CHANGELOG.md            # Version history
├── CLI_GUIDE.md            # User manual for the 'rgd' command
├── CONTRIBUTING.md         # Governance and contribution rules
├── GUIDE_EXPORT.md         # Documentation for ROS2/Isaac bridges
├── GUIDE_IMPORT.md         # Documentation for URDF/USD ingestion
├── LAYOUT.md               # This file
├── LICENSE                 # MIT License
├── pyproject.toml          # Python build configuration (PEP 621)
├── README.md               # The Vision and Manifesto
├── run.py                  # Dev launcher script
└── SECURITY.md             # Vulnerability reporting policy
🏗️ Directory Details
spec/ (The Standard)
Contains the "Golden Standard" definition of a robot. This folder serves two purposes: it documents the schema via example (Reference Implementation) and provides the default template for new projects.

00_core/: The Kernel and Meta-Governance (e.g., kernel.jsonc).

01_foundation/ to 06_ether/: The 6 normative domains of the OpenRGD protocol.

src/openrgd/ (The Toolchain)
The Python package source.

commands/: The CLI verbs. Each file corresponds to an rgd [verb] command.

init.py: Scaffolding engine (uses seeds/).

check.py: Semantic validator and linter.

boot.py: Cognitive BIOS simulator (Prompt generation).

compiler.py: Logic for compile-spec (Twin generation).

bridge.py: Router for the Export system.

importer.py: Router for the Import system.

studio.py: Web server for the GUI.

core/: Shared utilities and internal logic.

config.py: Global state (Quiet/Verbose flags).

visuals.py: UI helpers (Rich logs, ASCII art, Progress bars).

utils.py: Robust JSONC parser, Path resolution.

templates.py: Dynamic text generation helpers.

bridges/: The Export Plugins (Adapters).

ros2/: Generates .yaml and .xacro.

isaac/: Generates Python ArticulationCfg classes.

base.py: Abstract Interface for new bridges.

importers/: The Ingestion Plugins (Parsers).

urdf/: XML parser for ROS robots.

usd/: Regex parser for Isaac/Omniverse stages (.usda).

seeds/: Static assets included in the binary build.

default/: The copy of spec/ used by rgd init to generate new robots.

assets/ (Resources)
branding/: Official logos and vector graphics.

windows/: Integration scripts (setup.bat) and icons (.ico) for Windows Explorer support.

⚙️ Configuration Files
pyproject.toml: The modern replacement for setup.py. It defines dependencies (typer, rich), metadata, and the entry point script (rgd = openrgd.main:run).

SECURITY.md: Defines the Responsible Disclosure policy and PGP keys.