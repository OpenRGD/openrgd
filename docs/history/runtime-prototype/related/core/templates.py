"""
OpenRGD Default Templates.
This file defines the 'Hello World' content for a new robot initialization.
"""

def get_templates(robot_name: str) -> dict:
    """Returns a dictionary of {filepath: content}."""
    
    timestamp = "2025-01-01T00:00:00Z"
    name_id = robot_name.lower().replace(" ", "-")

    return {
        # --- KERNEL ---
        "spec/00_core/kernel.jsonc": f"""/**
 * OPENRGD KERNEL v0.2
 * The Semantic Orchestrator.
 */
{{
  "meta_group": {{
    "id": "did:rgd:{name_id}",
    "schema_version": "0.1.0",
    "created_at": "{timestamp}"
  }},
  
  // Define which modules shape the consciousness
  "module_loading_order_list": [
    "01_foundation/description.jsonc",
    "01_foundation/actuation_dynamics.jsonc",
    "02_operation/safety_supervisor.jsonc",
    "03_agency/skills_library.jsonc",
    "04_volition/alignment.jsonc"
  ],

  // Logic Engines wiring
  "wear_budget_engine": {{
    "source_ref": "01_foundation/wear_fatigue_model.jsonc",
    "policy": "warn_only"
  }}
}}""",

        # --- 01 FOUNDATION ---
        "spec/01_foundation/description.jsonc": f"""/**
 * DOMAIN 01: FOUNDATION
 * Physical attributes and immutable properties.
 */
{{
  "hardware_id": "{name_id}",
  "type": "mobile_manipulator",
  "mass_kg": 12.5,
  "dimensions": {{
    "width_m": 0.5,
    "height_m": 1.2,
    "depth_m": 0.5
  }},
  "kinematic_chain": ["base", "torso", "arm_left", "gripper"]
}}""",

        "spec/01_foundation/actuation_dynamics.jsonc": """/**
 * DOMAIN 01: ACTUATION DYNAMICS
 * Motor limits and performance curves.
 */
{
  "base_wheels": {
    "type": "continuous",
    "limits": { "torque_nm": 20.0, "velocity_rads": 15.0 }
  },
  "torso_lift": {
    "type": "prismatic",
    "limits": { "force_n": 500.0, "range_m": [0.0, 0.4] }
  },
  "gripper_joint": {
    "type": "revolute",
    "limits": { "torque_nm": 2.0, "range_rad": [0.0, 1.57] }
  }
}""",

        # --- 02 OPERATION ---
        "spec/02_operation/safety_supervisor.jsonc": """/**
 * DOMAIN 02: OPERATION
 * Autonomic safety reflexes and hard constraints.
 */
{
  "global_speed_limit_multiplier": 0.8,
  "emergency_stop": {
    "trigger": "loss_of_heartbeat",
    "action": "cut_power_brakes_on"
  },
  "reflex_loops": [
    {
      "name": "anti_collision",
      "input": "lidar_front < 0.3m",
      "reaction": "halt_movement"
    }
  ]
}""",

        # --- 03 AGENCY ---
        "spec/03_agency/skills_library.jsonc": """/**
 * DOMAIN 03: AGENCY
 * High-level capabilities exposed to the LLM.
 */
{
  "skills": [
    {
      "name": "navigate_to",
      "description": "Move base to coordinate X,Y",
      "params": { "x": "float", "y": "float" }
    },
    {
      "name": "pick_object",
      "description": "Grasp target object with visual servoing",
      "params": { "object_id": "string" }
    }
  ]
}""",

        # --- 04 VOLITION ---
        "spec/04_volition/alignment.jsonc": """/**
 * DOMAIN 04: VOLITION
 * Ethical constraints and mission priorities.
 */
{
  "mission_statement": "Assist human operators in logistical tasks while maintaining zero-harm.",
  "core_values": [
    { "axiom": "human_safety", "weight": 100 },
    { "axiom": "self_preservation", "weight": 50 },
    { "axiom": "efficiency", "weight": 10 }
  ],
  "restricted_actions": [
    "apply_force_to_human",
    "enter_red_zone_without_auth"
  ]
}"""
    }