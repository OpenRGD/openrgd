from abc import ABC, abstractmethod
from ..core.engine import RGDEngine

class BaseAdapter(ABC):
    def __init__(self, engine: RGDEngine):
        self.engine = engine

    @abstractmethod
    def spin(self):
        """Starts the main loop of the middleware."""
        pass

    @abstractmethod
    def publish_intent(self, intent: dict):
        """Sends a decision to the actuators."""
        pass