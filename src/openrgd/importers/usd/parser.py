import re
import json
from pathlib import Path
from typing import Dict, Any
from ..base import BaseImporter
from ...core.templates import get_templates

class USDImporter(BaseImporter):
    """
    Ingests USD (Universal Scene Description) files in ASCII format (.usda).
    Extracts PhysicsJoints and Drives to reconstruct the OpenRGD definition.
    """
    
    def parse(self) -> Dict[str, Any]:
        self.log(f"Parsing USD structure from {self.source}...")
        
        try:
            with open(self.source, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            self.log("❌ Error: Can only parse ASCII USD files (.usda). Convert .usd to .usda first.")
            return {}
        except Exception as e:
            self.log(f"❌ Read Error: {e}")
            return {}

        # 1. Trova il nome del robot (Default Prim)
        # Cerca: defaultPrim = "RobotName"
        name_match = re.search(r'defaultPrim\s*=\s*"([^"]+)"', content)
        if name_match:
            self.robot_name = name_match.group(1)

        # 2. Estrazione Giunti (PhysicsRevoluteJoint / PhysicsPrismaticJoint)
        # Pattern: def PhysicsRevoluteJoint "joint_name"
        joint_pattern = re.compile(r'def\s+Physics(Revolute|Prismatic)Joint\s+"([^"]+)"', re.MULTILINE)
        
        joints = {}
        
        for match in joint_pattern.finditer(content):
            j_type = match.group(1).lower() # revolute or prismatic
            j_name = match.group(2)
            
            # Cerca il blocco del giunto per trovare i limiti
            # (Questo è un parser semplificato, cerca nelle righe successive)
            block_start = match.end()
            block_end = content.find("def ", block_start) # Cerca il prossimo def come fine blocco
            if block_end == -1: block_end = len(content)
            
            joint_block = content[block_start:block_end]
            
            # Estrazione Limiti
            lower = -3.14
            upper = 3.14
            limit_match = re.search(r'float:physics:lowerLimit\s*=\s*([-0-9.]+)', joint_block)
            if limit_match: lower = float(limit_match.group(1))
            
            limit_match = re.search(r'float:physics:upperLimit\s*=\s*([-0-9.]+)', joint_block)
            if limit_match: upper = float(limit_match.group(1))

            # Estrazione Drive (Stiffness/Damping -> PID)
            stiffness = 0.0
            damping = 0.0
            drive_stiff = re.search(r'float:drive:angular:physics:stiffness\s*=\s*([-0-9.]+)', joint_block)
            if drive_stiff: stiffness = float(drive_stiff.group(1))
            
            drive_damp = re.search(r'float:drive:angular:physics:damping\s*=\s*([-0-9.]+)', joint_block)
            if drive_damp: damping = float(drive_damp.group(1))
            
            # Estrazione Max Force
            max_force = 100.0
            force_match = re.search(r'float:drive:angular:physics:maxForce\s*=\s*([-0-9.]+)', joint_block)
            if force_match: max_force = float(force_match.group(1))

            joints[j_name] = {
                "type": j_type,
                "limits": {
                    "torque_nm": max_force,
                    "range_rad": [lower, upper]
                },
                # Qui salviamo i parametri Isaac originali per il round-trip perfetto
                "isaac_params": {
                    "stiffness": stiffness,
                    "damping": damping
                }
            }

        self.log(f"Extracted {len(joints)} physics joints from USD.")

        # 3. Costruzione Struttura RGD
        rgd_structure = get_templates(self.robot_name)
        
        desc_content = {
            "hardware_id": self.robot_name,
            "source_format": "USD",
            "notes": "Imported from Isaac Sim context"
        }
        
        rgd_structure["spec/01_foundation/description.jsonc"] = \
            f"/** IMPORTED FROM USD */\n{json.dumps(desc_content, indent=2)}"
            
        rgd_structure["spec/01_foundation/actuation_dynamics.jsonc"] = \
            f"/** IMPORTED FROM ISAAC PHYSICS */\n{json.dumps(joints, indent=2)}"

        return rgd_structure