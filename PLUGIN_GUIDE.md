# Extending OpenRGD with Plugins

Welcome to the OpenRGD Plugin Guide — a friendly design guide for extending the `rgd` ecosystem with research tools, simulators, dashboards, validators and experimental ideas.

> **Current status:** the external plugin ABI is a design direction and is **not enabled in the canonical CLI yet**. This document is intentionally kept because extensibility is part of the project's vision. A plugin loader will be enabled only after its trust, isolation and compatibility contract is accepted and tested.

## Why Plugins?

Because a standard thrives when people can experiment around it without turning the core into a monolith.

Future plugins should make it possible to:

- add command groups;
- integrate simulators and hardware ecosystems;
- build visualization and validation tools;
- prototype new research ideas;
- keep experimental work outside the canonical standard until it matures.

## Proposed Python Entry Point

The intended model is a normal Python package with a Typer command group and an explicit entry point:

```toml
[project.entry-points."rgd.commands"]
awesome = "rgd_awesome_tools.cli:attach"
```

```python
import typer

app = typer.Typer(help="Awesome OpenRGD tools")

@app.command("ping")
def ping():
    print("Pong from an OpenRGD plugin")

def attach(root: typer.Typer) -> None:
    root.add_typer(app, name="awesome")
```

Before this becomes active, the project still needs to freeze:

- plugin ABI/versioning;
- permission model;
- provenance/trust policy;
- failure isolation;
- rules for safety-affecting plugins;
- conformance tests.

## Ideas Worth Building

### ⏳ Time Travel
Snapshots and diffs of a robot's self-model.

### ⚡ Chaos Lab
Controlled degradation and resilience testing.

### 🪞 Reality Mirror
Compare measured body state with the declared model and calibration.

### 🧪 Spec Mutation
Create controlled alternative body/profile candidates for simulation and research.

### 🌐 Simulator Bridges
Additional static or runtime adapters for ecosystems beyond the current ROS 2 static exporter.

The point of this guide is not to pretend these plugins already exist. It is to keep the door visibly open.

If you want to help turn the plugin model into a real, safe ABI, open an RFC.
