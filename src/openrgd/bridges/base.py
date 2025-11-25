from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseBridge(ABC):
    """
    The Abstract Interface for all OpenRGD Bridges.
    Every export adapter (ROS2, Isaac, etc.) must inherit from this.
    """
    
    def __init__(self, kernel_data: Dict[str, Any], spec_dir: Path):
        self.kernel = kernel_data
        self.spec_dir = spec_dir
        self.robot_id = kernel_data.get("meta_group", {}).get("id", "unknown")

    @abstractmethod
    def generate(self, output_dir: Path) -> None:
        """
        The main method that writes the configuration files to disk.
        Must be implemented by the specific bridge.
        """
        pass

    def log(self, msg: str):
        """Bridge-specific logging helper."""
        print(f"  [BRIDGE:{self.__class__.__name__}] {msg}")