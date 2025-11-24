# OpenRGD: A Proposed Standard for Cognitive Embodiment

[![Status: RFC](https://img.shields.io/badge/Status-Draft_Standard_v0.1-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**OpenRGD (Robot Graph Definition)** is an open architectural standard designed to serve as the universal semantic bridge between Artificial Intelligence and Physical Reality.

As intelligence becomes disembodied and ubiquitous, the necessity for a standardized protocol to define physical existence—identity, capability, constraints, and ethics—becomes the foundational challenge of robotics. OpenRGD addresses this by defining a machine-readable "Self-Model" that allows any cognitive agent to safely and effectively embody any physical machine.

---

## 1. The Mission

The primary objective of OpenRGD is to eliminate the "Grounding Gap"—the semantic disconnect between high-level reasoning models and low-level hardware control.

By formalizing the description of a robot not just as a kinematic chain (geometry), but as a semantic entity (purpose and limits), OpenRGD enables:

* **Introspection:** The ability for a machine to understand its own hardware and state.
* **Safety-by-Design:** The separation of intent from execution through immutable safety layers.
* **Interoperability:** A unified language allowing cognitive models to transfer seamlessly between different physical bodies.

## 2. The Architecture

OpenRGD is not a monolithic file format, but a hierarchical **Semantic Graph**. The standard organizes the complexity of artificial life into six normative domains.

### 01. Foundation (The Body)
*The immutable physical reality.*
This domain defines the hardware abstraction, including actuator dynamics, sensor fidelity, physical dimensions, and resource topology. It serves as the ground truth of the machine's physical existence.

### 02. Operation (The Physiology)
*The autonomic safety system.*
This domain defines the operational envelopes, reflex loops, and hard constraints that preserve the integrity of the machine and its environment. These rules are designed to override cognitive intent when safety is compromised.

### 03. Agency (The Mind)
*The capability interface.*
This domain maps the robot's potential interactions with the world. It defines the "Skills Library" and the API surface that the cognitive model can utilize to effect change in its environment.

### 04. Volition (The Conscience)
*The alignment of intent.*
This domain formalizes the system's value hierarchy, priority resolution engines, and ethical constraints. It acts as the governance layer for decision-making processes.

### 05. Evolution (The Lifecycle)
*The temporal state.*
This domain tracks the history of the system, including component wear, fatigue models, plasticity rates, and maintenance schedules. It introduces the concept of "mortality" and degradation into the robotic definition.

### 06. Ether (The Society)
*The collective connectivity.*
This domain defines the protocols for multi-agent coordination, swarm consensus, reputation management, and knowledge sharing between distinct entities.

## 3. The Kernel Concept

Implementations of the OpenRGD standard rely on a **Semantic Kernel**—an orchestration layer that dynamically loads and links all six domains. The Kernel ensures that the cognitive agent possesses a complete, consistent, and context-aware picture of its embodiment before any action is planned or executed.

## 4. Governance

OpenRGD is an open standard developed under the **Request for Comments (RFC)** process. It belongs to no single corporation but is maintained by the OpenRGD Organization for the benefit of the global robotics and AI community.

We invite researchers, ethicists, and engineers to contribute to the refinement of this specification.

* **Current Status:** v0.1 (Draft Proposal)
* **Documentation:** See `STRUCTURE.md` for technical hierarchy.
* **Collaboration:** See `CONTRIBUTING.md` to join the working group.

### 4.1 Future Roadmap: AI-Governed Evolution
> **Note:** This section outlines the architectural vision for v1.0+.

OpenRGD is designed from the outset to support **AI-assisted stewardship**. The specification proposes a framework where authorized AI systems may eventually propose changes via **Commitment Proposals (CPs)**—machine-readable diffs subject to a strict validation hierarchy:

1.  **Automated Validators:** Structural integrity and Safety Layer impact analysis.
2.  **Human Oversight:** Final review by domain maintainers.
3.  **Regulatory Audit:** Traceable cryptographic signatures to ensure legal compliance.

This establishes a path toward a future where AI systems participate in the continuous improvement of safety standards without bypassing human governance.

---

## 5. Authors

* **Pasquale Ranieri (Italia Robotica)** - *Lead Architect & Specification Author*

### Acknowledgements
* **Recursive Design:** Portions of this specification were developed with the assistance of Large Language Models (LLMs). The latest generation of models shows an emerging ability to infer physical behavior—linking geometry, dynamics, and constraints in ways that approximate real-world reasoning. These capabilities helped validate the internal consistency of the `01_Foundation` domain.

## 6. Contribute
**OpenRGD is an open standard.** To participate in its development, read the [`CONTRIBUTING.md`](CONTRIBUTING.md) guide and follow the contribution workflow.

---
Copyright © 2025 OpenRGD Organization. Distributed under the MIT License.