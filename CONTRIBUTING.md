# Contributing to OpenRGD

First off, **thank you**.

By being here, you are not just looking at a repository; you are stepping into the engine room of the future. OpenRGD is not a product—it is a movement to give Artificial Intelligence a physical body, safely, openly, and democratically.

We believe that the interface between Cognitive Intelligence (LLMs) and Physical Reality (Robotics) must not belong to a single corporation. It must be a shared language—an open standard that anyone can use, audit, and improve.

By contributing to OpenRGD, you are helping to ensure that the robots of tomorrow are built on transparent, understandable foundations. You are building a better, more accessible future.

---

## Why Your Contribution Matters

Robotics is transitioning from hard‑coded logic to cognitive agents.

- If we leave this to closed silos, we risk a fragmented, opaque, and unsafe future.
- If we build it together, we democratize embodied AI.

Whether you fix a typo, propose a new sensor schema, or optimize our CLI parser, you’re adding a brick to the “Rosetta Stone” of robotics.

---

## How You Can Help

We welcome every kind of contribution. Choose the path that fits you best.

### 1. The Architect (Schema Proposals)

OpenRGD is a living standard. If you are an expert in a specific field (Soft Robotics, Drone Dynamics, Haptics, etc.) we need your insight.

- **Task:** Propose improvements to the JSONC definitions inside the `spec/` domains.
- **Method:** Open an issue titled `[RFC] Proposal for…` and describe the missing or incorrect area.
- **Goal:** Expand the `.rgd` format until it can describe any physical machine.

### 2. The Engineer (CLI & Tooling)

Our reference implementation (`src/cli.py`) must be robust and fail‑safe.

- **Task:** Improve the Python CLI, add validation rules, or build converters (e.g., URDF → RGD).
- **Method:** Fork the repository, write clean Python code, include tests, and open a PR.

### 3. The Scribe (Examples & Documentation)

A standard is only useful if people can use it.

- **Task:** Create `.rgd` files for known robots (Unitree, Spot, TurtleBot, Panda Arm) and place them in `examples/`.
- **Goal:** Show that OpenRGD supports real-world hardware.

---

## Become a Maintainer

We use a domain-based governance model led by specialists, not generalists.

If you consistently contribute to a specific area—such as `01_foundation`, `02_operation`, or `04_volition`—you may apply to become the **Official Maintainer** of that domain.

To apply, open an issue titled:

```
[MAINTAINER APPLICATION] Domain X
```

Your name will be recorded in the schema as the guardian of that domain.

---

## Submission Guidelines

1. **Fork & Branch:**  
   Create a branch for your contribution, for example:  
   `git checkout -b feature/amazing-idea`

2. **Commit Messages:**  
   Keep them clear and meaningful.

3. **Code Style:**  
   - **Python:** Follow PEP8.  
   - **JSONC:** Keep comments helpful; ensure the structure validates.

4. **Pull Request:**  
   Submit your PR to the `main` branch and explain why the change is needed.

---

## A Note on “Heart”

Technical excellence matters, but intent matters more. This project is built for humanity.  
Be respectful, help newcomers, and always keep safety in mind.

---

> *“The best way to predict the future is to invent it.  
> The best way to secure it is to open‑source it.”*

---

## OpenRGD Maintainers
