🚀 Quick Start: From Zero to Hero
Welcome to the OpenRGD initiative. This guide will help you install the CLI, set up your environment, and generate a full robotic stack (AI + ROS2 + Isaac) in less than 60 seconds.

You don't need to be a robotics expert. You just need the will to build.

1. Prerequisites (Dependencies)
OpenRGD is built on Python. To make the magic happen, you need:

Python 3.8+ (Type python --version to check).

Git (To download the source code).

> Note: Dependencies like typer and rich will be handled automatically.

2. Instant Installation (Developer Mode)
We believe in open boxes. We install the source code in "Editable Mode", so you can look under the hood.

Open your terminal and run these 3 commands:

Bash

# 1. Download the project
git clone https://github.com/OpenRGD/openrgd.git

# 2. Enter the headquarters
cd openrgd

# 3. Install the 'rgd' command into your system
pip install -e .
🎉 Done. Test it immediately by typing:

Bash

rgd --help
If you see the red OpenRGD logo, you are officially an Operator.

3. Hello World: Your First Robot
Let's create the consciousness for a machine. Let's define a robot named "Jarvis".

Step A: Genesis (init)
Choose a folder where you want to work and run:

Bash

rgd init Jarvis
🖥️ Initializing containment field... 🧬 Cloning Gold Standard Templates... ✅ Project ready in ./Jarvis

Step B: The Awakening (boot)
Enter your robot folder and verify its identity. This command generates the Cognitive Context for LLMs (GPT-4, Claude).

Bash

cd Jarvis
rgd boot
You will see the system loading the modules (01_foundation, 04_volition...) and presenting the Golden Panel with the robot's identity.

Step C: The Materialization (compile & export)
Now for the killer feature. Let's transform this abstract definition into real code for simulators and hardware.

Compile the Twin: Create a machine-readable unified artifact.

Bash

rgd compile-spec
(Creates spec/openrgd_unified_spec.json)

Bridge to Reality: Generate configuration files for ROS2 or Isaac Lab automatically.

Bash

rgd export ros2
(Check the export/ folder: you just generated ros2_control.yaml and rgd_limits.xacro without writing a line of code!)

4. Next Steps: Become an Architect
Now that you have a working robot stack:

Open spec/01_foundation/actuation_dynamics.jsonc with VS Code.

Change the torque of a joint.

Run rgd export isaac to generate a new Python class for simulation.

You have just edited the DNA of a machine.

🆘 Troubleshooting
"Command 'rgd' not found?" Python is likely not in your PATH.

Fast Fix: Use python -m src.openrgd.main boot instead of rgd boot.

Real Fix: Reinstall Python and check "Add Python to PATH", or follow CLI_GUIDE.md.

"ImportError: No module named bridges?" If you just updated the code, run pip install -e . again to refresh the package map.

"How do I uninstall?" We hope you won't need to, but just in case: pip uninstall openrgd