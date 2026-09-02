from __future__ import annotations

from .base import SynapseGenerationError
from .ros2.generator import ROS2Synapse


AVAILABLE_SYNAPSES = {
    "ros2": ROS2Synapse,
}

UNAVAILABLE_SYNAPSES = {
    "isaac": (
        "The historical Isaac generator was a placeholder and has been removed "
        "from the active registry pending a tested implementation."
    ),
}


def get_synapse(name: str):
    return AVAILABLE_SYNAPSES.get(name.lower())


def unavailable_reason(name: str) -> str | None:
    return UNAVAILABLE_SYNAPSES.get(name.lower())


def list_synapse_targets() -> list[str]:
    return sorted(AVAILABLE_SYNAPSES)
