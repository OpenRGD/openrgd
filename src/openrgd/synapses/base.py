from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseSynapse(ABC):
    """
    The Abstract Interface for all OpenRGD Synapses.
    A Synapse connects the internal Cognitive Kernel to an external ecosystem
    (ROS2, Isaac, Viam, etc.) by translating intent and configuration.
    """
    
    def __init__(self, kernel_data: Dict[str, Any], spec_dir: Path):
        self.kernel = kernel_data
        self.spec_dir = spec_dir
        self.robot_id = kernel_data.get("meta_group", {}).get("id", "unknown")

    @abstractmethod
    def generate(self, output_dir: Path) -> None:
        """
        Materializes the connection. Writes configuration artifacts to disk.
        """
        pass

    def log(self, msg: str):
        """Synapse-specific logging helper."""
        # Usa il nome della classe (es. ROS2Synapse) nel log
        print(f"  [SYNAPSE:{self.__class__.__name__}] {msg}")