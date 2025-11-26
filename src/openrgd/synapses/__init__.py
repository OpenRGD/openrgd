from .ros2.generator import ROS2Synapse
from .isaac.generator import IsaacSynapse

# Registry Ufficiale
AVAILABLE_SYNAPSES = {
    "ros2": ROS2Synapse,
    "isaac": IsaacSynapse
}

def get_synapse(name: str):
    return AVAILABLE_SYNAPSES.get(name.lower())