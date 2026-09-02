from __future__ import annotations

import json
import re
from typing import Any, Dict

from ..base import BaseImporter


class USDImporter(BaseImporter):
    """Import an ASCII USD/USDA description into a partial OpenRGD spec.

    The importer extracts only facts supported by the source file. It does not
    synthesize a kernel, safety policy, alignment profile or other multi-domain
    material. ``rgd alive`` owns the later merge with a reviewed packaged seed.
    """

    def parse(self) -> Dict[str, Any]:
        self.log(f"Parsing USD structure from {self.source}...")

        try:
            content = self.source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.log(
                "Error: only ASCII/text USD files are supported. "
                "Convert binary .usd/.usdc content to .usda first."
            )
            return {}
        except OSError as exc:
            self.log(f"Read error: {exc}")
            return {}

        name_match = re.search(r'defaultPrim\s*=\s*"([^"]+)"', content)
        if name_match:
            self.robot_name = name_match.group(1)

        joint_pattern = re.compile(
            r'def\s+Physics(Revolute|Prismatic)Joint\s+"([^"]+)"',
            re.MULTILINE,
        )
        joints: dict[str, dict[str, Any]] = {}

        for match in joint_pattern.finditer(content):
            joint_type = match.group(1).lower()
            joint_name = match.group(2)

            block_start = match.end()
            block_end = content.find("def ", block_start)
            if block_end == -1:
                block_end = len(content)
            joint_block = content[block_start:block_end]

            lower = self._read_float(
                joint_block,
                r'float:physics:lowerLimit\s*=\s*([-+0-9.eE]+)',
                -3.14,
            )
            upper = self._read_float(
                joint_block,
                r'float:physics:upperLimit\s*=\s*([-+0-9.eE]+)',
                3.14,
            )
            stiffness = self._read_float(
                joint_block,
                r'float:drive:angular:physics:stiffness\s*=\s*([-+0-9.eE]+)',
                0.0,
            )
            damping = self._read_float(
                joint_block,
                r'float:drive:angular:physics:damping\s*=\s*([-+0-9.eE]+)',
                0.0,
            )
            max_force = self._read_float(
                joint_block,
                r'float:drive:angular:physics:maxForce\s*=\s*([-+0-9.eE]+)',
                100.0,
            )

            joints[joint_name] = {
                "type": joint_type,
                "limits": {
                    "torque_nm": max_force,
                    "range_rad": [lower, upper],
                },
                "source_parameters": {
                    "usd_drive_stiffness": stiffness,
                    "usd_drive_damping": damping,
                },
            }

        self.log(f"Extracted {len(joints)} physics joints from USD.")

        description = {
            "hardware_id": self.robot_name,
            "imported_from": str(self.source),
            "source_format": "USD_ASCII",
            "notes": "Partial Foundation evidence imported from a USD scene.",
        }

        return {
            "spec/01_foundation/description.jsonc": (
                "/** IMPORTED FROM USD; PARTIAL FOUNDATION EVIDENCE */\n"
                + json.dumps(description, indent=2)
            ),
            "spec/01_foundation/actuation_dynamics.jsonc": (
                "/** IMPORTED FROM USD PHYSICS; PARTIAL FOUNDATION EVIDENCE */\n"
                + json.dumps(joints, indent=2)
            ),
        }

    @staticmethod
    def _read_float(block: str, pattern: str, default: float) -> float:
        match = re.search(pattern, block)
        if not match:
            return default
        try:
            return float(match.group(1))
        except ValueError:
            return default
