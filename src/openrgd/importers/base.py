from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseImporter(ABC):
    """
    Abstract Interface for ingestion modules.
    """
    
    def __init__(self, source_path: str):
        self.source = Path(source_path)
        # Normalizza il nome: rimuove estensione e caratteri strani
        self.robot_name = self.source.stem.lower().replace(" ", "_").replace("-", "_")

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Must return a dictionary of {filepath: content_string}
        representing the RGD structure.
        """
        pass

    def log(self, msg: str):
        print(f"  [IMPORT:{self.__class__.__name__}] {msg}")