from __future__ import annotations

import json
import math
import re
from typing import Any, Dict

from ..base import BaseImporter


_JOINT_PATTERN = re.compile(
    r'\bdef\s+Physics(?P<kind>Revolute|Prismatic)Joint\s+"(?P<name>[^"]+)"'
)
_AXIS_VECTORS = {
    "X": [1.0, 0.0, 0.0],
    "Y": [0.0, 1.0, 0.0],
    "Z": [0.0, 0.0, 1.0],
}


def _finite_float(raw: str, *, field: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid numeric value for {field}: {raw!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite numeric value for {field}: {raw!r}")
    return value


def _strip_comments(text: str) -> str:
    """Replace USDA comments with whitespace while preserving strings/newlines."""

    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    line_comment = False
    block_comment = False

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
                output.append(char)
            else:
                output.append(" ")
            index += 1
            continue

        if block_comment:
            if char == "*" and next_char == "/":
                output.extend((" ", " "))
                block_comment = False
                index += 2
                continue
            output.append("\n" if char == "\n" else " ")
            index += 1
            continue

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "#":
            line_comment = True
            output.append(" ")
            index += 1
            continue

        if char == "/" and next_char == "/":
            line_comment = True
            output.extend((" ", " "))
            index += 2
            continue

        if char == "/" and next_char == "*":
            block_comment = True
            output.extend((" ", " "))
            index += 2
            continue

        output.append(char)
        index += 1

    if block_comment:
        raise ValueError("unterminated block comment in USDA source")
    if in_string:
        raise ValueError("unterminated string in USDA source")
    return "".join(output)


def _balanced_block(text: str, start: int, *, label: str) -> str:
    open_index = text.find("{", start)
    if open_index < 0:
        raise ValueError(f"{label} has no opening block")

    depth = 0
    in_string = False
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index]
    raise ValueError(f"{label} has an unterminated block")


def _single_match(
    text: str,
    pattern: str,
    *,
    field: str,
    flags: int = re.MULTILINE,
) -> str | None:
    matches = re.findall(pattern, text, flags=flags)
    if len(matches) > 1:
        raise ValueError(f"duplicate USDA attribute for {field}")
    return matches[0] if matches else None


def _optional_scalar(text: str, attribute: str, *, field: str) -> float | None:
    raw = _single_match(
        text,
        rf"^\s*(?:uniform\s+)?(?:float|double)\s+{re.escape(attribute)}\s*=\s*([^\s,\)\]\}}]+)",
        field=field,
    )
    return None if raw is None else _finite_float(raw, field=field)


def _optional_stage_scalar(text: str, name: str) -> float | None:
    raw = _single_match(
        text,
        rf"\b{re.escape(name)}\s*=\s*([^\s,\)\]\}}]+)",
        field=name,
    )
    return None if raw is None else _finite_float(raw, field=name)


def _optional_token(text: str, attribute: str, *, field: str) -> str | None:
    return _single_match(
        text,
        rf'^\s*(?:uniform\s+)?token\s+{re.escape(attribute)}\s*=\s*"([^"]+)"',
        field=field,
    )


def _optional_relationship(text: str, attribute: str, *, field: str) -> str | None:
    return _single_match(
        text,
        rf"^\s*(?:(?:prepend|append)\s+)?rel\s+{re.escape(attribute)}\s*=\s*<([^>]+)>",
        field=field,
    )


def _optional_vector(
    text: str,
    attribute: str,
    *,
    field: str,
    length: int,
) -> list[float] | None:
    raw = _single_match(
        text,
        rf"^\s*(?:uniform\s+)?(?:float|double|half|vector)3[fdh]?\s+{re.escape(attribute)}\s*=\s*\(([^)]*)\)",
        field=field,
    )
    if raw is None:
        return None
    parts = [item for item in re.split(r"[\s,]+", raw.strip()) if item]
    if len(parts) != length:
        raise ValueError(
            f"{field} must contain {length} numeric values, got {len(parts)}"
        )
    return [
        _finite_float(item, field=f"{field}[{index}]")
        for index, item in enumerate(parts)
    ]


def _optional_quaternion(
    text: str,
    attribute: str,
    *,
    field: str,
) -> list[float] | None:
    raw = _single_match(
        text,
        rf"^\s*(?:uniform\s+)?quat[fdh]\s+{re.escape(attribute)}\s*=\s*\(([^)]*)\)",
        field=field,
    )
    if raw is None:
        return None
    parts = [item for item in re.split(r"[\s,]+", raw.strip()) if item]
    if len(parts) != 4:
        raise ValueError(f"{field} must contain 4 numeric values, got {len(parts)}")
    return [
        _finite_float(item, field=f"{field}[{index}]")
        for index, item in enumerate(parts)
    ]


def _body_id(path: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "__", path.strip("/")).strip("_")
    return normalized or "usd_body"


class USDImporter(BaseImporter):
    """Import source-supported facts from text USDA into partial OpenRGD evidence.

    This lightweight parser intentionally supports a narrow, reviewable subset.
    It does not compose layers, resolve references, evaluate variants, or replace
    the OpenUSD SDK. Binary USD is rejected.
    """

    def parse(self) -> Dict[str, Any]:
        self.log(f"Parsing text USDA evidence from {self.source}...")

        try:
            raw = self.source.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "binary/non-UTF-8 USD is unsupported; convert the stage to USDA text"
            ) from exc
        except OSError as exc:
            raise ValueError(f"cannot read USD source: {exc}") from exc

        if not raw.lstrip().startswith("#usda"):
            raise ValueError(
                "only text USDA stages are supported by the lightweight importer"
            )

        content = _strip_comments(raw)
        default_prim = _single_match(
            content,
            r'\bdefaultPrim\s*=\s*"([^"]+)"',
            field="defaultPrim",
        )
        if default_prim:
            self.set_robot_name(default_prim)

        meters_per_unit = _optional_stage_scalar(content, "metersPerUnit")
        kilograms_per_unit = _optional_stage_scalar(content, "kilogramsPerUnit")
        if meters_per_unit is not None and meters_per_unit <= 0:
            raise ValueError("metersPerUnit must be greater than zero")
        if kilograms_per_unit is not None and kilograms_per_unit <= 0:
            raise ValueError("kilogramsPerUnit must be greater than zero")

        up_axis = _single_match(
            content,
            r'\bupAxis\s*=\s*"([^"]+)"',
            field="upAxis",
        )
        if up_axis is not None:
            up_axis = up_axis.upper()
            if up_axis not in _AXIS_VECTORS:
                raise ValueError(f"unsupported upAxis token: {up_axis!r}")

        source_artifact = self.source_artifact("USD_ASCII")
        stage_metadata: dict[str, Any] = {
            "angular_unit_enum": "DEGREE",
            "source_profile_str": "OPENUSD_USDA_LIGHTWEIGHT_V1",
        }
        if default_prim is not None:
            stage_metadata["default_prim_str"] = default_prim
        if meters_per_unit is not None:
            stage_metadata["meters_per_unit_float"] = meters_per_unit
        if kilograms_per_unit is not None:
            stage_metadata["kilograms_per_unit_float"] = kilograms_per_unit
        if up_axis is not None:
            stage_metadata["up_axis_enum"] = up_axis

        joint_topology: dict[str, dict[str, Any]] = {}
        joint_dynamics: dict[str, dict[str, Any]] = {}
        body_records: dict[str, dict[str, Any]] = {}

        for match in _JOINT_PATTERN.finditer(content):
            kind = match.group("kind")
            name = match.group("name")
            if name in joint_topology:
                raise ValueError(f"duplicate USD joint name: {name!r}")
            block = _balanced_block(content, match.end(), label=f"joint {name!r}")
            topology, dynamics, bodies = self._parse_joint(
                name=name,
                kind=kind,
                block=block,
                meters_per_unit=meters_per_unit,
                kilograms_per_unit=kilograms_per_unit,
            )
            joint_topology[name] = topology
            joint_dynamics[name] = dynamics
            for body_path in bodies:
                body_records.setdefault(
                    body_path,
                    {
                        "link_id_str": _body_id(body_path),
                        "source_prim_path_str": body_path,
                    },
                )

        if not joint_topology:
            raise ValueError(
                "no supported PhysicsRevoluteJoint or PhysicsPrismaticJoint found"
            )

        self.log(
            f"Extracted {len(body_records)} referenced bodies and "
            f"{len(joint_topology)} supported joints as partial Foundation evidence."
        )

        model_id = re.sub(
            r"[^a-z0-9_.]+",
            "_",
            self.robot_name.lower(),
        ).strip("._") or "robot"
        description = {
            "joint_topology_map": joint_topology,
            "kinematic_chain_list": [
                body_records[path] for path in sorted(body_records)
            ],
            "meta_group": {
                "domain_id_str": "01_foundation",
                "evidence_status_enum": "SOURCE_DERIVED_PARTIAL",
                "file_role_enum": "IMPORTED_PARTIAL_DESCRIPTION",
                "model_id_str": model_id,
                "source_artifact_map": source_artifact,
                "source_stage_metadata_map": stage_metadata,
                "version_semver_str": "0.1.0",
            },
        }
        dynamics = {
            "actuator_model_dynamics_map": {},
            "joint_dynamics_map": joint_dynamics,
            "meta_group": {
                "domain_id_str": "01_foundation",
                "dynamics_profile_id_str": f"{model_id}_usd_import",
                "evidence_status_enum": "SOURCE_DERIVED_PARTIAL",
                "file_role_enum": "IMPORTED_PARTIAL_ACTUATION_DYNAMICS",
                "source_artifact_map": source_artifact,
                "source_stage_metadata_map": stage_metadata,
                "version_semver_str": "0.1.0",
            },
        }

        return {
            "spec/01_foundation/description.jsonc": self._render(
                "IMPORTED FROM USDA; PARTIAL FOUNDATION EVIDENCE",
                description,
            ),
            "spec/01_foundation/actuation_dynamics.jsonc": self._render(
                "IMPORTED FROM USDA PHYSICS; PARTIAL FOUNDATION EVIDENCE",
                dynamics,
            ),
        }

    def _parse_joint(
        self,
        *,
        name: str,
        kind: str,
        block: str,
        meters_per_unit: float | None,
        kilograms_per_unit: float | None,
    ) -> tuple[dict[str, Any], dict[str, Any], tuple[str, ...]]:
        joint_type = "REVOLUTE" if kind == "Revolute" else "PRISMATIC"
        body0 = _optional_relationship(
            block,
            "physics:body0",
            field=f"joint {name} body0",
        )
        body1 = _optional_relationship(
            block,
            "physics:body1",
            field=f"joint {name} body1",
        )
        axis_token = _optional_token(
            block,
            "physics:axis",
            field=f"joint {name} axis",
        )
        if axis_token is not None:
            axis_token = axis_token.upper()
            if axis_token not in _AXIS_VECTORS:
                raise ValueError(
                    f"joint {name!r} has unsupported axis token {axis_token!r}"
                )

        lower = _optional_scalar(
            block,
            "physics:lowerLimit",
            field=f"joint {name} lowerLimit",
        )
        upper = _optional_scalar(
            block,
            "physics:upperLimit",
            field=f"joint {name} upperLimit",
        )
        if lower is not None and upper is not None and lower > upper:
            raise ValueError(f"joint {name!r} lowerLimit exceeds upperLimit")

        drive_prefix = "drive:angular" if joint_type == "REVOLUTE" else "drive:linear"
        drive_max_force = _optional_scalar(
            block,
            f"{drive_prefix}:physics:maxForce",
            field=f"joint {name} drive maxForce",
        )
        drive_stiffness = _optional_scalar(
            block,
            f"{drive_prefix}:physics:stiffness",
            field=f"joint {name} drive stiffness",
        )
        drive_damping = _optional_scalar(
            block,
            f"{drive_prefix}:physics:damping",
            field=f"joint {name} drive damping",
        )
        if drive_max_force is not None and drive_max_force < 0:
            raise ValueError(f"joint {name!r} drive maxForce cannot be negative")

        source_joint: dict[str, Any] = {
            "joint_schema_enum": f"USD_PHYSICS_{joint_type}_JOINT",
            "source_position_unit_enum": (
                "DEGREE" if joint_type == "REVOLUTE" else "STAGE_DISTANCE_UNIT"
            ),
        }
        if body0 is not None:
            source_joint["body0_prim_path_str"] = body0
        if body1 is not None:
            source_joint["body1_prim_path_str"] = body1
        if axis_token is not None:
            source_joint["axis_token_enum"] = axis_token
        raw_limits: dict[str, float] = {}
        if lower is not None:
            raw_limits["lower_float"] = lower
        if upper is not None:
            raw_limits["upper_float"] = upper
        if raw_limits:
            source_joint["source_limits_map"] = raw_limits

        reference_frames: dict[str, Any] = {}
        for suffix in ("0", "1"):
            local_pos = _optional_vector(
                block,
                f"physics:localPos{suffix}",
                field=f"joint {name} localPos{suffix}",
                length=3,
            )
            local_rot = _optional_quaternion(
                block,
                f"physics:localRot{suffix}",
                field=f"joint {name} localRot{suffix}",
            )
            frame: dict[str, Any] = {}
            if local_pos is not None:
                frame["position_stage_units_vec3_float"] = local_pos
                if meters_per_unit is not None:
                    frame["position_m_vec3_float"] = [
                        value * meters_per_unit for value in local_pos
                    ]
            if local_rot is not None:
                frame["orientation_real_i_j_k_quat4_float"] = local_rot
            if frame:
                reference_frames[f"frame_{suffix}"] = frame
        if reference_frames:
            source_joint["source_reference_frames_map"] = reference_frames

        source_drive: dict[str, Any] = {}
        if drive_max_force is not None:
            source_drive["max_force_source_units_float"] = drive_max_force
        if drive_stiffness is not None:
            source_drive["stiffness_source_units_float"] = drive_stiffness
        if drive_damping is not None:
            source_drive["damping_source_units_float"] = drive_damping
        if source_drive:
            source_drive["drive_namespace_str"] = drive_prefix
            source_joint["source_drive_map"] = source_drive

        topology: dict[str, Any] = {
            "source_usd_joint_map": source_joint,
            "type_enum": joint_type,
        }
        if axis_token is not None:
            topology["geometry_ideal"] = {
                "axis_xyz_vec3_float": _AXIS_VECTORS[axis_token],
            }

        topology_limits: dict[str, float] = {}
        dynamic_limits: dict[str, float] = {}
        if joint_type == "REVOLUTE":
            if lower is not None:
                radians = math.radians(lower)
                topology_limits["position_lower_rad_float"] = radians
                dynamic_limits["soft_min_position_rad_float"] = radians
            if upper is not None:
                radians = math.radians(upper)
                topology_limits["position_upper_rad_float"] = radians
                dynamic_limits["soft_max_position_rad_float"] = radians
            torque = self._converted_effort(
                joint_name=name,
                raw=drive_max_force,
                joint_type=joint_type,
                meters_per_unit=meters_per_unit,
                kilograms_per_unit=kilograms_per_unit,
            )
            if torque is not None:
                topology_limits["effort_max_nm_float"] = torque
                dynamic_limits["max_effort_nm_float"] = torque
        else:
            if (lower is not None or upper is not None) and meters_per_unit is None:
                raise ValueError(
                    f"joint {name!r} has prismatic limits but the stage does not "
                    "author metersPerUnit"
                )
            if lower is not None:
                meters = lower * meters_per_unit  # type: ignore[operator]
                topology_limits["position_lower_m_float"] = meters
                dynamic_limits["soft_min_position_m_float"] = meters
            if upper is not None:
                meters = upper * meters_per_unit  # type: ignore[operator]
                topology_limits["position_upper_m_float"] = meters
                dynamic_limits["soft_max_position_m_float"] = meters
            force = self._converted_effort(
                joint_name=name,
                raw=drive_max_force,
                joint_type=joint_type,
                meters_per_unit=meters_per_unit,
                kilograms_per_unit=kilograms_per_unit,
            )
            if force is not None:
                topology_limits["effort_max_n_float"] = force
                dynamic_limits["max_effort_n_float"] = force

        if topology_limits:
            topology["limits_ideal"] = topology_limits

        dynamics: dict[str, Any] = {
            "joint_type_enum": joint_type,
            "source_usd_joint_map": source_joint,
            "target_joint_ref_str": name,
        }
        if dynamic_limits:
            dynamics["joint_limits"] = dynamic_limits

        bodies = tuple(path for path in (body0, body1) if path is not None)
        return topology, dynamics, bodies

    @staticmethod
    def _converted_effort(
        *,
        joint_name: str,
        raw: float | None,
        joint_type: str,
        meters_per_unit: float | None,
        kilograms_per_unit: float | None,
    ) -> float | None:
        if raw is None:
            return None
        if meters_per_unit is None or kilograms_per_unit is None:
            return None
        if joint_type == "REVOLUTE":
            factor = kilograms_per_unit * meters_per_unit * meters_per_unit
        else:
            factor = kilograms_per_unit * meters_per_unit
        converted = raw * factor
        if not math.isfinite(converted):
            raise ValueError(f"joint {joint_name!r} effort conversion is non-finite")
        return converted

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
