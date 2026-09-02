"""Deterministic source-tree hashing and machine-bundle generation for OpenRGD."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
from typing import Any, Iterable

from .utils import strip_jsonc

INTEGRITY_PROFILE = "OPENRGD_SOURCE_TREE_SHA256_V1"
INTEGRITY_PREFIX = "sha256:"
MANIFEST_RELATIVE_PATH = "manifest.jsonc"
MANIFEST_SELF_VALUE = "sha256:SELF"
DEFAULT_STATIC_FILES = ("MANIFESTO.md",)

_GENERATED_TOP_LEVEL_NAMES = {
    "01_spec.jsonc",
    "02_spec.jsonc",
    "03_spec.jsonc",
    "04_spec.jsonc",
    "05_spec.jsonc",
    "06_spec.jsonc",
    "openrgd_unified_spec.jsonc",
    "openrgd_unified_spec_document.jsonc",
}
_INTEGRITY_FIELD_RE = re.compile(
    r'(?P<prefix>"integrity_hash_str"\s*:\s*")(?P<value>[^"]*)(?P<suffix>")'
)
_PROFILE_FIELD_RE = re.compile(
    r'(?P<prefix>"integrity_profile_str"\s*:\s*")(?P<value>[^"]*)(?P<suffix>")'
)


class CanonicalIntegrityError(ValueError):
    """Raised when a source tree cannot satisfy the canonical integrity profile."""


@dataclass(frozen=True)
class SourceEntry:
    """One path commitment in the OpenRGD canonical source index."""

    path: str
    media_type: str
    size_bytes: int
    sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "media_type": self.media_type,
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class IntegrityResult:
    """Computed and declared integrity state for one specification tree."""

    profile: str | None
    computed: str
    declared: str | None
    matches: bool
    files_count: int
    index: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "computed": self.computed,
            "declared": self.declared,
            "files_count": self.files_count,
            "matches": self.matches,
            "profile": self.profile,
        }


def resolve_spec_dir(root: Path) -> Path:
    """Resolve either a project root or a direct ``spec`` directory."""

    root = root.resolve()
    if root.name == "spec" and root.is_dir():
        return root
    candidate = root / "spec"
    if candidate.is_dir():
        return candidate
    raise CanonicalIntegrityError(f"spec directory not found under: {root}")


def _is_generated_source(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    return len(path.parts) == 1 and path.name in _GENERATED_TOP_LEVEL_NAMES


def discover_source_paths(
    spec_dir: Path,
    *,
    static_files: Iterable[str] = DEFAULT_STATIC_FILES,
) -> list[Path]:
    """Return the canonical source set, excluding generated aggregate names."""

    spec_dir = spec_dir.resolve()
    if not spec_dir.is_dir():
        raise CanonicalIntegrityError(f"spec directory does not exist: {spec_dir}")

    selected: dict[str, Path] = {}
    for path in spec_dir.rglob("*.jsonc"):
        if path.is_symlink():
            raise CanonicalIntegrityError(
                f"canonical source symlinks are not allowed: {path}"
            )
        rel = path.relative_to(spec_dir).as_posix()
        if not _is_generated_source(rel):
            selected[rel] = path

    for raw_rel in static_files:
        rel = PurePosixPath(raw_rel).as_posix()
        path = spec_dir / rel
        if path.is_symlink():
            raise CanonicalIntegrityError(
                f"canonical static-file symlinks are not allowed: {path}"
            )
        if path.is_file():
            selected[rel] = path

    if MANIFEST_RELATIVE_PATH not in selected:
        raise CanonicalIntegrityError(
            f"canonical source tree requires {MANIFEST_RELATIVE_PATH}"
        )
    return [selected[rel] for rel in sorted(selected)]


def _normalize_manifest_source(raw: bytes) -> bytes:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CanonicalIntegrityError("manifest.jsonc must be UTF-8") from exc

    normalized, count = _INTEGRITY_FIELD_RE.subn(
        lambda match: (
            f"{match.group('prefix')}{MANIFEST_SELF_VALUE}{match.group('suffix')}"
        ),
        text,
        count=1,
    )
    if count != 1:
        raise CanonicalIntegrityError(
            "manifest.jsonc must contain exactly one integrity_hash_str field"
        )
    return normalized.encode("utf-8")


def normalized_source_bytes(path: Path, spec_dir: Path) -> bytes:
    """Return exact source bytes, normalizing only the manifest self-hash field."""

    raw = path.read_bytes()
    rel = path.relative_to(spec_dir).as_posix()
    if rel == MANIFEST_RELATIVE_PATH:
        return _normalize_manifest_source(raw)
    return raw


def _media_type(path: Path) -> str:
    if path.suffix == ".jsonc":
        return "application/jsonc"
    if path.suffix == ".md":
        return "text/markdown; charset=utf-8"
    return "application/octet-stream"


def build_source_index(spec_dir: Path) -> tuple[dict[str, Any], list[SourceEntry]]:
    """Build the deterministic path-sorted index used as the root preimage."""

    spec_dir = spec_dir.resolve()
    entries: list[SourceEntry] = []
    for path in discover_source_paths(spec_dir):
        rel = path.relative_to(spec_dir).as_posix()
        payload = normalized_source_bytes(path, spec_dir)
        entries.append(
            SourceEntry(
                path=rel,
                media_type=_media_type(path),
                size_bytes=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
        )

    index = {
        "files": [entry.as_dict() for entry in entries],
        "hash_algorithm": "SHA-256",
        "manifest_self_value": MANIFEST_SELF_VALUE,
        "profile": INTEGRITY_PROFILE,
        "source_root": "spec",
    }
    return index, entries


def canonical_index_bytes(index: dict[str, Any]) -> bytes:
    """Serialize the source index using the versioned canonical JSON profile."""

    return json.dumps(
        index,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _parse_jsonc(path: Path) -> Any:
    return json.loads(strip_jsonc(path.read_text(encoding="utf-8")), strict=False)


def compute_integrity(spec_dir: Path) -> IntegrityResult:
    """Compute the source-tree root and compare it with the bundle manifest."""

    spec_dir = spec_dir.resolve()
    index, entries = build_source_index(spec_dir)
    digest = hashlib.sha256(canonical_index_bytes(index)).hexdigest()
    computed = f"{INTEGRITY_PREFIX}{digest}"

    manifest = _parse_jsonc(spec_dir / MANIFEST_RELATIVE_PATH)
    meta = manifest.get("meta_group", {}) if isinstance(manifest, dict) else {}
    declared = meta.get("integrity_hash_str")
    profile = meta.get("integrity_profile_str")

    return IntegrityResult(
        profile=profile,
        computed=computed,
        declared=declared,
        matches=(profile == INTEGRITY_PROFILE and declared == computed),
        files_count=len(entries),
        index=index,
    )


def _ensure_current_profile(text: str) -> str:
    profile_match = _PROFILE_FIELD_RE.search(text)
    if profile_match:
        current = profile_match.group("value")
        if current != INTEGRITY_PROFILE:
            raise CanonicalIntegrityError(
                "refusing to overwrite a different integrity profile: "
                f"{current!r}"
            )
        return text

    integrity_match = _INTEGRITY_FIELD_RE.search(text)
    if not integrity_match:
        raise CanonicalIntegrityError(
            "manifest.jsonc must contain integrity_hash_str before profile migration"
        )

    line_start = text.rfind("\n", 0, integrity_match.start()) + 1
    indentation = text[line_start : integrity_match.start()]
    profile_line = (
        f'{indentation}"integrity_profile_str": "{INTEGRITY_PROFILE}",\n'
    )
    return text[:line_start] + profile_line + text[line_start:]


def update_manifest_integrity(spec_dir: Path) -> IntegrityResult:
    """Write the current profile and computed root into ``manifest.jsonc``."""

    spec_dir = spec_dir.resolve()
    manifest_path = spec_dir / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        raise CanonicalIntegrityError(
            f"cannot update integrity without {MANIFEST_RELATIVE_PATH}"
        )

    original = manifest_path.read_text(encoding="utf-8")
    text = _ensure_current_profile(original)
    if text != original:
        manifest_path.write_text(text, encoding="utf-8", newline="\n")

    result = compute_integrity(spec_dir)
    text = manifest_path.read_text(encoding="utf-8")
    updated, count = _INTEGRITY_FIELD_RE.subn(
        lambda match: (
            f"{match.group('prefix')}{result.computed}{match.group('suffix')}"
        ),
        text,
        count=1,
    )
    if count != 1:
        raise CanonicalIntegrityError(
            "manifest.jsonc must contain exactly one integrity_hash_str field"
        )
    manifest_path.write_text(updated, encoding="utf-8", newline="\n")

    verified = compute_integrity(spec_dir)
    if not verified.matches:
        raise CanonicalIntegrityError(
            "manifest integrity did not stabilize after update: "
            f"declared={verified.declared!r} computed={verified.computed!r} "
            f"profile={verified.profile!r}"
        )
    return verified


def _domain_for(relative_path: str) -> str:
    first = PurePosixPath(relative_path).parts[0]
    if first == "00_core" or re.fullmatch(r"0[1-6]_[a-z0-9_]+", first):
        return first
    return "root"


def _assert_safe_output(spec_dir: Path, output_path: Path) -> None:
    source_paths = {path.resolve() for path in discover_source_paths(spec_dir)}
    if output_path.resolve() in source_paths:
        raise CanonicalIntegrityError(
            f"generated output would overwrite canonical source: {output_path}"
        )
    if output_path.suffix.lower() != ".json":
        raise CanonicalIntegrityError("machine-bundle output must use .json")


def build_machine_bundle(spec_dir: Path, output_path: Path) -> dict[str, Any]:
    """Generate one deterministic machine bundle without modifying sources."""

    spec_dir = spec_dir.resolve()
    output_path = output_path.resolve()
    _assert_safe_output(spec_dir, output_path)

    integrity = compute_integrity(spec_dir)
    if not integrity.matches:
        raise CanonicalIntegrityError(
            "manifest integrity mismatch; run 'rgd hash --write' before compilation: "
            f"declared={integrity.declared!r} computed={integrity.computed!r} "
            f"profile={integrity.profile!r}"
        )

    manifest = _parse_jsonc(spec_dir / MANIFEST_RELATIVE_PATH)
    standard_version = (
        manifest.get("meta_group", {}).get("rgd_standard_version_semver_str")
        or "UNDECLARED"
    )

    indexed = {item["path"]: item for item in integrity.index["files"]}
    files: list[dict[str, Any]] = []
    for path in discover_source_paths(spec_dir):
        rel = path.relative_to(spec_dir).as_posix()
        record: dict[str, Any] = {
            "domain": _domain_for(rel),
            "id": path.stem,
            "media_type": indexed[rel]["media_type"],
            "path": f"spec/{rel}",
            "source_sha256": indexed[rel]["sha256"],
        }
        if path.suffix == ".jsonc":
            record["content"] = _parse_jsonc(path)
        else:
            record["content_text"] = path.read_text(encoding="utf-8")
        files.append(record)

    document = {
        "files": files,
        "meta": {
            "artifact_type": "OPENRGD_CANONICAL_MACHINE_BUNDLE",
            "bundle_integrity_hash": integrity.computed,
            "files_count": integrity.files_count,
            "integrity_profile": INTEGRITY_PROFILE,
            "standard": "OpenRGD",
            "standard_version": standard_version,
        },
        "source_index": integrity.index,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            document,
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
        "bundle_integrity_hash": integrity.computed,
        "files_count": integrity.files_count,
        "output_path": str(output_path),
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "profile": INTEGRITY_PROFILE,
    }


def _assert_safe_mirror_destination(spec_dir: Path, destination: Path) -> None:
    spec_dir = spec_dir.resolve()
    destination = destination.resolve()
    if destination == spec_dir:
        raise CanonicalIntegrityError("standard mirror cannot overwrite spec")
    if destination in spec_dir.parents:
        raise CanonicalIntegrityError(
            "standard mirror destination cannot be an ancestor of spec"
        )
    if spec_dir in destination.parents:
        raise CanonicalIntegrityError(
            "standard mirror destination cannot be inside spec"
        )


def build_standard_mirror(spec_dir: Path, destination: Path) -> int:
    """Create a clean strict-JSON mirror from the canonical source set."""

    spec_dir = spec_dir.resolve()
    destination = destination.resolve()
    _assert_safe_mirror_destination(spec_dir, destination)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    count = 0
    for path in discover_source_paths(spec_dir):
        rel = path.relative_to(spec_dir)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonc":
            target = target.with_suffix(".json")
            target.write_text(
                json.dumps(
                    _parse_jsonc(path),
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
        else:
            shutil.copyfile(path, target)
        count += 1
    return count
