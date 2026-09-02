from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
from pathlib import Path
import re
from typing import Any, Dict


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class BaseImporter(ABC):
    """Abstract interface for source-description ingestion modules."""

    def __init__(self, source_path: str):
        self.source = Path(source_path)
        self.robot_name = self.normalize_robot_name(self.source.stem)

    @staticmethod
    def normalize_robot_name(value: str) -> str:
        """Return a path-safe, stable identifier without changing case."""

        normalized = _SAFE_NAME_RE.sub("-", str(value).strip()).strip("._-")
        if not normalized:
            normalized = "robot"
        return normalized[:128]

    def set_robot_name(self, value: str) -> None:
        self.robot_name = self.normalize_robot_name(value)

    def source_artifact(self, format_name: str) -> dict[str, Any]:
        """Describe source provenance without embedding a machine-local path."""

        payload = self.source.read_bytes()
        return {
            "source_filename_str": self.source.name,
            "source_format_enum": format_name.upper(),
            "source_sha256_str": f"sha256:{hashlib.sha256(payload).hexdigest()}",
            "source_size_bytes_int": len(payload),
        }

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Return ``{relative_path: UTF-8 text}`` partial OpenRGD evidence."""

    def log(self, msg: str) -> None:
        print(f"  [IMPORT:{self.__class__.__name__}] {msg}")
