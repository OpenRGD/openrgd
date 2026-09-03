from pathlib import Path
from typing import Dict, Any
from ...core.utils import load_jsonc
from ...core.visuals import log

class RGDEngine:
    """
    The Pure Logic Core.
    Decoupled from the communication layer (ROS2/Viam).
    """
    def __init__(self, spec_dir: Path):
        self.spec_dir = spec_dir
        self.state = {
            "world_model": {},
            "system_health": {},
            "active_intent": None
        }
        
        # 1. Load the Cognitive BIOS
        self.kernel = self._load_module("00_core/kernel.jsonc")
        self.hal = self._load_module("01_foundation/hal_mapping.jsonc")
        self.safety = self._load_module("02_operation/safety_supervisor.jsonc")
        
        log("Cognitive Engine Initialized.", "SYSTEM")

    def _load_module(self, rel_path: str) -> Dict:
        path = self.spec_dir / rel_path
        if not path.exists():
            log(f"Missing core module: {rel_path}", "WARN")
            return {}
        return load_jsonc(path)

    def process_perception(self, sensor_id: str, data: Any) -> Dict:
        """
        Ingests raw data, validates confidence, updates world model.
        Returns a reaction/command if needed.
        """
        # Esempio di logica RGD pura:
        # Se il dato arriva da un sensore non mappato nel HAL, ignoralo.
        # (Qui andrebbe la logica di perception_pipeline.jsonc)
        
        self.state["world_model"][sensor_id] = data
        return {"status": "UPDATED", "reflex_trigger": False}

    def validate_command(self, actuator_id: str, value: float) -> bool:
        """
        Checks if a command violates the safety envelope.
        """
        # Esempio: Check against safety_supervisor limits
        max_val = self.safety.get("max_impact_energy_j_float", 100.0)
        if value > max_val:
            log(f"Safety Veto on {actuator_id}: {value} > {max_val}", "AI")
            return False
        return True