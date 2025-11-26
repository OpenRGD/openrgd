import json
from pathlib import Path
from ..base import BaseSynapse  # Import aggiornato

class ROS2Synapse(BaseSynapse):
    """
    Connects OpenRGD to the ROS 2 Ecosystem.
    Generates: ros2_control.yaml, rgd_limits.xacro, rgd_hardware.xacro.
    """
    
    def generate(self, output_dir: Path) -> None:
        self.log(f"Extending neural pathways to ROS 2 for {self.robot_id}...")
        
        # 1. LOAD TWIN
        unified_path = self.spec_dir / "openrgd_unified_spec.json"
        if not unified_path.exists():
            self.log("❌ Machine Twin not found. Run 'rgd compile-spec' first.")
            return

        try:
            with open(unified_path, 'r', encoding='utf-8') as f:
                unified_data = json.load(f)
        except Exception as e:
            self.log(f"❌ Error reading Twin: {e}")
            return

        # 2. EXTRACT
        actuation_dynamics = None
        actuation_topology = None
        hal_mapping = None

        for module in unified_data.get("files", []):
            mid = module.get("id")
            if mid == "actuation_dynamics": actuation_dynamics = module.get("content")
            elif mid == "actuation_topology": actuation_topology = module.get("content")
            elif mid == "hal_mapping": hal_mapping = module.get("content")

        if not actuation_dynamics:
            self.log("❌ Critical: 'actuation_dynamics' missing.")
            return

        # 3. MERGE & MAP
        joints_map = {}
        
        # Flatten sources
        phys_data = self._find_joints_data(actuation_dynamics)
        topo_data = self._resolve_topology(actuation_topology)
        hal_data = hal_mapping.get("actuator_drivers_map", {}) if hal_mapping else {}

        all_keys = set(list(phys_data.keys()) + list(topo_data.keys()) + list(hal_data.keys()))
        
        for key in all_keys:
            if key in ["meta_group", "__doc__"]: continue
            
            p = phys_data.get(key, {})
            t = topo_data.get(key, {})
            h = hal_data.get(key, {})
            
            joint_name = t.get("target_joint_ref_str") or p.get("target_joint_ref_str") or h.get("logical_actuator_ref_str") or key
            
            joints_map[joint_name] = {"physics": p, "topology": t, "hal": h}

        self.log(f"Mapped {len(joints_map)} joints across Physics/Topology/HAL.")

        # 4. GENERATE
        self._generate_ros2_control_yaml(joints_map, output_dir)
        self._generate_limits_xacro(joints_map, output_dir)
        self._generate_hardware_xacro(joints_map, output_dir)

    # --- HELPERS (Gli stessi della v0.9 ma indentati nella classe) ---
    def _find_joints_data(self, content):
        if "joint_dynamics_map" in content: return content["joint_dynamics_map"]
        if "actuators" in content: return content["actuators"]
        return {k:v for k,v in content.items() if isinstance(v, dict) and "limits" in v}

    def _resolve_topology(self, topo):
        if not topo: return {}
        profiles = topo.get("control_profiles_map", {})
        instances = topo.get("joint_actuator_mapping_map", {})
        resolved = {}
        for k, v in instances.items():
            import copy
            base = copy.deepcopy(profiles.get(v.get("use_profile_ref_str"), {}))
            
            # Recursive update utility
            def update(d, u):
                for ki, vi in u.items():
                    if isinstance(vi, dict): d[ki] = update(d.get(ki, {}), vi)
                    else: d[ki] = vi
                return d
            
            update(base, v) # Merge instance over profile
            resolved[k] = base
        return resolved

    def _extract_val(self, data, keys, default=None):
        for k in keys:
            if k in data: return data[k]
            for sub in ["limits", "application_limits", "joint_limits", "control_defaults", "position_mode_gains"]:
                if sub in data and k in data[sub]: return data[sub][k]
        return default

    def _generate_ros2_control_yaml(self, joints_map, output_dir):
        lines = [f"# OPENRGD GENERATED: ROS2 CONTROL", "controller_manager:", "  ros__parameters:", "    update_rate: 100", 
                 "    joint_state_broadcaster:", "      type: joint_state_broadcaster/JointStateBroadcaster",
                 "    forward_position_controller:", "      type: position_controllers/JointGroupPositionController", "",
                 "forward_position_controller:", "  ros__parameters:", "    joints:"]
        for name in sorted(joints_map.keys()): lines.append(f"      - {name}")
        lines.append("    gains:")
        
        for name, data in joints_map.items():
            topo = data["topology"]
            p = self._extract_val(topo, ["kp_position_float", "kp"], 0.0)
            i = self._extract_val(topo, ["ki_position_float", "ki"], 0.0)
            d = self._extract_val(topo, ["kd_position_float", "kd"], 0.0)
            if p or i or d: lines.append(f"      {name}: {{p: {p}, i: {i}, d: {d}}}")
            
        with open(output_dir / "ros2_control.yaml", "w", encoding="utf-8") as f: f.write("\n".join(lines))
        self.log(f"✅ Config: ros2_control.yaml")

    def _generate_limits_xacro(self, joints_map, output_dir):
        lines = ['<?xml version="1.0"?>', '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">', '  ', '']
        for name, data in joints_map.items():
            phys = data["physics"]
            topo = data["topology"]
            eff = self._extract_val(topo, ["torque_limit_peak_nm_float", "effort"]) or self._extract_val(phys, ["max_torque_nm_float", "effort"], 0.0)
            vel = self._extract_val(topo, ["velocity_limit_rad_s_float", "velocity"]) or self._extract_val(phys, ["max_velocity_rad_s_float", "velocity"], 0.0)
            lower = self._extract_val(phys, ["soft_min_position_rad_float", "lower"], -3.14)
            upper = self._extract_val(phys, ["soft_max_position_rad_float", "upper"], 3.14)
            
            lines.append(f'  <xacro:property name="{name}_effort" value="{eff}" />')
            lines.append(f'  <xacro:property name="{name}_velocity" value="{vel}" />')
            lines.append(f'  <xacro:property name="{name}_lower" value="{lower}" />')
            lines.append(f'  <xacro:property name="{name}_upper" value="{upper}" />')
            lines.append('')
        lines.append('</robot>')
        with open(output_dir / "rgd_limits.xacro", "w", encoding="utf-8") as f: f.write("\n".join(lines))
        self.log(f"✅ Limits: rgd_limits.xacro")

    def _generate_hardware_xacro(self, joints_map, output_dir):
        lines = ['<?xml version="1.0"?>', '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">', '  <ros2_control name="OpenRGD" type="system">', '    <hardware>']
        plugin = "openrgd_ros2/GenericSystem"
        for d in joints_map.values():
            if "driver_plugin_str" in d["hal"]: plugin = d["hal"]["driver_plugin_str"]; break
        lines.append(f'      <plugin>{plugin}</plugin>'); lines.append('    </hardware>')
        
        for name, data in joints_map.items():
            hal = data["hal"]
            can_id = self._extract_val(hal, ["device_node_id_int", "can_id"], 0)
            lines.append(f'    <joint name="{name}">')
            lines.append(f'      <param name="can_id">{can_id}</param>')
            lines.append('      <state_interface name="position"/>')
            lines.append('      <command_interface name="position"/>')
            lines.append('    </joint>')
        lines.append('  </ros2_control>'); lines.append('</robot>')
        with open(output_dir / "rgd_hardware.xacro", "w", encoding="utf-8") as f: f.write("\n".join(lines))
        self.log(f"✅ Drivers: rgd_hardware.xacro")