from .ros2.generator import ROS2Bridge
from .isaac.generator import IsaacBridge

# Registry dei bridge supportati
AVAILABLE_BRIDGES = {
    "ros2": ROS2Bridge,
    "isaac": IsaacBridge
}

def get_bridge(name: str):
    return AVAILABLE_BRIDGES.get(name)