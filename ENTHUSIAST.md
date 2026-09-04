# 🔥 Join the Vanguard: The OpenRGD Enthusiast Guide

So, you've seen the vision. You understand that robots need more than code: they need a shared language for body, limits, capabilities, values, time and relationships.

**Welcome home.**

OpenRGD is not only for Python developers. We need roboticists, control engineers, researchers, philosophers, designers, writers, lawyers, educators, students and people who are simply fascinated by the future of embodied intelligence.

## 🚀 Level 1: Try It

Clone the repository and bring the included robot alive:

```bash
pip install -e .
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

Then open the generated JSONC files and see whether the representation makes sense to you.

If something is awkward, confusing or missing, tell us. That feedback is valuable.

## 🛠️ Level 2: Build & Break

Try your own URDF or USDA:

```bash
rgd alive your_robot.urdf
```

Questions worth exploring:

- Did the importer preserve the facts that matter?
- Which physical data was missing from the source?
- Could actuator models be matched automatically?
- Which values should remain unknown rather than guessed?
- Can another simulator or robot consume the resulting profile?

A failed experiment can be as valuable as a successful one.

## 🏛️ Level 3: Improve a Domain

OpenRGD spans six domains. Specialists are welcome to challenge them.

- Motor expert? Improve actuator and transmission representation.
- Controls engineer? Help us reach the 1 kHz safety/control targets responsibly.
- Roboticist? Improve proprioception, calibration and sim-to-real semantics.
- Security/safety specialist? Attack our assumptions.
- Philosopher or ethicist? Help make Volition precise rather than decorative.
- Distributed-systems researcher? Explore Ether, Chronograf and multi-agent coordination.

Open an RFC or pull request and explain the evidence behind the change.

## 🔮 Level 4: Draft the Future

Wild ideas are welcome when they are labelled honestly.

AION, HyperAion, Chronograf, native low-latency transports, swarm protocols and new forms of embodied memory all started as questions before they became specifications or code.

The rule is not “don't dream.” The rule is:

> **dream boldly, label maturity clearly, test what can be tested.**

## 💬 Participate

- GitHub Issues — bugs, ideas and RFCs
- GitHub Discussions — conversation and community
- Pull Requests — working proposals

If you're wondering whether your contribution is “important enough,” it probably is. Open standards become useful because many people look at them from different angles.

> *The best way to predict the future is to invent it. The best way to make it useful is to build it together.*

**Start now.**
