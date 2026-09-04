# OpenRGD CLI: Operator's Manual

The `rgd` CLI turns OpenRGD from a specification you can read into something you can try.

## ⚡ The command to remember: `rgd alive`

```bash
rgd alive robot.urdf
```

or:

```bash
rgd alive robot.usda
```

`alive` performs the normal OpenRGD workflow automatically:

```text
import evidence
→ enrich with seed
→ canonical hash
→ check
→ grounding/boot context
→ compile machine bundle
→ static ROS 2 export
```

By default the generated project is written under:

```text
my-robots/RGD-<robot-name>/
```

Use `--out` to choose another directory.

## Installation

```bash
pip install -e .
rgd --help
```

Python 3.10+ is required.

## Lower-level commands

### `rgd import`
Extract only source-supported evidence from URDF or text USDA.

### `rgd init NAME`
Create a project directly from the packaged OpenRGD seed.

### `rgd hash`
Verify or intentionally update the canonical source-tree hash.

### `rgd check`
Validate profile integrity and kernel-selected modules.

### `rgd boot`
Build the non-actuating grounding context used to understand the robot profile.

### `rgd compile-spec`
Create the deterministic machine-readable unified bundle.

### `rgd export ros2`
Generate static ROS 2 interoperability files. Hardware-specific output is emitted only when explicit HAL bindings are available.

### `rgd run`
The canonical repository does not contain the physical embodied runtime. Historical runtime subcommands remain fail-closed rather than pretending to actuate hardware.

## Quiet mode

```bash
rgd --quiet alive robot.urdf
```

Use quiet mode in CI and scripts.

## Engineering targets vs implementation claims

OpenRGD can describe ambitious runtime targets — including a 1 kHz safety/reflex loop — while the canonical CLI remains non-actuating. A target in the spec means “this is what compatible runtime implementations should work toward and measure,” not “the Python CLI already guarantees this.”
