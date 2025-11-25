import json
import copy
from pathlib import Path
from ..base import BaseBridge

class ROS2Bridge(BaseBridge):
    """
    Transforms OpenRGD definitions into ROS2 ecosystem files.
    v0.9: Supports Control Profiles (Inheritance) & Full Stack Mapping.
    """
    
    def generate(self, output_dir: Path) -> None:
        self.log(f"Transpiling identity {self.robot_id} to ROS2 format...")
        
        # 1. LOAD UNIFIED SPEC
        unified_path = self.spec_dir / "openrgd_unified_spec.json"
        if not unified_path.exists():
            self.log("❌ Machine Twin not found. Run 'rgd compile-spec' first.")
            return

        try:
            with open(unified_path, 'r', encoding='utf-8') as f:
                unified_data = json.load(f)
        except Exception as e:
            self.log(f"❌ Error reading Machine Twin: {e}")
            return

        # 2. EXTRACT MODULES
        actuation_dynamics = None
        actuation_topology = None
        hal_mapping = None

        for module in unified_data.get("files", []):
            mid = module.get("id")
            if mid == "actuation_dynamics": actuation_dynamics = module.get("content")
            elif mid == "actuation_topology": actuation_topology = module.get("content")
            elif mid == "hal_mapping": hal_mapping = module.get("content")

        if not actuation_dynamics:
            self.log("❌ Critical: 'actuation_dynamics' module missing.")
            return

        # 3. RESOLVE TOPOLOGY INHERITANCE
        # Before merging, we must expand all profiles in the topology.
        resolved_topology = self._expand_profiles(actuation_topology)

        # 4. MERGE DATA INTO MASTER JOINTS MAP
        # Key = Joint Name, Value = {physics:..., topology:..., hal:...}
        joints_map = {}
        
        # A. Physics (Source of Truth for hard limits)
        phys_data = self._find_joints_data(actuation_dynamics)
        
        # B. Topology (Source of Truth for control gains & inheritance)
        topo_data = resolved_topology.get("joint_actuator_mapping_map", {})

        # C. HAL (Source of Truth for drivers/CAN IDs)
        hal_data = hal_mapping.get("actuator_drivers_map", {}) if hal_mapping else {}

        # Collect all unique keys
        all_keys = set(list(phys_data.keys()) + list(topo_data.keys()) + list(hal_data.keys()))
        
        for key in all_keys:
            if key in ["meta_group", "__doc__"]: continue
            
            p = phys_data.get(key, {})
            t = topo_data.get(key, {})
            h = hal_data.get(key, {})
            
            # Resolve logical joint name
            joint_name = t.get("target_joint_ref_str") or p.get("target_joint_ref_str") or h.get("logical_actuator_ref_str") or key
            
            joints_map[joint_name] = {
                "physics": p,
                "topology": t,
                "hal": h
            }

        self.log(f"Mapped {len(joints_map)} joints with resolved inheritance.")

        # 5. GENERATE ARTIFACTS
        self._generate_ros2_control_yaml(joints_map, output_dir)
        self._generate_limits_xacro(joints_map, output_dir)
        self._generate_hardware_xacro(joints_map, output_dir)

    def _find_joints_data(self, content: dict) -> dict:
        """Helper to find joint definitions in nested structures."""
        if "joint_dynamics_map" in content: return content["joint_dynamics_map"]
        if "actuators" in content: return content["actuators"]
        # Flatten/Filter fallback
        valid = {}
        for k, v in content.items():
            if k not in ["meta_group", "__doc__"] and isinstance(v, dict):
                valid[k] = v
        return valid

    def _expand_profiles(self, topology_content: dict) -> dict:
        """
        Resolves inheritance: Instance > Overrides > Profile.
        Returns a new topology dictionary with fully expanded instances.
        """
        if not topology_content: return {}
        
        profiles = topology_content.get("control_profiles_map", {})
        instances = topology_content.get("joint_actuator_mapping_map", {})
        
        expanded_instances = {}
        
        for key, instance_data in instances.items():
            # 1. Start with empty base
            final_data = {}
            
            # 2. Check for profile usage
            profile_id = instance_data.get("use_profile_ref_str")
            if profile_id and profile_id in profiles:
                # Deep copy the profile data first
                final_data = copy.deepcopy(profiles[profile_id])
            
            # 3. Apply Instance Data (Overwriting profile)
            # We need a recursive update for nested dicts like "control_defaults"
            self._recursive_update(final_data, instance_data)
            
            # 4. Handle explicit "overrides" block if present (legacy support)
            if "overrides" in instance_data:
                self._recursive_update(final_data, instance_data["overrides"])
                
            expanded_instances[key] = final_data

        # Return a structure mimicking the original but expanded
        return {"joint_actuator_mapping_map": expanded_instances}

    def _recursive_update(self, d, u):
        """Updates dict d with u recursively."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._recursive_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _extract_val(self, data, keys, default=None):
        """Helper to find value deep in dict using list of possible keys."""
        # 1. Direct search
        for k in keys:
            if k in data: return data[k]
        
        # 2. Nested search in common containers
        sub_containers = [
            "limits", "application_limits", "joint_limits", 
            "control_defaults", "position_mode_gains", "velocity_mode_gains", 
            "advanced_impedance_model", "transmission_config"
        ]
        for sub in sub_containers:
            if sub in data and isinstance(data[sub], dict):
                for k in keys:
                    if k in data[sub]: return data[sub][k]
        return default

    def _generate_ros2_control_yaml(self, joints_map, output_dir):
        """Creates the PID and Controller Config."""
        lines = [
            f"# GENERATED BY OPENRGD BRIDGE v0.9",
            f"# Robot ID: {self.robot_id}",
            "",
            "controller_manager:",
            "  ros__parameters:",
            "    update_rate: 100",
            "    joint_state_broadcaster:",
            "      type: joint_state_broadcaster/JointStateBroadcaster",
            "    forward_position_controller:",
            "      type: position_controllers/JointGroupPositionController",
            "",
            "forward_position_controller:",
            "  ros__parameters:",
            "    joints:"
        ]
        
        for name in sorted(joints_map.keys()):
            lines.append(f"      - {name}")
            
        lines.append("")
        lines.append("    gains:")
        
        for name, data in joints_map.items():
            topo = data["topology"]
            
            # Try to extract PID gains
            kp = self._extract_val(topo, ["kp_position_float", "kp"], 0.0)
            ki = self._extract_val(topo, ["ki_position_float", "ki"], 0.0)
            kd = self._extract_val(topo, ["kd_position_float", "kd"], 0.0)
            
            # If no PID found, check if Isaac Impedance model is present and convert
            if kp == 0 and kd == 0:
                 stiff = self._extract_val(topo, ["stiffness_nm_rad_float", "stiffness"], 0.0)
                 damp = self._extract_val(topo, ["damping_nms_rad_float", "damping"], 0.0)
                 if stiff > 0:
                     kp = stiff # Rough equivalence for P-controller
                     kd = damp

            if kp > 0 or kd > 0:
                lines.append(f"      {name}: {{p: {kp}, i: {ki}, d: {kd}}}")

        with open(output_dir / "ros2_control.yaml", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.log(f"✅ Generated Config: ros2_control.yaml")

    def _generate_limits_xacro(self, joints_map, output_dir):
        """Creates the Physics definitions."""
        lines = [
            '<?xml version="1.0"?>',
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">',
            f'  ',
            f'  ',
            ''
        ]
        
        for name, data in joints_map.items():
            phys = data["physics"]
            topo = data["topology"]
            
            # Priority: Application Limits (Topology) > Physical Limits (Physics)
            eff = self._extract_val(topo, ["torque_limit_peak_nm_float", "effort"]) or \
                  self._extract_val(phys, ["max_torque_nm_float", "effort"]) or 0.0
                  
            vel = self._extract_val(topo, ["velocity_limit_rad_s_float", "velocity"]) or \
                  self._extract_val(phys, ["max_velocity_rad_s_float", "velocity"]) or 0.0
            
            # Range comes from physics/description usually
            # Handle list range [min, max]
            range_val = self._extract_val(phys, ["soft_position_limits_rad", "range_rad", "range"])
            lower = -3.14
            upper = 3.14
            
            if range_val and isinstance(range_val, list):
                 lower = range_val[0]
                 upper = range_val[1]
            else:
                # Try individual keys
                lower = self._extract_val(phys, ["soft_min_position_rad_float", "lower"], -3.14)
                upper = self._extract_val(phys, ["soft_max_position_rad_float", "upper"], 3.14)
            
            # Dynamics
            damp = self._extract_val(phys, ["viscous_friction_nm_s_per_rad_float", "damping"], 0.0)
            fric = self._extract_val(phys, ["coulomb_friction_nm_float", "friction"], 0.0)

            lines.append(f'  ')
            lines.append(f'  <xacro:property name="{name}_effort" value="{eff}" />')
            lines.append(f'  <xacro:property name="{name}_velocity" value="{vel}" />')
            lines.append(f'  <xacro:property name="{name}_lower" value="{lower}" />')
            lines.append(f'  <xacro:property name="{name}_upper" value="{upper}" />')
            lines.append(f'  <xacro:property name="{name}_damping" value="{damp}" />')
            lines.append(f'  <xacro:property name="{name}_friction" value="{fric}" />')
            lines.append('')

        lines.append('</robot>')
        with open(output_dir / "rgd_limits.xacro", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.log(f"✅ Generated Limits: rgd_limits.xacro")

    def _generate_hardware_xacro(self, joints_map, output_dir):
        """Creates the <ros2_control> tag with hardware plugin config."""
        lines = [
            '<?xml version="1.0"?>',
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">',
            f'  ',
            '  <ros2_control name="OpenRGD_System" type="system">',
            '    <hardware>'
        ]
        
        # Find Plugin
        plugin_name = "openrgd_ros2_control/GenericSystem"
        for d in joints_map.values():
            p = self._extract_val(d["hal"], ["driver_plugin_str"])
            if p:
                plugin_name = p
                break
                
        lines.append(f'      <plugin>{plugin_name}</plugin>')
        lines.append('    </hardware>')
        
        for name, data in joints_map.items():
            hal = data["hal"]
            # Fallback extraction for HAL
            can_id = self._extract_val(hal, ["device_node_id_int", "id", "can_id"], 0)
            bus = self._extract_val(hal, ["bus_interface_str", "bus"], "can0")
            
            lines.append(f'    <joint name="{name}">')
            lines.append(f'      <param name="can_id">{can_id}</param>')
            lines.append(f'      <param name="bus">{bus}</param>')
            lines.append('      <command_interface name="position"/>')
            lines.append('      <state_interface name="position"/>')
            lines.append('      <state_interface name="velocity"/>')
            lines.append('      <state_interface name="effort"/>')
            lines.append('    </joint>')

        lines.append('  </ros2_control>')
        lines.append('</robot>')

        with open(output_dir / "rgd_hardware.xacro", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.log(f"✅ Generated Drivers: rgd_hardware.xacro")