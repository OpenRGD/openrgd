from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
from typing import Any

from ..base import BaseSynapse, SynapseGenerationError


_KNOWN_OUTPUTS = (
    "export_manifest.json",
    "rgd_hardware.xacro",
    "rgd_limits.xacro",
    "ros2_control.yaml",
)


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _first_number(*values: Any) -> float | None:
    for value in values:
        parsed = _number(value)
        if parsed is not None:
            return parsed
    return None


def _format_number(value: float) -> str:
    if value == 0:
        return "0"
    return format(value, ".15g")


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = deepcopy(value)
    return base


@dataclass(frozen=True)
class JointExport:
    name: str
    joint_type: str
    actuator_id: str | None
    lower: float | None
    upper: float | None
    velocity: float | None
    effort: float | None
    position_unit: str | None
    velocity_unit: str | None
    effort_unit: str | None
    kp: float | None
    ki: float | None
    kd: float | None
    driver_plugin: str | None
    interfaces: tuple[str, ...]
    device_node_id: int | None

    def manifest_record(self) -> dict[str, Any]:
        return {
            "actuator_id": self.actuator_id,
            "device_node_id": self.device_node_id,
            "driver_plugin": self.driver_plugin,
            "effort_limit": self.effort,
            "effort_unit": self.effort_unit,
            "interfaces": list(self.interfaces),
            "joint_name": self.name,
            "joint_type": self.joint_type,
            "position_lower": self.lower,
            "position_unit": self.position_unit,
            "position_upper": self.upper,
            "velocity_limit": self.velocity,
            "velocity_unit": self.velocity_unit,
        }


class ROS2Synapse(BaseSynapse):
    """Generate deterministic, non-actuating ROS 2 configuration artifacts."""

    target_name = "ros2"

    def generate(self, output_dir: Path) -> dict[str, Any]:
        bundle, bundle_sha256 = self.load_machine_bundle()

        description = self.module_content(bundle, "description", required=True)
        dynamics = self.module_content(
            bundle,
            "actuation_dynamics",
            required=True,
        )
        topology = self.module_content(bundle, "actuation_topology")
        hal_mapping = self.module_content(bundle, "hal_mapping")

        joints = self._build_joint_records(
            description=description,
            dynamics=dynamics,
            topology=topology,
            hal_mapping=hal_mapping,
        )
        if not joints:
            raise SynapseGenerationError(
                "no non-fixed joints were found in the compiled profile"
            )

        missing_hardware = sorted(
            joint.name
            for joint in joints
            if not joint.driver_plugin or not joint.interfaces
        )
        plugins = sorted(
            {
                joint.driver_plugin
                for joint in joints
                if joint.driver_plugin is not None
            }
        )

        hardware_complete = not missing_hardware and len(plugins) == 1
        if missing_hardware:
            hardware_reason = "MISSING_EXPLICIT_HAL_BINDINGS"
        elif len(plugins) > 1:
            hardware_reason = "MULTIPLE_SYSTEM_PLUGINS_REQUIRE_EXPLICIT_COMPOSITION"
        elif len(plugins) == 0:
            hardware_reason = "NO_HAL_DRIVER_PLUGIN"
        else:
            hardware_reason = "COMPLETE"

        status = "HARDWARE_BOUND" if hardware_complete else "CONFIGURATION_ONLY"
        output_dir.mkdir(parents=True, exist_ok=True)
        for name in _KNOWN_OUTPUTS:
            path = output_dir / name
            if path.exists():
                path.unlink()

        generated: list[str] = []

        control_path = output_dir / "ros2_control.yaml"
        control_path.write_text(
            self._render_ros2_control(
                joints,
                bundle_root=bundle["meta"]["bundle_integrity_hash"],
                status=status,
            ),
            encoding="utf-8",
            newline="\n",
        )
        generated.append(control_path.name)

        limits_path = output_dir / "rgd_limits.xacro"
        limits_path.write_text(
            self._render_limits_xacro(
                joints,
                bundle_root=bundle["meta"]["bundle_integrity_hash"],
            ),
            encoding="utf-8",
            newline="\n",
        )
        generated.append(limits_path.name)

        if hardware_complete:
            hardware_path = output_dir / "rgd_hardware.xacro"
            hardware_path.write_text(
                self._render_hardware_xacro(
                    joints,
                    driver_plugin=plugins[0],
                    bundle_root=bundle["meta"]["bundle_integrity_hash"],
                ),
                encoding="utf-8",
                newline="\n",
            )
            generated.append(hardware_path.name)

        manifest_path = output_dir / "export_manifest.json"
        generated_with_manifest = sorted([*generated, manifest_path.name])
        manifest = {
            "artifact_type": "OPENRGD_STATIC_ROS2_EXPORT",
            "bundle_integrity_hash": bundle["meta"]["bundle_integrity_hash"],
            "generated_files": generated_with_manifest,
            "hardware_binding": {
                "complete": hardware_complete,
                "driver_plugins": plugins,
                "missing_joint_bindings": missing_hardware,
                "reason": hardware_reason,
            },
            "joint_count": len(joints),
            "joints": [joint.manifest_record() for joint in joints],
            "robot_id": self.robot_id,
            "source_bundle_sha256": f"sha256:{bundle_sha256}",
            "status": status,
            "target": "ROS2",
        }
        manifest_path.write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        return {
            "generated_files": generated_with_manifest,
            "hardware_binding_complete": hardware_complete,
            "output_dir": str(output_dir),
            "status": status,
            "target": "ros2",
        }

    def _build_joint_records(
        self,
        *,
        description: dict[str, Any],
        dynamics: dict[str, Any],
        topology: dict[str, Any],
        hal_mapping: dict[str, Any],
    ) -> list[JointExport]:
        description_map = description.get("joint_topology_map", {})
        if not isinstance(description_map, dict):
            description_map = {}

        topology_by_joint = self._topology_by_joint(topology)
        dynamics_by_joint = self._dynamics_by_joint(dynamics)
        hal_by_actuator = self._hal_by_actuator(hal_mapping)

        description_meta = description.get("meta_group", {})
        imported_partial = (
            isinstance(description_meta, dict)
            and description_meta.get("file_role_enum")
            == "IMPORTED_PARTIAL_DESCRIPTION"
        )

        if imported_partial and description_map:
            names = {
                name
                for name, record in description_map.items()
                if isinstance(record, dict)
                and str(record.get("type_enum", "")).upper() != "FIXED"
            }
        else:
            names = {
                name
                for name, record in description_map.items()
                if isinstance(record, dict)
                and str(record.get("type_enum", "")).upper() != "FIXED"
            }
            names.update(topology_by_joint)
            names.update(dynamics_by_joint)

        records: list[JointExport] = []
        for name in sorted(names):
            desc = (
                description_map.get(name, {})
                if isinstance(description_map.get(name), dict)
                else {}
            )
            topo = topology_by_joint.get(name, {})
            dynamic = dynamics_by_joint.get(name, {})

            joint_type = str(
                desc.get("type_enum")
                or dynamic.get("joint_type_enum")
                or "UNSPECIFIED"
            ).upper()
            if joint_type == "FIXED":
                continue

            desc_limits = (
                desc.get("limits_ideal", {})
                if isinstance(desc.get("limits_ideal"), dict)
                else {}
            )
            dynamic_limits = (
                dynamic.get("joint_limits", {})
                if isinstance(dynamic.get("joint_limits"), dict)
                else {}
            )
            application_limits = (
                topo.get("application_limits", {})
                if isinstance(topo.get("application_limits"), dict)
                else {}
            )
            legacy_limits = (
                dynamic.get("limits", {})
                if isinstance(dynamic.get("limits"), dict)
                else {}
            )

            if joint_type == "PRISMATIC":
                lower = _first_number(
                    desc_limits.get("position_lower_m_float"),
                    dynamic_limits.get("soft_min_position_m_float"),
                    legacy_limits.get("lower"),
                )
                upper = _first_number(
                    desc_limits.get("position_upper_m_float"),
                    dynamic_limits.get("soft_max_position_m_float"),
                    legacy_limits.get("upper"),
                )
                velocity = _first_number(
                    application_limits.get("velocity_limit_m_s_float"),
                    dynamic_limits.get("max_velocity_m_s_float"),
                    desc_limits.get("velocity_max_m_s_float"),
                    legacy_limits.get("velocity"),
                )
                effort = _first_number(
                    application_limits.get("force_limit_peak_n_float"),
                    dynamic_limits.get("max_effort_n_float"),
                    desc_limits.get("effort_max_n_float"),
                    legacy_limits.get("effort"),
                )
                position_unit = "m"
                velocity_unit = "m/s"
                effort_unit = "N"
            else:
                range_rad = legacy_limits.get("range_rad")
                legacy_lower = (
                    range_rad[0]
                    if isinstance(range_rad, list) and len(range_rad) == 2
                    else None
                )
                legacy_upper = (
                    range_rad[1]
                    if isinstance(range_rad, list) and len(range_rad) == 2
                    else None
                )
                lower = _first_number(
                    desc_limits.get("position_lower_rad_float"),
                    dynamic_limits.get("soft_min_position_rad_float"),
                    legacy_limits.get("lower"),
                    legacy_lower,
                )
                upper = _first_number(
                    desc_limits.get("position_upper_rad_float"),
                    dynamic_limits.get("soft_max_position_rad_float"),
                    legacy_limits.get("upper"),
                    legacy_upper,
                )
                velocity = _first_number(
                    application_limits.get("velocity_limit_rad_s_float"),
                    dynamic_limits.get("max_velocity_rad_s_float"),
                    desc_limits.get("velocity_max_rad_s_float"),
                    legacy_limits.get("velocity"),
                    legacy_limits.get("velocity_rads"),
                )
                effort = _first_number(
                    application_limits.get("torque_limit_peak_nm_float"),
                    dynamic_limits.get("max_effort_nm_float"),
                    dynamic_limits.get("max_torque_nm_float"),
                    desc_limits.get("effort_max_nm_float"),
                    legacy_limits.get("effort"),
                    legacy_limits.get("torque_nm"),
                )
                position_unit = "rad"
                velocity_unit = "rad/s"
                effort_unit = "Nm"

            gains = self._position_gains(topo)
            actuator_id = topo.get("_actuator_id") or dynamic.get("_actuator_id")
            hal = (
                hal_by_actuator.get(str(actuator_id), {})
                if actuator_id is not None
                else {}
            )
            if not hal:
                hal = hal_by_actuator.get(name, {})

            raw_interfaces = hal.get("ros2_control_interface_list_enum", [])
            interfaces = (
                tuple(sorted(str(item) for item in raw_interfaces))
                if isinstance(raw_interfaces, list)
                else ()
            )
            node_id = hal.get("device_node_id_int")
            device_node_id = (
                int(node_id)
                if isinstance(node_id, int) and not isinstance(node_id, bool)
                else None
            )
            driver_plugin = hal.get("driver_plugin_str")
            if not isinstance(driver_plugin, str) or not driver_plugin.strip():
                driver_plugin = None

            records.append(
                JointExport(
                    name=name,
                    joint_type=joint_type,
                    actuator_id=str(actuator_id) if actuator_id is not None else None,
                    lower=lower,
                    upper=upper,
                    velocity=velocity,
                    effort=effort,
                    position_unit=position_unit,
                    velocity_unit=velocity_unit,
                    effort_unit=effort_unit,
                    kp=gains["kp"],
                    ki=gains["ki"],
                    kd=gains["kd"],
                    driver_plugin=driver_plugin,
                    interfaces=interfaces,
                    device_node_id=device_node_id,
                )
            )

        return records

    @staticmethod
    def _topology_by_joint(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
        profiles = topology.get("control_profiles_map", {})
        mappings = topology.get("joint_actuator_mapping_map", {})
        if not isinstance(profiles, dict) or not isinstance(mappings, dict):
            return {}

        resolved: dict[str, dict[str, Any]] = {}
        for actuator_id, entry in mappings.items():
            if not isinstance(entry, dict):
                continue
            joint_name = entry.get("target_joint_ref_str")
            if not isinstance(joint_name, str) or not joint_name:
                continue
            if joint_name in resolved:
                raise SynapseGenerationError(
                    f"multiple actuator mappings target joint {joint_name!r}"
                )

            profile_ref = entry.get("use_profile_ref_str")
            profile = profiles.get(profile_ref, {}) if profile_ref else {}
            merged = deepcopy(profile) if isinstance(profile, dict) else {}
            _deep_merge(
                merged,
                {key: value for key, value in entry.items() if key != "overrides"},
            )
            overrides = entry.get("overrides", {})
            if isinstance(overrides, dict):
                _deep_merge(merged, overrides)
            merged["_actuator_id"] = actuator_id
            resolved[joint_name] = merged
        return resolved

    @staticmethod
    def _dynamics_by_joint(dynamics: dict[str, Any]) -> dict[str, dict[str, Any]]:
        joint_map = dynamics.get("joint_dynamics_map")
        if isinstance(joint_map, dict):
            source = joint_map
        else:
            source = {
                key: value
                for key, value in dynamics.items()
                if isinstance(value, dict) and "limits" in value
            }

        resolved: dict[str, dict[str, Any]] = {}
        for actuator_id, entry in source.items():
            if not isinstance(entry, dict):
                continue
            joint_name = entry.get("target_joint_ref_str") or actuator_id
            if not isinstance(joint_name, str) or not joint_name:
                continue
            copy = deepcopy(entry)
            copy["_actuator_id"] = actuator_id
            resolved[joint_name] = copy
        return resolved

    @staticmethod
    def _hal_by_actuator(hal_mapping: dict[str, Any]) -> dict[str, dict[str, Any]]:
        drivers = hal_mapping.get("actuator_drivers_map", {})
        if not isinstance(drivers, dict):
            return {}

        indexed: dict[str, dict[str, Any]] = {}
        for key, entry in drivers.items():
            if not isinstance(entry, dict):
                continue
            indexed[str(key)] = entry
            logical = entry.get("logical_actuator_ref_str")
            if isinstance(logical, str) and logical:
                indexed.setdefault(logical, entry)
        return indexed

    @staticmethod
    def _position_gains(topology: dict[str, Any]) -> dict[str, float | None]:
        defaults = topology.get("control_defaults", {})
        if not isinstance(defaults, dict):
            defaults = {}
        gains = defaults.get("position_mode_gains", {})
        if not isinstance(gains, dict):
            gains = {}
        return {
            "kp": _first_number(gains.get("kp"), gains.get("kp_position_float")),
            "ki": _first_number(gains.get("ki"), gains.get("ki_position_float")),
            "kd": _first_number(gains.get("kd"), gains.get("kd_position_float")),
        }

    @staticmethod
    def _render_ros2_control(
        joints: list[JointExport],
        *,
        bundle_root: str,
        status: str,
    ) -> str:
        lines = [
            "# OpenRGD deterministic static ROS 2 export",
            f"# bundle_integrity_hash: {bundle_root}",
            f"# status: {status}",
            "# This file does not connect to or actuate hardware.",
            "controller_manager:",
            "  ros__parameters:",
            "    joint_state_broadcaster:",
            "      type: joint_state_broadcaster/JointStateBroadcaster",
            "    forward_position_controller:",
            "      type: position_controllers/JointGroupPositionController",
            "",
            "forward_position_controller:",
            "  ros__parameters:",
            "    joints:",
        ]
        for joint in joints:
            lines.append(
                f"      - {json.dumps(joint.name, ensure_ascii=False)}"
            )

        with_gains = [
            joint
            for joint in joints
            if any(value is not None for value in (joint.kp, joint.ki, joint.kd))
        ]
        if with_gains:
            lines.extend(["    gains:"])
            for joint in with_gains:
                components: list[str] = []
                if joint.kp is not None:
                    components.append(f"p: {_format_number(joint.kp)}")
                if joint.ki is not None:
                    components.append(f"i: {_format_number(joint.ki)}")
                if joint.kd is not None:
                    components.append(f"d: {_format_number(joint.kd)}")
                lines.append(
                    f"      {json.dumps(joint.name, ensure_ascii=False)}: "
                    + "{"
                    + ", ".join(components)
                    + "}"
                )
        return "\n".join(lines) + "\n"

    @staticmethod
    def _render_limits_xacro(
        joints: list[JointExport],
        *,
        bundle_root: str,
    ) -> str:
        lines = [
            '<?xml version="1.0"?>',
            f"<!-- OpenRGD source root: {escape(bundle_root)} -->",
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">',
        ]
        for joint in joints:
            prefix = escape(joint.name, quote=True)
            lines.append(f"  <!-- {prefix} ({escape(joint.joint_type)}) -->")
            for suffix, value in (
                ("effort", joint.effort),
                ("velocity", joint.velocity),
                ("lower", joint.lower),
                ("upper", joint.upper),
            ):
                if value is not None:
                    lines.append(
                        f'  <xacro:property name="{prefix}_{suffix}" '
                        f'value="{_format_number(value)}" />'
                    )
        lines.append("</robot>")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _render_hardware_xacro(
        joints: list[JointExport],
        *,
        driver_plugin: str,
        bundle_root: str,
    ) -> str:
        lines = [
            '<?xml version="1.0"?>',
            f"<!-- OpenRGD source root: {escape(bundle_root)} -->",
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">',
            '  <ros2_control name="OpenRGDStaticExport" type="system">',
            "    <hardware>",
            f"      <plugin>{escape(driver_plugin)}</plugin>",
            "    </hardware>",
        ]
        for joint in joints:
            lines.append(f'    <joint name="{escape(joint.name, quote=True)}">')
            if joint.device_node_id is not None:
                lines.append(
                    f'      <param name="device_node_id">'
                    f"{joint.device_node_id}</param>"
                )
            for interface in joint.interfaces:
                safe_interface = escape(interface, quote=True)
                lines.append(
                    f'      <state_interface name="{safe_interface}"/>'
                )
                lines.append(
                    f'      <command_interface name="{safe_interface}"/>'
                )
            lines.append("    </joint>")
        lines.extend(["  </ros2_control>", "</robot>"])
        return "\n".join(lines) + "\n"
