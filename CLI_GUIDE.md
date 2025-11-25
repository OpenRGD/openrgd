# OpenRGD CLI: Operator's Manual

The **OpenRGD Command Line Interface** (`rgd`) is the primary tool for managing the lifecycle of a cognitive robot definition. It acts as the bridge between your file system and the AI Agent.

---

## ⚡ Installation

If you are developing locally (from the source):

```bash
cd openrgd
pip install -e .
Verify the installation:

Bash

rgd --help
🎮 Core Commands
1. Genesis (init)
Scaffolds a new robot project ("Containment Field") populated with the internal Gold Standard templates.

Bash

# Interactive mode (will ask for the project name)
rgd init

# Fast mode (creates the folder immediately)
rgd init my_robot_v1
What it does:

Creates the standard folder structure (spec/01_foundation, spec/02_operation, etc.).

Injects a valid kernel.jsonc in spec/00_core.

Populates domains with reference templates (actuation dynamics, safety supervisors, ethical alignment).

2. Diagnostics (check)
Validates the semantic integrity of your robot definition.

Bash

# Auto-detects the kernel in the current folder
rgd check

# Targets a specific kernel file
rgd check path/to/kernel.jsonc
What it does:

Auto-discovery: Finds kernel.jsonc automatically (searching in root, spec/, or 00_core/).

Link Verification: Ensures every module referenced in the Kernel actually exists on the disk.

Syntax Validation: Checks for valid JSONC syntax using a robust parser.

Visuals: Displays a hierarchical, color-coded tree of the robot's "cortex".

3. Awakening (boot)
Simulates the robot's cognitive boot sequence and generates the System Prompt for Large Language Models.

Bash

# Standard Boot (Cinematic UI)
rgd boot

# Pipeable Output (for software pipelines)
rgd boot --output json
Use Case: Copy the output of rgd boot (Text Mode) and paste it into the System Message of GPT-4, Claude, or your local VLA model to "ground" it in physical reality.

4. Compilation (compile-spec)
Compiles the fragmented .jsonc files into a Unified Specification Artifact. This is essential for training or fine-tuning models on the robot's definition.

Bash

rgd compile-spec
The "Twin" System: This command generates two files in your spec/ folder:

openrgd_unified_spec.jsonc (Human Twin): Contains the raw source code (comments included) of all modules. Optimized for LLM context injection (the AI can read the comments).

openrgd_unified_spec.json (Machine Twin): Contains clean, minified JSON data. Optimized for validators and software tools.

🤖 Automation & CI/CD
The CLI supports "Robotic Modes" for integration into pipelines (GitHub Actions, Jenkins, Docker).

Quiet Mode (-q / --quiet)
Disables all animations, ASCII art, and "personality" logs. Only critical errors or requested data are printed to stdout.

Bash

# Example: Extract JSON configuration silently to a file
rgd boot -q --output json > robot_config.json
Verbose Mode (-v / --verbose)
Enables deep debugging logs, showing exact file paths, parsing steps, and internal state changes.

Bash

rgd check -v
🧠 "Cinematic" Experience
By default, the CLI runs in Cinematic Mode. It simulates system initialization delays, displays ASCII art, and occasionally "chats" via randomized status messages (e.g., "Checking my limbs...").

This is designed to give the developer a sense of connection with the machine being defined. To disable this permanently for a session, use -q.