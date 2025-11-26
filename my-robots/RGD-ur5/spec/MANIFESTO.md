# The OpenRGD Manifesto
**Grounding Artificial Intelligence in Physical Reality**

> "Intelligence without context is hallucination. Power without control is danger."

## 1. The Declaration
We stand at the threshold of the Embodied AI era. Large Language Models have solved the problem of *Cognition*, and traditional robotics has solved the problem of *Actuation*.

But a dangerous gap remains: **The Grounding Gap.**

Currently, AI models are "brains in a jar"—disconnected from the physical laws of the bodies they are meant to control. They hallucinate actions because they lack a standardized sense of self. Conversely, robots are "mindless bodies"—trapped in rigid scripts, unaware of their own capabilities.

**OpenRGD exists to bridge this gap.** We believe that the interface between a digital mind and a physical machine must be:
1.  **Semantic:** Understandable by both humans and AI.
2.  **Universal:** Agnostic to hardware brand or model architecture.
3.  **Open:** A public good, not a proprietary walled garden.

## 2. Our Core Principles

### I. Identity is Safety
A robot cannot operate safely if it does not know what it is.
Safety constraints (speed limits, torque limits, ethical boundaries) must not be buried in obscure Python code or proprietary firmware. They must be declared explicitly in the robot's **Definition File (.rgd)**.
* *The Principle:* The AI must read the safety rules *before* it plans the action.

### II. The "Cognitive BIOS"
We do not seek to replace operating systems like ROS or Linux. We seek to provide the **BIOS** for higher-level intelligence.
Just as a computer's BIOS tells the OS what hardware is present, OpenRGD tells the Cognitive Agent (LLM/VLA) what body it inhabits. It provides the "prompt context" required for Zero-Shot Embodiment.

### III. No Black Boxes
The definitions of physical capabilities and ethical constraints must be transparent.
* **Foundation (Hardware)** must be exposed.
* **Operation (Safety)** must be auditable.
* **Volition (Ethics)** must be configurable.
We reject the idea of "magic" proprietary drivers that hide the robot's true nature from its user.

### IV. Democratization of Embodiment
The ability to deploy advanced AI on robotic hardware should not be the privilege of a few mega-corporations. By creating an open standard, we lower the barrier to entry.
* A student in a garage should be able to write an `.rgd` file for a custom 3D-printed arm.
* A researcher should be able to swap a robot's brain (Model A to Model B) without rewriting the body's drivers.

## 3. The Architecture of Life
We organize the complexity of artificial life into six universal domains. This is not just a file format; it is a taxonomy for existence:

1.  **Foundation:** The immutable physics of the body.
2.  **Operation:** The physiological rules of survival and safety.
3.  **Agency:** The library of capabilities and skills.
4.  **Volition:** The alignment of intent and ethics.
5.  **Evolution:** The capacity to learn and adapt over time.
6.  **Ether:** The connection to the swarm and society.

## 4. The Future We Build
We envision a future where robots are helpful, safe, and intelligible partners in human society. To achieve this, we cannot build on quicksand. We need a solid foundation.

**OpenRGD is that foundation.**

It is the shared language that allows the digital world to touch the physical world without breaking it.

### The Initiative

**Original Architect:** Pasquale Ranieri (@phate6872)
**Maintained by:** The OpenRGD Community