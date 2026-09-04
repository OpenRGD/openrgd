# OpenRGD: A Proposed Standard for Cognitive Embodiment

[![Status: RFC](https://img.shields.io/badge/Status-Draft_Standard_v0.2-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**OpenRGD (Robot Graph Definition)** is an open architectural standard designed to serve as the universal semantic bridge between Artificial Intelligence and Physical Reality.  
It defines a machine-readable **Self-Model** that helps a cognitive agent understand the body it inhabits: what it is, what it can do, what it must not do, how it changes over time, and how it relates to other agents.

---

## ⚡ Start Instantly: Bring a Robot Alive

Don't just read the spec — give OpenRGD a robot description and watch the profile come alive.

### 🐧 Linux / macOS

```bash
# 1. Install the toolchain
git clone https://github.com/OpenRGD/openrgd.git
cd openrgd
pip install -e .

# 2. The magic command
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

### 🪟 Windows (PowerShell)

```powershell
# 1. Install the toolchain
git clone https://github.com/OpenRGD/openrgd.git
cd openrgd
pip install -e .

# 2. The magic command
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

`rgd alive` is the high-level OpenRGD workflow. From one URDF or text USDA file it:

```text
understands source evidence
        ↓
creates the OpenRGD body profile
        ↓
enriches it with the selected seed
        ↓
computes canonical integrity
        ↓
validates the profile
        ↓
builds the grounding context
        ↓
compiles the machine bundle
        ↓
generates static ROS 2 interoperability files
```

You can also try the USDA example:

```bash
rgd alive example/minimal-arm/openrgd_minimal_arm.usda
```

The generated profile is a starting point for embodiment, not an automatic hardware-safety certification. Physical actuation belongs to a compatible embodied runtime and Body Adapter.

---

## 1. Interoperability

A unified language enabling cognitive models to move across different robotic bodies, platforms, simulators, and ecosystems without relearning the meaning of embodiment from scratch.

---

## 2. The Architecture

OpenRGD is not a monolithic file but a hierarchical **Semantic Graph** structured into six domains.

### **01. Foundation — The Body**  
*Physical reality.*  
Defines hardware, geometry, actuators, sensors, calibration, topology, physical quality and embodiment evidence.

### **02. Operation — The Physiology**  
*Safety and operational limits.*  
Defines safety envelopes, reflex rules, runtime constraints, and engineering targets for low-level control.

### **03. Agency — The Mind**  
*Capability interface.*  
Defines skills, world models, proprioception, perception-oriented structures, and how cognition can interact with the world.

### **04. Volition — The Conscience**  
*Intent alignment.*  
Defines values, alignment, arbitration, decision governance, and experimental semantic projections such as HyperAion.

### **05. Evolution — The Lifecycle**  
*Temporal state.*  
Tracks wear, maintenance, adaptation, continuity, and change over time.

### **06. Ether — The Society**  
*Collective intelligence.*  
Defines multi-agent coordination, consensus, reputation, federation, and shared reality interfaces.

---

## 3. Toolchain (CLI)

The `rgd` CLI manages the lifecycle of an embodiment definition.

### The Golden Loop

For most people, start with one command:

```bash
rgd alive robot.urdf
```

When you want individual control, the underlying tools remain available:

- **Ingest** (`rgd import`) — extract evidence from URDF or text USDA.
- **Enrich** (`rgd alive`) — create a complete OpenRGD profile from source evidence plus a seed.
- **Validate** (`rgd check`) — verify integrity and module structure.
- **Ground** (`rgd boot`) — generate a non-actuating grounding context.
- **Compile** (`rgd compile-spec`) — produce the deterministic machine bundle.
- **Bridge** (`rgd export ros2`) — generate static ROS 2 interoperability files.

---

## 4. The Kernel Concept

OpenRGD uses a **Semantic Kernel profile** as the map that links embodiment domains together. The canonical repository describes the contracts, relationships, safety objectives and grounding information; physical execution is implemented by compatible runtime components outside the standard/tooling core.

---

## 5. Engineering Targets

OpenRGD deliberately distinguishes between **what exists today** and **what we are engineering toward**.

For example, the current v0.2 reference profile includes a target of a **1 kHz safety/reflex loop** and sub-millisecond decision budgets for compatible low-level safety controllers. These are engineering objectives to measure and improve against — not claims that every OpenRGD implementation already achieves or certifies them.

That distinction lets the project stay ambitious without pretending the future has already arrived.

---

## 6. Governance

OpenRGD follows an open RFC-driven development model.

- **Status:** Draft Standard v0.2
- **Documentation:** See `STRUCTURE.md`
- **Contribution Guide:** See `CONTRIBUTING.md`
- **Friendly onboarding:** See `ONBOARDING.md`
- **Want to help?** See `ENTHUSIAST.md`

---

## 7. Future Roadmap: AI-Assisted Evolution

> *This section describes a direction, not a claim of completed implementation.*

OpenRGD is designed to support AI-assisted stewardship through machine-readable proposals, automated validation, human review and auditable evolution.

The goal is simple: make embodiment standards capable of evolving as robotics evolves — without losing traceability, safety, or human accountability.

---

## 8. Authors

* **Pasquale Ranieri (Italia Robotica)** — *Lead Architect & Specification Author*

### Acknowledgements
Portions of OpenRGD have been developed with the assistance of Large Language Models as design, coding and review tools. Human maintainers remain responsible for accepting changes to the standard.

## 9. Contribute

**OpenRGD is an open standard.** Engineers, roboticists, researchers, designers, writers, ethicists, students and curious builders are welcome.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), try an example, break something, improve it, and tell us what you learned.

> **Robots are dreams made executable. Let's give them a language for understanding the bodies they inhabit.**

---

Distributed under the MIT License.
