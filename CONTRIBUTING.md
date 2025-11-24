# Contributing to OpenRGD

First off, **thank you**.

By being here, you are not just looking at a repository; you are stepping into the engine room of the future. OpenRGD is not a product—it is a movement to give Artificial Intelligence a physical body, safely, openly, and democratically.

We believe that the interface between Cognitive Intelligence (LLMs) and Physical Reality (Robotics) **must not belong to a single corporation**. It must be a shared language—an open standard that anyone can use, audit, and improve.

By contributing to OpenRGD, you are helping to ensure that the robots of tomorrow are built on transparent, understandable foundations. You are building a better, more accessible future.

---

## Why Your Contribution Matters

We are at a turning point. Robots are moving from "hard-coded scripts" to "cognitive agents."
* If we leave this to closed silos, we risk a fragmented, opaque, and unsafe future.
* If we build it together, **we democratize the access to embodied AI.**

Whether you fix a typo, propose a new sensor schema, or optimize our CLI parser, you are adding a brick to the "Rosetta Stone" of robotics.

---

## How You Can Help

We need all kinds of minds here. Pick your path:

### 1. The Architect (Schema Proposals)
OpenRGD is a living standard. If you are an expert in a specific field (e.g., Soft Robotics, Drone Flight Dynamics, Haptic Feedback), we need your knowledge.
* **The Task:** Propose changes to the JSONC definitions in `schemas/`.
* **The Method:** Open an issue titled `[RFC] Proposal for...` and describe the missing piece.
* **The Goal:** Make the `.rgd` format capable of describing *any* machine.

### 2. The Engineer (CLI & Tooling)
Our reference implementation (`src/cli.py`) needs to be robust, fast, and fail-safe.
* **The Task:** Improve the Python CLI, add validation logic, or create converters (e.g., URDF -> RGD).
* **The Method:** Fork the repo, write clean Python code, add tests, and submit a PR.

### 3. The Scribe (Examples & Docs)
A standard is only as good as its documentation.
* **The Task:** Create `.rgd` files for popular robots (Unitree, Spot, TurtleBot, Panda Arm) and add them to `examples/`.
* **The Goal:** Prove that OpenRGD works for real-world hardware.

---

## 🏆 Become a Maintainer (Own a Domain)

We use a "Domain Expert" governance model. We don't want generalists to guess; we want specialists to lead.

* Are you a motor control wizard?
* Are you an ethics/alignment researcher?
* Do you live and breathe kinematics?

**Claim your spot.**
If you contribute consistently to a specific domain (e.g., `01-foundation` or `04-volition`), you can apply to become the **Official Maintainer** for that section. Your name will be permanently recorded in the schema definition as the guardian of that domain.

To apply, open an issue: `[MAINTAINER APPLICATION] Domain X`.

---

## 🚀 Submission Guidelines

1.  **Fork & Branch:** Create a branch for your feature (`git checkout -b feature/amazing-idea`).
2.  **Commit:** Keep messages clear and concise.
3.  **Code Style:**
    * **Python:** Follow PEP8.
    * **JSONC:** Ensure comments are helpful and the structure validates.
4.  **Pull Request:** Submit your PR to the `main` branch. Explain *why* this change is needed.

### A Note on "Heart"
We value technical excellence, but we value **intent** even more. We are building this for humanity. Be kind, be patient with beginners, and always code with the user's safety in mind.

---

_ "The best way to predict the future is to invent it. The best way to secure it is to open source it." _

---
OpenRGD Maintainers