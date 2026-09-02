"""Non-actuating OpenRGD profile inspection and grounding utilities."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .canonical import CanonicalIntegrityError, IntegrityResult, compute_integrity
from .utils import find_default_kernel, strip_jsonc


class ProfileInspectionError(ValueError):
    """Raised when a profile cannot be safely inspected or grounded."""


@dataclass(frozen=True)
class LoadedModule:
    """One kernel-selected, parsed JSONC module."""

    ref: str
    path: Path
    content: dict[str, Any]
    sha256: str
    size_bytes: int

    def summary(self) -> dict[str, Any]:
        return {
            "path": self.ref,
            "sha256": f"sha256:{self.sha256}",
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class ProfileSnapshot:
    """Integrity-verified profile state selected by one kernel."""

    spec_dir: Path
    kernel_path: Path
    robot_id: str
    kernel: dict[str, Any]
    integrity: IntegrityResult
    modules: tuple[LoadedModule, ...]

    def module_by_stem(self, stem: str) -> LoadedModule | None:
        matches = [
            module for module in self.modules if PurePosixPath(module.ref).stem == stem
        ]
        if len(matches) > 1:
            refs = ", ".join(module.ref for module in matches)
            raise ProfileInspectionError(
                f"module stem {stem!r} is ambiguous across: {refs}"
            )
        return matches[0] if matches else None

    def validation_payload(self) -> dict[str, Any]:
        return {
            "artifact_type": "OPENRGD_PROFILE_VALIDATION",
            "integrity": self.integrity.as_dict(),
            "kernel_ref": "00_core/kernel.jsonc",
            "modules": [module.summary() for module in self.modules],
            "modules_count": len(self.modules),
            "physical_execution_assessed": False,
            "robot_id": self.robot_id,
            "runtime_readiness": "NOT_ASSESSED",
            "status": "VALID",
        }


def _parse_jsonc_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProfileInspectionError(f"cannot read {label}: {path}: {exc}") from exc

    try:
        value = json.loads(strip_jsonc(text), strict=False)
    except json.JSONDecodeError as exc:
        raise ProfileInspectionError(
            f"invalid JSONC in {label} {path}: line {exc.lineno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise ProfileInspectionError(f"{label} must contain a JSON object: {path}")
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ProfileInspectionError(
            f"{label} contains non-canonical JSON values: {path}: {exc}"
        ) from exc
    return value


def resolve_kernel_path(kernel_path: Path | None = None) -> Path:
    """Resolve a canonical kernel path from an argument or current directory."""

    candidate = find_default_kernel() if kernel_path is None else kernel_path
    if candidate is None:
        raise ProfileInspectionError(
            "kernel not found; expected spec/00_core/kernel.jsonc"
        )
    resolved = Path(candidate).resolve()
    if not resolved.is_file():
        raise ProfileInspectionError(f"kernel is not a file: {resolved}")
    if resolved.name != "kernel.jsonc" or resolved.parent.name != "00_core":
        raise ProfileInspectionError(
            "kernel must use the canonical path spec/00_core/kernel.jsonc"
        )
    return resolved


def _spec_dir_for_kernel(kernel_path: Path) -> Path:
    spec_dir = kernel_path.parent.parent.resolve()
    if spec_dir.name != "spec":
        raise ProfileInspectionError(
            f"kernel is not located under a canonical spec directory: {kernel_path}"
        )
    if kernel_path != spec_dir / "00_core" / "kernel.jsonc":
        raise ProfileInspectionError(
            f"kernel path does not resolve canonically inside {spec_dir}"
        )
    return spec_dir


def _normalize_module_ref(raw: Any) -> str:
    if not isinstance(raw, str):
        raise ProfileInspectionError("kernel module references must be strings")
    normalized = raw.replace("\\", "/").strip()
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.parts[0] == "spec"
    ):
        raise ProfileInspectionError(f"unsafe kernel module reference: {raw!r}")
    if path.suffix != ".jsonc":
        raise ProfileInspectionError(
            f"kernel module reference must point to JSONC source: {raw!r}"
        )
    return path.as_posix()


def inspect_profile(kernel_path: Path | None = None) -> ProfileSnapshot:
    """Verify source integrity and load every kernel-selected module."""

    resolved_kernel = resolve_kernel_path(kernel_path)
    spec_dir = _spec_dir_for_kernel(resolved_kernel)

    try:
        integrity = compute_integrity(spec_dir)
    except (CanonicalIntegrityError, OSError, ValueError) as exc:
        raise ProfileInspectionError(f"cannot compute profile integrity: {exc}") from exc
    if not integrity.matches:
        raise ProfileInspectionError(
            "canonical source-tree integrity mismatch: "
            f"declared={integrity.declared!r} computed={integrity.computed!r} "
            f"profile={integrity.profile!r}"
        )

    kernel = _parse_jsonc_object(resolved_kernel, label="kernel")
    meta = kernel.get("meta_group")
    if not isinstance(meta, dict):
        raise ProfileInspectionError("kernel meta_group must be an object")
    robot_id = meta.get("id")
    if not isinstance(robot_id, str) or not robot_id.strip():
        raise ProfileInspectionError("kernel meta_group.id must be a non-empty string")

    raw_modules = kernel.get("module_loading_order_list")
    if not isinstance(raw_modules, list) or not raw_modules:
        raise ProfileInspectionError(
            "kernel module_loading_order_list must be a non-empty list"
        )

    refs: list[str] = []
    seen: set[str] = set()
    for raw_ref in raw_modules:
        ref = _normalize_module_ref(raw_ref)
        if ref in seen:
            raise ProfileInspectionError(f"duplicate kernel module reference: {ref}")
        seen.add(ref)
        refs.append(ref)

    modules: list[LoadedModule] = []
    for ref in refs:
        relative = PurePosixPath(ref)
        path = (spec_dir / Path(*relative.parts)).resolve()
        if spec_dir not in path.parents:
            raise ProfileInspectionError(
                f"module escapes canonical spec directory: {ref}"
            )
        if not path.is_file():
            raise ProfileInspectionError(f"kernel-selected module is missing: {ref}")

        content = _parse_jsonc_object(path, label=f"module {ref}")
        payload = path.read_bytes()
        modules.append(
            LoadedModule(
                ref=ref,
                path=path,
                content=content,
                sha256=hashlib.sha256(payload).hexdigest(),
                size_bytes=len(payload),
            )
        )

    return ProfileSnapshot(
        spec_dir=spec_dir,
        kernel_path=resolved_kernel,
        robot_id=robot_id,
        kernel=kernel,
        integrity=integrity,
        modules=tuple(modules),
    )


def _joint_summary(snapshot: ProfileSnapshot) -> list[dict[str, Any]]:
    description_module = snapshot.module_by_stem("description")
    dynamics_module = snapshot.module_by_stem("actuation_dynamics")

    description = description_module.content if description_module else {}
    dynamics = dynamics_module.content if dynamics_module else {}
    topology = description.get("joint_topology_map", {})
    if not isinstance(topology, dict):
        topology = {}
    raw_joint_dynamics = dynamics.get("joint_dynamics_map", {})
    if not isinstance(raw_joint_dynamics, dict):
        raw_joint_dynamics = {}
    joint_dynamics: dict[str, dict[str, Any]] = {}
    for key, value in raw_joint_dynamics.items():
        if not isinstance(value, dict):
            continue
        target = value.get("target_joint_ref_str")
        name = target if isinstance(target, str) and target else str(key)
        if name in joint_dynamics:
            raise ProfileInspectionError(
                f"multiple dynamics records target joint {name!r}"
            )
        joint_dynamics[name] = value

    names = sorted(set(topology) | set(joint_dynamics))
    records: list[dict[str, Any]] = []
    for name in names:
        top = topology.get(name, {})
        dyn = joint_dynamics.get(name, {})
        if not isinstance(top, dict):
            top = {}
        if not isinstance(dyn, dict):
            dyn = {}
        record: dict[str, Any] = {
            "joint_id": name,
            "type": top.get("type_enum") or dyn.get("joint_type_enum"),
        }
        ideal_limits = top.get("limits_ideal")
        dynamic_limits = dyn.get("joint_limits")
        if isinstance(ideal_limits, dict) and ideal_limits:
            record["ideal_limits"] = ideal_limits
        if isinstance(dynamic_limits, dict) and dynamic_limits:
            record["dynamic_limits"] = dynamic_limits
        records.append(record)
    return records


def _alignment_summary(snapshot: ProfileSnapshot) -> dict[str, Any] | None:
    module = snapshot.module_by_stem("alignment")
    if module is None:
        return None
    alignment = module.content
    meta = alignment.get("meta_group", {})
    if not isinstance(meta, dict):
        meta = {}
    raw_invariants = alignment.get("hard_invariants_list", [])
    if not isinstance(raw_invariants, list):
        raw_invariants = []

    invariants: list[dict[str, Any]] = []
    for item in raw_invariants:
        if not isinstance(item, dict):
            continue
        invariants.append(
            {
                "description": item.get("description_str"),
                "id": item.get("invariant_id_str"),
                "scope": item.get("scope_str"),
                "violation_response": item.get("violation_response_enum"),
            }
        )
    return {
        "hard_invariants": invariants,
        "hard_invariants_count": len(invariants),
        "moral_philosophy": meta.get("moral_philosophy_enum"),
        "profile_id": meta.get("alignment_profile_id_str"),
    }


def build_grounding_context(snapshot: ProfileSnapshot) -> dict[str, Any]:
    """Build a deterministic, non-actuating grounding artifact."""

    joints = _joint_summary(snapshot)
    alignment = _alignment_summary(snapshot)
    return {
        "artifact_type": "OPENRGD_NON_ACTUATING_GROUNDING_CONTEXT",
        "integrity": snapshot.integrity.as_dict(),
        "module_loading_order": [module.ref for module in snapshot.modules],
        "modules": {module.ref: module.content for module in snapshot.modules},
        "physical_execution": {
            "assessed": False,
            "authorized": False,
            "status": "NOT_AUTHORIZED_BY_BOOT",
        },
        "robot_id": snapshot.robot_id,
        "summary": {
            "alignment": alignment,
            "described_joints": joints,
            "described_joints_count": len(joints),
            "modules_count": len(snapshot.modules),
        },
    }


def render_grounding_text(context: dict[str, Any]) -> str:
    """Render a stable human summary without claiming runtime readiness."""

    integrity = context["integrity"]
    summary = context["summary"]
    alignment = summary.get("alignment")
    lines = [
        "OPENRGD NON-ACTUATING GROUNDING CONTEXT",
        "=" * 43,
        f"Identity: {context['robot_id']}",
        f"Source root: {integrity['computed']}",
        f"Modules loaded: {summary['modules_count']}",
        f"Described joints: {summary['described_joints_count']}",
    ]
    if isinstance(alignment, dict):
        lines.append(
            f"Alignment profile: {alignment.get('profile_id') or 'UNDECLARED'}"
        )
        lines.append(
            f"Hard invariants declared: {alignment.get('hard_invariants_count', 0)}"
        )
    lines.extend(
        [
            "Physical execution assessed: NO",
            "Physical execution authorized: NO",
            "Status: GROUNDING_ONLY",
        ]
    )
    return "\n".join(lines) + "\n"
