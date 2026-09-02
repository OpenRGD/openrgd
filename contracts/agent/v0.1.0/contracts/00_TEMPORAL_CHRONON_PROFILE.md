# OpenRGD Temporal/Chronon Interoperability Profile v0.1

Status: **FORMALIZATION CANDIDATE**  
Scope: Robot Chronograf ↔ RGD-Physics ↔ OpenRGD Embodied Runtime  
Goal: preserve the most advanced existing work while removing ambiguity between TimeAtom, anchor, Chronon, Aion, and memory.

## 1. Normative ownership

The stack MUST preserve these ownership boundaries:

| Component | Owns | MUST NOT own |
|---|---|---|
| Robot Chronograf | time measurement, clock-domain identity, uncertainty, temporal channels, anchor issuance/resolution | robot memory semantics, physics payloads |
| RGD-Physics | Chronon semantics, spacetime metric/laws, Aion payload/isotopes, causal/physics validation | wall-clock authority, UTC/GNSS/PTP synchronization |
| OpenRGD Embodied Runtime | agent identity, goals, cognition adapters, capability execution, projection/recall | canonical time or canonical history |
| Projection stores | facts, skills, episodes, summaries, indexes | source-of-truth life history |

The canonical life history of an embodied agent MUST be a sequence/DAG of **Chronons** anchored through Robot Chronograf.

## 2. The temporal primitive

### 2.1 Clock Domain

A measured unit of time is meaningful only inside a declared clock domain.

A `ClockDomainRef` MUST identify:

- `clock_domain_id_str`: unique domain instance;
- `layer_enum_str`: CHRONOS / KAIROS / AION / METACHRONOS / ESCHATON;
- `clock_kind_enum_str`: WALL_CLOCK / MONOTONIC / SIMULATION / SUBJECTIVE / RELATIONAL / LOGICAL;
- `epoch_ref_str`: the epoch or origin used by the domain;
- `timescale_enum_str`: UTC / TAI / MONOTONIC / SIM / LOGICAL / domain-specific;
- optional `boot_id_str` for reboot-scoped clocks;
- optional `parent_domain_refs_arr` for cross-domain mappings.

Examples:

```text
chronos.utc.system
chronos.monotonic.boot:<boot-id>
sim:<sim-id>
kairos.agent:<agent-id>
aion.interaction:<context-id>
```

### 2.2 TimeAtom

The existing Robot Chronograf `TimeAtom v1` remains the canonical measured coordinate:

```text
epoch_seconds_int
subsecond_ticks_uint
tick_resolution_exp10_int
timescale_enum_str
uncertainty_group
sync_class_enum_str
reference_chain_arr
```

A TimeAtom MUST NOT be interpreted without its `ClockDomainRef` when the clock domain cannot be inferred unambiguously.

`reference_chain_arr` records time-evidence/provenance references; it is not a substitute for `clock_domain_id_str`.

### 2.3 Temporal Barcode

The existing Temporal Barcode remains the event-time envelope and MUST bind:

- TimeAtom;
- Chronograf channel;
- runtime loop;
- OpenRGD domain;
- event kind;
- source/target/context/payload references when available.

## 3. ChronografAnchorRef64

RGD-Physics already reserves a 64-bit `anchor` field. The full TimeAtom is richer and MUST NOT be truncated into that field.

The 64-bit field is therefore formalized as an **opaque anchor handle**.

```text
ChronografAnchorRef64 :=
    anchor_namespace_id_str
  + anchor_handle_uint64
  + time_atom_sha256_hex_str
```

Rules:

1. `anchor_handle_uint64 = 0` is reserved and invalid.
2. Handles are allocated monotonically within one `anchor_namespace_id_str`.
3. A handle is NOT a timestamp and MUST NOT be decoded as one.
4. The globally meaningful identity is `(namespace, handle, time_atom_hash)`.
5. Handles MAY restart only when the namespace changes.
6. Ordering across namespaces MUST use TimeAtom/cross-domain evidence/causal links, not numeric handle comparison.
7. Resolution MUST verify the stored TimeAtom hash.

Recommended namespace:

```text
urn:rgd:chronograf:<agent-id>:boot:<boot-id>
```

A persistent life may span many anchor namespaces. Reboots are connected through `MCH_HYPOSTASIS` Chronons.

## 4. Anchor Record

Robot Chronograf owns the append-only mapping from AnchorRef64 to the full temporal measurement.

An `AnchorRecord` MUST contain:

```text
anchor_ref
clock_domain_ref
time_atom
optional temporal_barcode
previous_anchor_ref     # issuance chain in same namespace
causal_parent_anchor_refs
integrity hashes
```

One TimeAtom MAY anchor multiple Chronons when several states/events are intentionally treated as simultaneous observations of the same measured instant. Default runtime behavior SHOULD issue one anchor per meaningful emitted event.

External attestations (GNSS/NTS/Roughtime/RFC3161/transparency-log receipts) SHOULD be linked as immutable evidence records rather than mutating an already-issued anchor.

## 5. Chronon

A Chronon is the immutable reality/history envelope anchored to a Robot Chronograf measurement.

Normative semantic model:

```text
Chronon
├── chronon_id
├── agent_id / life_id
├── local chronon sequence
├── ChronografAnchorRef64
├── metric / spacetime coordinates
├── local laws / physics metadata
├── Aion payload encoding
├── facets[]
├── previous_chronon_id
├── causal_parent_chronon_ids[]
└── integrity commitment
```

The Chronon is the canonical historical object. It is not a database event row.

## 6. Aion

The Aion is the state/payload isotope carried by a Chronon.

The existing RGD-Physics classes (`Aion128`, `Aion512`, `Aion4096`, `Aion16384`) are retained for compatibility. Their current binary layout includes the Chronon header (`anchor`, metric, laws) together with the payload; this profile calls that legacy representation a **packed Chronon/Aion frame**.

Future refactoring MAY separate envelope and payload classes, but MUST preserve wire compatibility or provide explicit versioned codecs.

`Aion16384` is the natural bridge for HyperAion semantic vectors; it does not change the 64-bit anchor-ref rule.

## 7. Facets / parametric life state

A Chronon MAY carry multiple independently typed facet references. Standard facet kinds:

```text
PHYSICAL
PERCEPTUAL
COGNITIVE
PSYCHOLOGICAL
VOLITIONAL
ETHICAL
CONTEXTUAL
SOCIAL
MEMORY_RECALL
LEARNING
```

A facet is represented by:

```text
facet_kind_enum_str
payload_ref_str
payload_sha256_hex_str
media_type_str
schema_ref_str?
```

This prevents Chronons from becoming giant monolithic JSON objects while still allowing the complete physical, psychological, and contextual life of the robot to be reconstructed.

## 8. Causality

Chronology and causality are different.

Chronons MUST support:

- `previous_chronon_id_str`: local append order / life-ledger predecessor;
- `causal_parent_chronon_ids_arr`: semantic/physical causal DAG;
- AnchorRecord `causal_parent_anchor_refs_arr`: cross-system temporal causality when needed.

A later timestamp does not by itself prove causation.

## 9. Memory projections

The embodied runtime tables `events`, `episodes`, `facts`, and `skills` become projections/indexes over Chronons.

```text
Chronons (canonical append-only life history)
        │
        ├── Episodes
        ├── Facts / beliefs
        ├── Skills / procedural memory
        ├── Self model
        ├── Social memory
        └── summaries / embeddings / retrieval indexes
```

Projection records MAY be rebuilt. Chronons MUST NOT depend on projections for historical validity.

A fact such as `gripper gain ≈ 0.84` MUST carry evidence references to the Chronons from which it was consolidated. A later observation changes the projection; it does not rewrite old Chronons.

## 10. Chronograf channel profile for embodied runtime

Default mapping:

| Embodied event | Channel | Loop | Domain | Facet |
|---|---|---|---|---|
| physical observation | CHR_CORE | loop_chronos_core | D01_FOUNDATION | PHYSICAL |
| action result / motor commit | CHR_CAUSAL | loop_chronos_core | D02_OPERATION | PHYSICAL |
| action intent / model proposal | KAI_BASE | loop_kairos_cognition | D03_AGENCY | COGNITIVE |
| prediction / dry-run | KAI_PREDICT | loop_kairos_cognition | D03_AGENCY | COGNITIVE |
| safety decision | MCH_ANANKE | loop_kairos_cognition | META_CROSS | VOLITIONAL |
| integrity/runtime error | MCH_ALETHEIA | loop_chronos_core | META_CROSS | CONTEXTUAL |
| learning/consolidation | KAI_ONEIRIC | loop_kairos_oneiric | D05_EVOLUTION | LEARNING |
| identity creation/reboot continuity | MCH_HYPOSTASIS | loop_chronos_core | META_CROSS | CONTEXTUAL |
| human semantic observation | AIO_INTERACTION | loop_aion_interaction | D06_ETHER | SOCIAL |
| emergency stop/off | ESC_GRACE | loop_chronos_core | META_CROSS | PHYSICAL |

The mapping is a default profile, not a restriction on future channels.

## 11. Legacy migration

Existing `memory.sqlite3` rows are valid historical evidence but use float `created_at` timestamps. Migration MUST:

1. retain the original event row unchanged;
2. create a TimeAtom using the old timestamp;
3. label the clock domain `legacy.posix.system`;
4. mark sync/evidence quality as legacy/unattested;
5. create a Temporal Barcode according to the mapping above;
6. issue an AnchorRef64;
7. create one Chronon containing a commitment to the original payload;
8. persist an `event_id → chronon_id` migration link;
9. never migrate the same event twice.

Migration does not invent stronger temporal certainty than the original log possessed.

## 12. Integrity

At minimum:

- payloads are SHA-256 committed;
- TimeAtoms are SHA-256 committed inside AnchorRef64;
- Chronons are content-committed;
- local Chronons form an append-only predecessor chain;
- MCH_ALETHEIA is used for detected timeline/integrity violations.

Cryptographic signing/transparency-log anchoring is an upper profile and is intentionally separate from the core local runtime contract.

## 13. Non-goals of v0.1

This profile does not yet standardize:

- cross-robot global anchor-handle allocation;
- legal timestamp attestation;
- a global transparency log;
- final JCS/CBOR canonicalization;
- spatial metric encoding beyond the current RGD-Physics contract;
- a complete HyperAion-to-Chronon facet schema.

Those can evolve without changing the core rule: **Chronograf measures/anchors time; RGD-Physics defines the Chronon; OpenRGD projects memory from Chronons.**
