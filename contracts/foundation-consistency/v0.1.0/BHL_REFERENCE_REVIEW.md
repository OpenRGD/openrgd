# BHL reference review — fixture evidence only

Baseline exact Core `afe1a831b950a4e6560f0285a0103fc4eaa343b7`; 01B exact `cb23d15f8f08462aaf020d101732b9915d391115`. [01B CI](https://github.com/OpenRGD/openrgd/actions/runs/46110271989) logs 162 occurrences, 133 resolved, 29 unresolved and two findings. 76 indexed files, unchanged V1 root. This is a **reference-document audit**, not Paky-01 as-built inventory or a physical diagnostic.

| Evidence | Occurrences | Required owner decision |
|---|---:|---|
| Actuation target_joint_ref_str -> Description joint_topology_map | 16 | Model owner provides exact identity mapping and authoritative nominal topology; do not assume the existing knee name is equivalent or create 16 fake joints. |
| Actuation component_model_ref_str -> library component_catalog_map | 8 | One repeated missing catalog identifier tmotor_ak60_6_v1. Supply independently sourced reviewed catalog/model revision or correct the actual design selection; do not synthesize specs or substitute a similar model. |
| CAL kinematic_offsets_map hip_pitch_right | 1 | CAL + model owners establish intended joint and measurement provenance; no alias/reseal. |
| Fidelity runtime_validation_ref_str | 1 | Exact field role in 01B is 02_operation/runtime_validation.jsonc. Existing field points to 01_foundation/runtime_validation.jsonc. The target file exists and is indexed. Only deterministic path correction is ready for an isolated candidate migration. |
| Fidelity right_wrist_ft | 1 | Model owner validates whether sensor is intended or sample from another design; do not fabricate geometry/device. |
| HAL ankle_pitch_right_actuator | 1 | Model/HAL owner validates explicit instance mapping; not a joint or model ID. |
| HAL wifi_rf_monitor | 1 | Model/HAL owner establishes intended sensor identity; do not equate with wifi_rf_module by similarity. |
| Legacy target_description_hash_str empty digest | separate | Preserve historic data. Versioned digest semantics and original measurement applicability require separate review. |
| calibration_validity MAJOR global false/local block false | separate | Safety owner reviews policy precedence and action scope; proposed conservative static projection BLOCK_REQUIRED plus review conflict, never a runtime permission. |

The candidate path change is isolated to a disposable copy. No alias table, fabricated specs, policy rewrite, measurement binding or modification of canonical spec, standard mirror, seed or robot files. The fixture migration must check original V1 root, exact old field and target path, exact byte delta, reseal via actual Core, and independently rerun 01B. Historical root is unchanged. New revision needs owner review and separate approval. Other occurrence groups stay unresolved. Do not mark reference conformance PASS simply because CI expected these failures.
