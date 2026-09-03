from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict

from ..base import BaseImporter


_SUPPORTED_JOINT_TYPES = {
    "revolute",
    "continuous",
    "prismatic",
    "fixed",
    "floating",
    "planar",
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == name]


def _child(element: ET.Element, name: str) -> ET.Element | None:
    children = _children(element, name)
    return children[0] if children else None


def _finite_float(raw: str, *, field: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid numeric value for {field}: {raw!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite numeric value for {field}: {raw!r}")
    return value


def _optional_float(
    element: ET.Element | None,
    attribute: str,
    *,
    field: str,
) -> float | None:
    if element is None:
        return None
    raw = element.get(attribute)
    if raw is None:
        return None
    return _finite_float(raw, field=field)


def _optional_vector(
    element: ET.Element | None,
    attribute: str,
    *,
    field: str,
    length: int = 3,
) -> list[float] | None:
    if element is None:
        return None
    raw = element.get(attribute)
    if raw is None:
        return None
    parts = raw.split()
    if len(parts) != length:
        raise ValueError(
            f"{field} must contain {length} numeric values, got {len(parts)}"
        )
    return [
        _finite_float(part, field=f"{field}[{index}]")
        for index, part in enumerate(parts)
    ]


def _profile_id(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9_.]+", "_", value.lower()).strip("._")
    return normalized or "robot"


class URDFImporter(BaseImporter):
    """Import source-supported URDF facts into a partial OpenRGD profile.

    The importer does not synthesize identity policy, alignment, safety or
    cognitive modules. ``rgd alive`` is the explicit later operation that may
    combine this physical evidence with a reviewed seed profile.
    """

    def parse(self) -> Dict[str, Any]:
        self.log(f"Parsing URDF XML structure from {self.source}...")

        try:
            tree = ET.parse(self.source)
        except (ET.ParseError, OSError) as exc:
            raise ValueError(f"cannot parse URDF source: {exc}") from exc

        root = tree.getroot()
        if _local_name(root.tag) != "robot":
            raise ValueError("URDF root element must be <robot>")

        declared_name = root.get("name")
        if declared_name:
            self.set_robot_name(declared_name)

        source_artifact = self.source_artifact("URDF")
        links: list[dict[str, Any]] = []
        link_names: set[str] = set()

        for link in _children(root, "link"):
            record = self._parse_link(link)
            link_id = record["link_id_str"]
            if link_id in link_names:
                raise ValueError(f"duplicate URDF link name: {link_id!r}")
            link_names.add(link_id)
            links.append(record)

        joint_topology: dict[str, dict[str, Any]] = {}
        joint_dynamics: dict[str, dict[str, Any]] = {}

        for joint in _children(root, "joint"):
            name, topology, dynamics = self._parse_joint(joint)
            if name in joint_topology:
                raise ValueError(f"duplicate URDF joint name: {name!r}")
            joint_topology[name] = topology
            if dynamics is not None:
                joint_dynamics[name] = dynamics

        self.log(
            f"Extracted {len(links)} links and {len(joint_topology)} joints "
            "as partial Foundation evidence."
        )

        model_id = _profile_id(self.robot_name)
        description = {
            "meta_group": {
                "domain_id_str": "01_foundation",
                "evidence_status_enum": "SOURCE_DERIVED_PARTIAL",
                "file_role_enum": "IMPORTED_PARTIAL_DESCRIPTION",
                "model_id_str": model_id,
                "source_artifact_map": source_artifact,
                "version_semver_str": "0.1.0",
            },
            "joint_topology_map": joint_topology,
            "kinematic_chain_list": links,
        }
        dynamics = {
            "actuator_model_dynamics_map": {},
            "joint_dynamics_map": joint_dynamics,
            "meta_group": {
                "domain_id_str": "01_foundation",
                "dynamics_profile_id_str": f"{model_id}_urdf_import",
                "evidence_status_enum": "SOURCE_DERIVED_PARTIAL",
                "file_role_enum": "IMPORTED_PARTIAL_ACTUATION_DYNAMICS",
                "source_artifact_map": source_artifact,
                "version_semver_str": "0.1.0",
            },
        }

        return {
            "spec/01_foundation/description.jsonc": self._render(
                "IMPORTED FROM URDF; PARTIAL FOUNDATION EVIDENCE",
                description,
            ),
            "spec/01_foundation/actuation_dynamics.jsonc": self._render(
                "IMPORTED FROM URDF LIMITS/DYNAMICS; PARTIAL FOUNDATION EVIDENCE",
                dynamics,
            ),
        }

    def _parse_link(self, link: ET.Element) -> dict[str, Any]:
        name = link.get("name")
        if not name:
            raise ValueError("URDF <link> is missing required name")

        record: dict[str, Any] = {"link_id_str": name}
        inertial = _child(link, "inertial")
        if inertial is None:
            return record

        properties: dict[str, Any] = {}
        mass = _child(inertial, "mass")
        mass_value = _optional_float(
            mass,
            "value",
            field=f"link {name} inertial mass",
        )
        if mass_value is not None:
            properties["mass_kg_float"] = mass_value

        origin = _child(inertial, "origin")
        xyz = _optional_vector(
            origin,
            "xyz",
            field=f"link {name} inertial origin xyz",
        )
        rpy = _optional_vector(
            origin,
            "rpy",
            field=f"link {name} inertial origin rpy",
        )
        if xyz is not None:
            properties["center_of_mass_xyz_m_vec3_float"] = xyz
        if rpy is not None:
            properties["inertial_origin_rpy_rad_vec3_float"] = rpy

        inertia = _child(inertial, "inertia")
        if inertia is not None:
            names = ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")
            values: list[float] = []
            present = True
            for component in names:
                value = _optional_float(
                    inertia,
                    component,
                    field=f"link {name} inertia {component}",
                )
                if value is None:
                    present = False
                    break
                values.append(value)
            if present:
                properties[
                    "inertia_tensor_xx_yy_zz_xy_xz_yz_kgm2_vec6_float"
                ] = values

        if properties:
            record["inertial_properties"] = properties
        return record

    def _parse_joint(
        self,
        joint: ET.Element,
    ) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
        name = joint.get("name")
        if not name:
            raise ValueError("URDF <joint> is missing required name")

        joint_type = joint.get("type", "").lower()
        if joint_type not in _SUPPORTED_JOINT_TYPES:
            raise ValueError(
                f"joint {name!r} has unsupported type {joint_type!r}"
            )

        parent = _child(joint, "parent")
        child = _child(joint, "child")
        parent_link = parent.get("link") if parent is not None else None
        child_link = child.get("link") if child is not None else None
        if not parent_link or not child_link:
            raise ValueError(
                f"joint {name!r} must declare parent and child links"
            )

        topology: dict[str, Any] = {
            "connectivity": {
                "child_link_ref_str": child_link,
                "parent_link_ref_str": parent_link,
            },
            "type_enum": joint_type.upper(),
        }

        geometry: dict[str, Any] = {}
        origin = _child(joint, "origin")
        xyz = _optional_vector(
            origin,
            "xyz",
            field=f"joint {name} origin xyz",
        )
        rpy = _optional_vector(
            origin,
            "rpy",
            field=f"joint {name} origin rpy",
        )
        axis = _optional_vector(
            _child(joint, "axis"),
            "xyz",
            field=f"joint {name} axis xyz",
        )
        if xyz is not None:
            geometry["origin_xyz_m_vec3_float"] = xyz
        if rpy is not None:
            geometry["origin_rpy_rad_vec3_float"] = rpy
        if axis is not None:
            geometry["axis_xyz_vec3_float"] = axis
        if geometry:
            topology["geometry_ideal"] = geometry

        limit = _child(joint, "limit")
        effort = _optional_float(
            limit,
            "effort",
            field=f"joint {name} limit effort",
        )
        velocity = _optional_float(
            limit,
            "velocity",
            field=f"joint {name} limit velocity",
        )
        lower = _optional_float(
            limit,
            "lower",
            field=f"joint {name} limit lower",
        )
        upper = _optional_float(
            limit,
            "upper",
            field=f"joint {name} limit upper",
        )

        topology_limits = self._topology_limits(
            joint_type=joint_type,
            effort=effort,
            velocity=velocity,
            lower=lower,
            upper=upper,
        )
        if topology_limits:
            topology["limits_ideal"] = topology_limits

        mimic = _child(joint, "mimic")
        if mimic is not None:
            target = mimic.get("joint")
            if not target:
                raise ValueError(
                    f"joint {name!r} mimic element is missing target joint"
                )
            mimic_map: dict[str, Any] = {"joint_ref_str": target}
            multiplier = _optional_float(
                mimic,
                "multiplier",
                field=f"joint {name} mimic multiplier",
            )
            offset = _optional_float(
                mimic,
                "offset",
                field=f"joint {name} mimic offset",
            )
            if multiplier is not None:
                mimic_map["multiplier_float"] = multiplier
            if offset is not None:
                mimic_map["offset_float"] = offset
            topology["mimic_map"] = mimic_map

        if joint_type == "fixed":
            return name, topology, None

        dynamics_record: dict[str, Any] = {
            "joint_type_enum": joint_type.upper(),
            "target_joint_ref_str": name,
        }
        dynamic_limits = self._dynamic_limits(
            joint_type=joint_type,
            effort=effort,
            velocity=velocity,
            lower=lower,
            upper=upper,
        )
        if dynamic_limits:
            dynamics_record["joint_limits"] = dynamic_limits

        source_dynamics = _child(joint, "dynamics")
        damping = _optional_float(
            source_dynamics,
            "damping",
            field=f"joint {name} dynamics damping",
        )
        friction = _optional_float(
            source_dynamics,
            "friction",
            field=f"joint {name} dynamics friction",
        )
        if damping is not None or friction is not None:
            dynamics_map: dict[str, Any] = {}
            if damping is not None:
                dynamics_map["damping_coefficient_float"] = damping
            if friction is not None:
                dynamics_map["friction_coefficient_float"] = friction
            dynamics_record["source_dynamics_map"] = dynamics_map

        return name, topology, dynamics_record

    @staticmethod
    def _topology_limits(
        *,
        joint_type: str,
        effort: float | None,
        velocity: float | None,
        lower: float | None,
        upper: float | None,
    ) -> dict[str, float]:
        limits: dict[str, float] = {}
        if joint_type in {"revolute", "continuous"}:
            if lower is not None and joint_type != "continuous":
                limits["position_lower_rad_float"] = lower
            if upper is not None and joint_type != "continuous":
                limits["position_upper_rad_float"] = upper
            if velocity is not None:
                limits["velocity_max_rad_s_float"] = velocity
            if effort is not None:
                limits["effort_max_nm_float"] = effort
        elif joint_type == "prismatic":
            if lower is not None:
                limits["position_lower_m_float"] = lower
            if upper is not None:
                limits["position_upper_m_float"] = upper
            if velocity is not None:
                limits["velocity_max_m_s_float"] = velocity
            if effort is not None:
                limits["effort_max_n_float"] = effort
        return limits

    @staticmethod
    def _dynamic_limits(
        *,
        joint_type: str,
        effort: float | None,
        velocity: float | None,
        lower: float | None,
        upper: float | None,
    ) -> dict[str, float]:
        limits: dict[str, float] = {}
        if joint_type in {"revolute", "continuous"}:
            if lower is not None and joint_type != "continuous":
                limits["soft_min_position_rad_float"] = lower
            if upper is not None and joint_type != "continuous":
                limits["soft_max_position_rad_float"] = upper
            if velocity is not None:
                limits["max_velocity_rad_s_float"] = velocity
            if effort is not None:
                limits["max_effort_nm_float"] = effort
        elif joint_type == "prismatic":
            if lower is not None:
                limits["soft_min_position_m_float"] = lower
            if upper is not None:
                limits["soft_max_position_m_float"] = upper
            if velocity is not None:
                limits["max_velocity_m_s_float"] = velocity
            if effort is not None:
                limits["max_effort_n_float"] = effort
        return limits

    @staticmethod
    def _render(header: str, payload: dict[str, Any]) -> str:
        return (
            f"/** {header} */\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                indent=2,
            )
            + "\n"
        )
