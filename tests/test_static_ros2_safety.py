from __future__ import annotations

from openrgd.synapses.ros2.generator import ROS2Synapse


def test_imported_body_cannot_inherit_seed_hal_by_joint_name_collision() -> None:
    """Seed HAL must not bind an imported body merely by matching a joint name."""

    description = {
        "meta_group": {
            "file_role_enum": "IMPORTED_PARTIAL_DESCRIPTION",
        },
        "joint_topology_map": {
            "knee_joint_right": {
                "type_enum": "REVOLUTE",
                "limits_ideal": {
                    "position_lower_rad_float": -1.0,
                    "position_upper_rad_float": 1.0,
                    "velocity_max_rad_s_float": 2.0,
                    "effort_max_nm_float": 4.0,
                },
            }
        },
    }
    dynamics = {
        "joint_dynamics_map": {
            "knee_joint_right": {
                "joint_type_enum": "REVOLUTE",
                "target_joint_ref_str": "knee_joint_right",
            }
        }
    }
    seed_topology = {
        "control_profiles_map": {},
        "joint_actuator_mapping_map": {
            "seed_knee_actuator": {
                "target_joint_ref_str": "knee_joint_right",
            }
        },
    }
    seed_hal = {
        "actuator_drivers_map": {
            "seed_knee_actuator": {
                "driver_plugin_str": "seed_driver/UnsafeCoincidentalMatch",
                "ros2_control_interface_list_enum": ["position"],
                "device_node_id_int": 12,
            }
        }
    }

    synapse = object.__new__(ROS2Synapse)
    records = synapse._build_joint_records(
        description=description,
        dynamics=dynamics,
        topology=seed_topology,
        hal_mapping=seed_hal,
    )

    assert len(records) == 1
    assert records[0].name == "knee_joint_right"
    assert records[0].driver_plugin is None
    assert records[0].interfaces == ()
    assert records[0].device_node_id is None
