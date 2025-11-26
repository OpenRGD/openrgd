# 📤 OpenRGD Export Guide

The **`rgd export`** command acts as the "Semantic Bridge" (or Transpiler).
It transforms your high-level OpenRGD definition into low-level configuration files required by specific robotic ecosystems (ROS2, Isaac Sim, MuJoCo).

> **Philosophy:** "Define Once, Deploy Anywhere."
> You shouldn't have to manually write `ros2_control.yaml` or Python configuration classes. OpenRGD generates them from the single source of truth.

---

## 1. Supported Targets

The CLI uses a plugin-based architecture to support multiple ecosystems.

| Target | Output Format | Description |
| :--- | :--- | :--- |
| **ros2** | `.yaml`, `.xacro` | Generates `ros2_control` configuration and physical limits injection. |
| **isaac** | `.py` | Generates `ArticulationCfg` classes for Isaac Lab / Omniverse training. |
| **mujoco** | `.xml` | *(Coming Soon)* Generates MJCF physical definitions. |

---

## 2. Prerequisites: The Compilation Step

**CRITICAL:** Before exporting, you must compile your project.
The exporter does NOT read the raw `.jsonc` files directly. It reads the **Machine Twin** (`openrgd_unified_spec.json`) to ensure data integrity.

```bash
# 1. Enter your robot directory
cd MyRobot

# 2. Compile the spec (creates the Machine Twin)
rgd compile-spec

# 3. Now you can export
rgd export ros2
3. Usage & Workflows
A. Exporting for ROS2 (Real Hardware)
This generates the configuration needed to run the robot with ros2_control.

Bash

rgd export ros2
Output (export/ folder):

ros2_control.yaml: Defines the Controller Manager, update rate, and PID gains.

rgd_limits.xacro: Contains physical limits (torque, velocity, damping) as Xacro properties.

rgd_hardware.xacro: Defines the <ros2_control> tag with hardware drivers and CAN bus IDs.

How to use it in ROS2: In your robot's main URDF file:

XML

<robot xmlns:xacro="[http://www.ros.org/wiki/xacro](http://www.ros.org/wiki/xacro)">
  <xacro:include filename="$(find my_robot)/config/rgd_limits.xacro" />
  
  <joint name="knee_joint">
    <limit effort="${knee_joint_effort}" velocity="${knee_joint_velocity}" ... />
  </joint>
</robot>
B. Exporting for Isaac Lab (Simulation / RL)
This generates the Python class required to spawn the robot in NVIDIA Isaac Lab.

Bash

rgd export isaac
Output (export/ folder):

isaac_robot_cfg.py: A Python file containing the ArticulationCfg class.

Key Features:

Automatically groups joints by Control Profile (e.g., HEAVY_LEG, LIGHT_ARM).

Translates PID gains into Isaac's Stiffness/Damping model.

Sets the correct drive mode (FORCE vs ACCELERATION).

4. How Mapping Works
The exporter uses a "Smart Extract" logic to find the right values even if your JSON structure varies slightly.

Hierarchy of Truth
When generating a value (e.g., Max Torque), the bridge looks in this order:

Application Limits (in actuation_topology.jsonc) -> Highest priority (Software cap)

Physical Limits (in actuation_dynamics.jsonc) -> Hardware ceiling

Default Fallback -> Safe minimums (e.g. 0.0)

Inheritance
If you use Profiles in actuation_topology.jsonc (e.g., use_profile_ref_str: "heavy_leg"), the exporter automatically resolves the inheritance, applying any overrides you defined for that specific joint.

5. Troubleshooting
❌ "Machine Twin not found"
You forgot to run rgd compile-spec before exporting. The exporter needs the compiled JSON to guarantee it's using the latest valid data.

❌ "Critical: module missing"
Your specification is incomplete. Ensure you have 01_foundation/actuation_dynamics.jsonc and 01_foundation/actuation_topology.jsonc defined.

❌ Zero values in output
If your output files show value="0.0", check your variable names. The bridge looks for standard keys like torque_nm, effort, max_torque. If you used a custom key like my_custom_force_val, the bridge won't find it.