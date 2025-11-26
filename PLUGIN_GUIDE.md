Extending the rgd CLI with Plugins

Welcome to the OpenRGD Plugin Guide – a friendly walkthrough on how to extend the rgd command-line interface with new capabilities, ideas, experiments, and even slightly wild features.

OpenRGD is built around a simple philosophy:

The Cognitive BIOS should be modular, hackable, and open to collaboration.
Anyone should be able to add new commands to the ecosystem—without touching the core.

This guide shows you how to build such plugins, from tiny helpers to ambitious add-ons that explore the frontier of robotics meta-systems.

And if you build something cool, consider contributing it back to the project.
Let’s grow the OpenRGD standard together.

Why Plugins?

Because a standard thrives when it’s extensible.

Plugins let you:

Add entire groups of custom commands

Integrate research tools, simulators, dashboards, or validators

Experiment with alternative governance, safety or alignment flows

Prototype new functionality without modifying the core repository

Share your work with others through a Python package

If you know basic Python, you already know enough.

Quick Overview

The rgd CLI works like a command bus.
Plugins are simply:

A small Python module with:

app = typer.Typer(...)

One or more commands

An attach(root) function

An entry point in your pyproject.toml:

[project.entry-points."rgd.commands"]
"my-plugin-name" = "my_module.cli:attach"


When rgd starts, it automatically discovers and loads all plugins.
No extra configuration. No hacking the core.

1. Creating a Plugin (Internal Version)

If you are working inside the OpenRGD repository (e.g. contributing directly), create a new command module under:

src/openrgd/commands/


Example file: src/openrgd/commands/hello.py

import typer

app = typer.Typer(help="Friendly demo commands for OpenRGD.")

PLUGIN_NAME = "hello"  # Optional hint for the registry


@app.command("say")
def say_hello(name: str = "world"):
    """A friendly example command."""
    print(f"[OpenRGD] Hello, {name}!")


def attach(root: typer.Typer) -> None:
    """Attach this command group to the root CLI."""
    root.add_typer(app, name="hello")


Now add it to the list of built-in modules in:

src/openrgd/core/command_registry.py

BUILTIN_COMMAND_MODULES = [
    "openrgd.commands.compiler",
    "openrgd.commands.integrity",
    "openrgd.commands.hello",
]


Run it:

rgd hello say
rgd hello say --name Paky


Plugin created.
Plugin loaded.
Robot greeted.

2. Creating an External Plugin (Recommended)

This is the most powerful and future-proof approach.
You create a standalone Python package that anyone can install:

pip install rgd-awesome-tools


OpenRGD will detect it automatically.

2.1. Project Structure
rgd-awesome-tools/
  pyproject.toml
  src/
    rgd_awesome_tools/
      __init__.py
      cli.py

2.2. Plugin Code (cli.py)
import typer

app = typer.Typer(help="Awesome tools that extend the RGD ecosystem.")


def attach(root: typer.Typer) -> None:
    """
    Entry point for the plugin system.
    Exposes commands under:
        rgd awesome <command>
    """
    root.add_typer(app, name="awesome")


@app.command("ping")
def ping():
    """Tiny diagnostic command."""
    print("[Awesome] Pong from your plugin!")

2.3. Entry Point (pyproject.toml)
[project]
name = "rgd-awesome-tools"
version = "0.1.0"
description = "Awesome external plugin for OpenRGD"
requires-python = ">=3.8"
dependencies = ["openrgd>=0.1.0", "typer>=0.9.0"]

[project.entry-points."rgd.commands"]
"awesome" = "rgd_awesome_tools.cli:attach"

[tool.setuptools.packages.find]
where = ["src"]


Install it in development mode:

pip install -e .


Try it:

rgd awesome ping


You’ve just taught rgd a new trick.

3. Best Practices for Plugin Developers

Plugins should be:

Self-contained

Documented (short --help messages make a big difference)

Named cleanly (e.g., rgd-lab-tools, not rgd_plugin_thing_v2)

Modular (prefer a command group over a flat single command)

Non-invasive (no monkey patches, no global overrides)

If you create something that could benefit the community, open a PR or propose it as an optional official plugin. OpenRGD thrives on open collaboration.

4. Plugin Ideas (Fun + Useful)

Here are some imaginative (yet doable) plugin concepts.
If one inspires you—build it and send us a pull request.

🚀 4.1. Time Travel Plugin

Name: rgd-timetravel
What it does:
Creates time-stamped “snapshots” of the robot’s cognitive BIOS and lets operators travel between versions.

Commands you might expose:

rgd timetravel snapshot
rgd timetravel diff --from v12 --to v15
rgd timetravel checkout --id v09


Great for auditing, forensics, research and teaching your robot its own history.

🤝 4.2. Social-Score Plugin

Name: rgd-socialscore
What it does:
Calculates and displays the social weight matrix of entities that the robot knows, based on the Volition domain (04_).

Outputs might include:

rgd socialscore matrix


Which could show a table such as:

Entity	Trust	Reciprocity	Priority
Human-Owner	0.95	0.88	High
Child-Guest	0.93	0.91	Highest
Pet-Cat	0.40	0.70	Medium
Delivery-Bot	0.20	0.10	Low

Great for experimenting with alignment, safety, and multi-agent social modeling.

⚡ 4.3 Chaos Lab Plugin

Name: rgd-chaoslab
What it does:
Applies controlled disturbances and stress tests to the robot’s specification.

Examples:

rgd chaoslab inject --noise 0.3 --sensor imu
rgd chaoslab degrade --actuator left_leg
rgd chaoslab score


Useful for evaluating robustness and recovery strategies.

🧪 4.4. Specification Mutation Plugin

Name: rgd-mutator
A “creative mode” plugin that applies controlled mutations to the spec:

randomize joint limits (small safe deltas)

generate alternative self-model candidates

simulate capability degradation

explore speculative futures (“what if the robot grows a second arm?”)

Perfect for researchers and those who like breaking things to understand them.

🌐 4.5. Reality Mirror Plugin

Name: rgd-realitymirror
Reads real sensor/state logs and compares them against the robot’s internal model:

rgd realitymirror check
rgd realitymirror drift


Detects self-model drift, calibration issues, or hardware inconsistencies.

5. Contributing Plugins to OpenRGD

If you build something useful, inspiring, or even delightfully eccentric:

Open a PR

Submit it as an optional plugin

Or propose it as a standard extension

OpenRGD thrives when developers push its boundaries.

Your plugin might become part of the official tooling—or even help shape the direction of the standard itself.

6. Final Notes

Building a plugin is intentionally easy.
We want OpenRGD to feel like a playground for robotics tooling, not a locked-down monolith.

If you need any help, have ideas, or want to collaborate, reach out or open an issue on GitHub.

Let’s build the Cognitive BIOS together.
One plugin at a time.