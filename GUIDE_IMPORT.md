# 📥 OpenRGD Import Guide

The **`rgd import`** command serves as the "Semantic Vacuum Cleaner."
It allows you to ingest legacy robot definitions (URDF, USD) and automatically transpile them into a valid OpenRGD **Foundation Domain**.

> **Philosophy:** We do not discard the past. We structure it.
> The importer extracts the *physical truth* (mass, limits, geometry) from your existing files and wraps it in the *cognitive context* of OpenRGD.

---

## 1. Supported Formats

The CLI currently supports the following industry standards via a lightweight, dependency-free parsing engine.

| Format | Extension | Engine Used | Notes |
| :--- | :--- | :--- | :--- |
| **URDF** | `.urdf`, `.xml` | `xml.etree` | The standard for ROS1/ROS2. Extracts Links and Joints. |
| **USD (ASCII)** | `.usda`, `.usd` | `regex` | Universal Scene Description (Isaac Sim). Must be text-based. |
| **USD (Zip)** | `.usdz` | `zipfile` + `regex` | Automatically extracts and parses `.usda` files inside the archive. |

---

## 2. Usage

The syntax is designed to be frictionless. You do not need to specify the format; the CLI detects it automatically based on the file extension.

### Basic Import
```bash
rgd import my_robot.urdf
Action: Creates a folder named my_robot/ containing the full OpenRGD structure (spec/00_core, spec/01_foundation, etc.) populated with data extracted from the URDF.

Custom Output Directory
Bash

rgd import assets/robot.usda --out ./projects/new_bot
Action: Saves the generated RGD definition into ./projects/new_bot.

3. Deep Dive: What gets imported?
The importer maps legacy concepts to the 01_FOUNDATION domain.

From URDF (.urdf)
<robot name="..."> → Becomes the Project Name and Kernel ID.

<link name="..."> → Populates kinematic_chain in description.jsonc.

<joint> Properties:

type → type_enum (revolute, prismatic, fixed).

<limit effort="..."> → torque_nm in actuation_dynamics.jsonc.

<limit velocity="..."> → velocity_rads.

<limit lower/upper="..."> → range_rad.

From USD / Isaac Sim (.usda, .usdz)
defaultPrim → Robot Name.

PhysicsRevoluteJoint → Actuator definitions.

drive:angular:physics:stiffness → Maps to advanced_impedance_model (PID tuning).

drive:angular:physics:damping → Maps to damping.

maxForce → Maps to torque_nm.

4. Troubleshooting & Limitations
⚠️ "Binary USD" Error
If you try to import a binary USD file (.usdc), the CLI will reject it:

❌ Critical: File is BINARY USD (.usdc). Cannot parse with lightweight importer.

Solution: You must convert the file to ASCII format using Pixar's tools (bundled with Isaac Sim or Maya):

Bash

# Convert binary to text
usdcat robot.usdc -o robot.usda

# Then import
rgd import robot.usda
⚠️ "No Joints Found"
If the importer runs but produces an empty actuation_dynamics.jsonc, your source file might define only visual meshes (geometry) without physical metadata (joints/limits).

URDF: Check that <joint> tags exist and are not just type="fixed".

USD: Ensure the stage has PhysicsAPI applied and joints are defined as PhysicsJoint, not just Xforms.

5. Post-Import Workflow
Importing is just the beginning ("Step 0"). Once ingested:

Enrich: Open spec/04_volition/alignment.jsonc and define the robot's mission (the importer creates a generic placeholder).

Compile: Run rgd compile-spec to generate the unified artifact.

Boot: Run rgd boot to see how the LLM interprets your imported physics.

Bash

# The "Magical" Sequence
rgd import frank.urdf
cd frank
rgd boot