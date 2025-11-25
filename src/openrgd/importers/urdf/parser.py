import json
import xml.etree.ElementTree as ET
from typing import Dict, Any
from ..base import BaseImporter

class URDFImporter(BaseImporter):
    """
    Ingests standard URDF XML files and maps them to OpenRGD JSONC.
    """
    
    def parse(self) -> Dict[str, Any]:
        self.log(f"Parsing XML structure from {self.source}...")
        
        try:
            tree = ET.parse(self.source)
            root = tree.getroot()
        except Exception as e:
            self.log(f"XML Parsing Error: {e}")
            return {}

        # Override robot name if present in URDF
        if root.get("name"):
            self.robot_name = root.get("name")
        
        # 1. Estrazione Dati
        links = []
        joints = {}
        
        for link in root.findall("link"):
            name = link.get("name")
            if name: links.append(name)
            
        for joint in root.findall("joint"):
            name = joint.get("name")
            jtype = joint.get("type", "fixed")
            limit = joint.find("limit")
            
            # Valori di default sicuri
            effort = 0.0
            velocity = 0.0
            lower = -3.14
            upper = 3.14
            
            if limit is not None:
                try:
                    effort = float(limit.get("effort", 0))
                    velocity = float(limit.get("velocity", 0))
                    lower = float(limit.get("lower", -3.14))
                    upper = float(limit.get("upper", 3.14))
                except ValueError:
                    pass # Se i valori non sono numeri, usa i default
                
            joints[name] = {
                "type": jtype,
                "limits": {
                    "torque_nm": effort,
                    "velocity_rads": velocity,
                    "range_rad": [lower, upper]
                }
            }

        self.log(f"Extracted {len(links)} links and {len(joints)} joints.")

        # 2. Costruzione Struttura RGD (Output Dictionary)
        # Costruiamo i file JSONC risultanti
        
        timestamp = "2025-01-01T00:00:00Z"
        
        # KERNEL
        kernel_content = {
            "meta_group": {
                "id": f"did:rgd:{self.robot_name}",
                "schema_version": "0.1.0",
                "created_at": timestamp
            },
            "module_loading_order_list": [
                "01_foundation/description.jsonc",
                "01_foundation/actuation_dynamics.jsonc",
                "04_volition/alignment.jsonc"
            ]
        }

        # DESCRIPTION
        desc_content = {
            "hardware_id": self.robot_name,
            "imported_from": str(self.source),
            "kinematic_chain": links
        }
        
        # ALIGNMENT (Default)
        align_content = {
            "mission_statement": "Operate safely within imported parameters.",
            "priorities": ["safety", "compliance"]
        }

        # --- ASSEMBLAGGIO ---
        return {
            "spec/00_core/kernel.jsonc": f"/** IMPORTED KERNEL */\n{json.dumps(kernel_content, indent=2)}",
            
            "spec/01_foundation/description.jsonc": f"/** IMPORTED FROM URDF */\n{json.dumps(desc_content, indent=2)}",
            
            "spec/01_foundation/actuation_dynamics.jsonc": f"/** IMPORTED DYNAMICS */\n{json.dumps(joints, indent=2)}",
            
            "spec/04_volition/alignment.jsonc": f"/** DEFAULT ALIGNMENT */\n{json.dumps(align_content, indent=2)}"
        }