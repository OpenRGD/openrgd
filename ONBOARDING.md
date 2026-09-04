# 🚀 Quick Start: From Zero to Alive

Welcome to OpenRGD.

You don't need to be a robotics expert to explore the standard. If you have a URDF or text USDA file, you already have enough to start.

## 1. Install

OpenRGD currently requires **Python 3.10+** and Git.

```bash
git clone https://github.com/OpenRGD/openrgd.git
cd openrgd
pip install -e .
rgd --help
```

## 2. Hello World: Bring a Robot Alive

The easiest path is the high-level workflow:

```bash
rgd alive example/minimal-arm/openrgd_minimal_arm.urdf
```

or:

```bash
rgd alive example/minimal-arm/openrgd_minimal_arm.usda
```

OpenRGD will create a robot profile under `my-robots/`, validate its canonical integrity, build its grounding context, compile the machine bundle and prepare the static ROS 2 bridge output.

That's the idea behind `alive`: **one source file in, an inspectable embodiment profile out.**

## 3. Look Under the Hood

After `rgd alive`, explore the generated project:

```text
my-robots/RGD-<robot>/
├── manifest.json
├── README.txt
├── spec/
└── export/ros2/
```

Then try the lower-level commands individually:

```bash
cd my-robots/RGD-openrgd_minimal_arm
rgd hash
rgd check
rgd boot
rgd compile-spec
rgd export ros2
```

## 4. Edit the DNA

Open a file such as:

```text
spec/01_foundation/actuation_topology.jsonc
```

You'll see how physical components, mounting, transmissions and limits are represented. OpenRGD is deliberately human-readable: the standard should be understandable by humans and machines together.

## 5. Build With Us

- Read `README.md` for the vision.
- Read `ENTHUSIAST.md` for ways to contribute.
- Read `GUIDE_IMPORT.md` and `GUIDE_EXPORT.md` for deeper tooling details.
- Read `STRUCTURE.md` when you want the architecture.

If something is confusing, that's useful information. Open an issue. Friendly tools are built by noticing friction.
