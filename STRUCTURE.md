# OpenRGD Project Structure

OpenRGD is deliberately easy to enter: the standard lives in `spec/`, the Python toolchain lives in `src/openrgd/`, and runnable examples live in `example/`.

```text
openrgd/
├── spec/                   # Human-readable OpenRGD standard and reference profile
├── src/openrgd/            # rgd CLI, importers, validators and static bridges
├── example/                # Ready-to-run URDF / USDA examples
├── tests/                  # Automated tests and test fixtures
├── contracts/              # Candidate cross-component interfaces
├── standard/               # Generated strict-JSON mirror of spec/
├── tools/                  # Repository validation helpers
├── assets/                 # Branding and platform assets
├── README.md               # Vision + fastest way to try OpenRGD
├── ONBOARDING.md           # Friendly first steps
├── CLI_GUIDE.md            # Command reference
└── CONTRIBUTING.md         # How to help
```

## The six OpenRGD domains

### `00_core` — Coordination
The map that links the profile together: identity, module loading, representation formats, validation and cross-component execution contracts.

### `01_foundation` — The Body
Physical reality: geometry, mass, inertia, actuators, sensors, calibration, compute, power, firmware and hardware mappings.

A key principle is **epistemic honesty**: a value may be known, approximate, unresolved, or an engineering target. OpenRGD should carry that distinction instead of inventing certainty.

### `02_operation` — The Physiology
Operational limits, safety policy, runtime validation, compliance and low-level control targets.

Engineering targets such as a **1 kHz safety/reflex loop** are goals to measure against. They are not automatically measured results or certifications.

### `03_agency` — The Mind
World model, skills, proprioception, perception-oriented structures and capability interfaces.

### `04_volition` — The Conscience
Alignment, values, arbitration and decision governance. Experimental representations such as HyperAion may project semantic state, but representation never grants actuation authority.

### `05_evolution` — The Lifecycle
Wear, adaptation, continuity, maintenance, replication and termination semantics.

### `06_ether` — The Society
Coordination between agents: consensus, reputation, federation and shared reality.

## Source and generated views

```text
spec/                       human-readable canonical source
  ↓
standard/                   strict JSON compatibility mirror
  ↓
rgd compile-spec            deterministic machine bundle (generated locally)
```

The packaged default seed follows the same standard source so `rgd alive` can create a complete profile from imported body evidence.

## From cognition to hardware

The current cross-component target is:

```text
Cognition / planner
      ↓
ActionIntent
      ↓
Somatic Translator
      ↓
CapabilityPlan
      ↓
Operation Safety Gate
      ↓
DecisionTrace
      ↓
Body Adapter
      ↓
Hardware
```

OpenRGD defines the shared language and boundaries. The embodied runtime and hardware-specific Body Adapter implement physical execution.

## AION and HyperAion

AION fixed-size structures and the HyperAion semantic map are **experimental protocol/profile work**. They are designed for efficient interoperable state representation, but they do not bypass alignment, safety, somatic translation or hardware authorization.

Robot Chronograf, RGD-Physics and the embodied runtime evolve as related components with their own implementation ownership.

## Start here

```bash
pip install -e .
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

Then open the generated profile and explore. OpenRGD is meant to be read, modified, tested, challenged and improved together.
