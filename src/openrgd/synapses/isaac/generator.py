from pathlib import Path
from ..base import BaseSynapse # Import base

class IsaacSynapse(BaseSynapse):
    """
    Connects OpenRGD to NVIDIA Isaac Lab.
    Generates Python configuration classes for RL.
    """
    def generate(self, output_dir: Path) -> None:
        self.log(f"Extending neural pathways to Isaac Lab for {self.robot_id}...")
        # ... (Logica identica a prima, cambia solo il nome della classe) ...
        # Per brevità non la ricopio tutta, ma assicurati di cambiare 'class IsaacBridge' in 'class IsaacSynapse'