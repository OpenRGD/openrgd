# VIS-0.1A — Evolvable embodiment: visual/CAD revisions and OpenRGD Evolution crosswalk

**2026-11-17 · NON-NORMATIVE CANDIDATE / DESIGN NOTE.** This is a proposed interpretation, not a change to `spec/`, `standard/`, the source-root hash, a Life issuer, physical commissioning or robot actuation. It accompanies `rgd.visual-assets.v0.1-candidate` for review before any Console implementation promotes semantics.

## What exists today (source-checked, not an assumed implementation)

The canonical repository has all six original `spec/05_evolution/*.jsonc` files, with strict JSON mirrors in `standard/05_evolution/*.json`:

| Existing source | Historical intent | Required reinterpretation |
| --- | --- | --- |
| `hardware_mutation.jsonc` | Replacement/integration of parts, graceful degradation and an example 75% core-replacement identity threshold | POLICY ONLY, never a physical mutation executor; no percentage may automatically create/revoke a legal RIN, physical enrollment or Life. |
| `plasticity.jsonc` | Constraints on self-modifying skills, behavior and calibration | POLICY ONLY; semantic/learning plasticity distinct from morphology/CAD changes. Proposed numeric gains/drifts are not runtime-conformance or default permission. |
| `genealogy.jsonc` | Origin and mutation_log of instance lineage | Portably readable PROJECTION of evidence, not authoritative append-only Chronon/history or signed proof of identity. |
| `replication.jsonc` | Fork, clone and inheritance options | Separate enrollment/explicit fork; a copied file/backup does not instantiate the same Life. |
| `digital_resurrection.jsonc` | Backup/restore continuity | Recovery requires current external authority/history watermark, not trusting a bundled checkpoint. |
| `termination.jsonc` | Decommissioning and asset transfer | Separate owner/legal authorization; a ZIP import cannot execute decommission actions. |

`spec/manifest.jsonc` declares **05_evolution = optional, PROPOSAL**. The reference kernel `spec/00_core/kernel.jsonc` does **not** select its files in `module_loading_order_list`. Their sample content is NOT active policy. Several `plasticity` refs use `.json` mirror paths rather than canonical `.jsonc` and need versioned reconciliation; do not rewrite historical source/hashes silently.

`01_foundation/description.jsonc` is ideal design intent (CAD perfection in the legacy comments); `calibration.jsonc` describes instance-specific measured deltas, including joint zero, IMU/camera extrinsics and friction/mass differences. `wear_fatigue_model.jsonc` is a degradation MODEL, not live observed wear. A new structural component is not merely a new calibration offset.

Core-C Life/identity candidate (PR #13) explicitly distinguishes **exact RGD source_root, physical enrollment, LifeIdentity, RobotLifeBinding, runtime/boot/session** and states that model revision **may change without issuing a new Life only after external binding/context revalidation**. Core-D Temporal/Memory candidate (PR #14) places canonical history/Chronons in external authenticated History writer and derived memories/annotations separately; a timestamp in a package does not prove qualified time or successful durable history commit. These PRs are proposals, not active authority services.

## Three different meanings of plasticity (not interchangeable)

The historical `05_evolution/plasticity.jsonc` addresses *neural/behavioral self-modification and changes in configuration policy*. It is NOT a deformable-material physics contract or a declaration of installed hardware.

The separate `01_foundation/soft_body_dynamics.jsonc` and `soft_materials_library.jsonc` describe **reference** deformable components, elastic modulus, self-healing material examples and passive/active soft-body response. `01_foundation/wear_fatigue_model.jsonc` describes wear/fatigue models. These examples are NOT evidence that Paky-01 physically has smart artificial skin or a self-healing subsystem.

Therefore distinguish:
1. **Transient elastic/deformable state** — changes with load/temperature and returns without replacing hardware; source design and as-built revision remain the same, runtime telemetry may vary. Renderer may use measured deformation signals ONLY if source and frame are validated, never invent them.
2. **Persistent morphological change** — a permanently deformed component, wear outside a verified envelope, new shell/limb, sensor relocation, repair or replacement. Create an as-built **mutation event/revision**, with inspection/calibration consequences; changes to ideal design only via explicit versioned model revision.
3. **Behavioral/neuroplastic learning** — a change to skills, weights, policies or agency, under separate `05_evolution/plasticity` and Agency governance; no CAD mesh update, motor action grant or physical identity alteration follows automatically.

A cosmetic **digital** texture/GLB change is a fourth distinct **visual-only** revision: no proof that physical hardware or appearance has changed.

## Essential distinction: four independently revisioned dimensions

| Dimension | Immutable/revisioned key | What changes | Who may attest |
| --- | --- | --- | --- |
| **Design model** | `model_revision.source_root` / exact version | Ideal joint tree, limits, link frames, CAD design | Reviewed Forge/model publisher; not the browser |
| **Visual asset set** | `asset_set_revision.manifest_sha256` and each `asset.sha256` | STL→GLB/LOD/materials/appearance; link-local visual XYZ/RPY | Content integrity + source attribution; **not physical evidence** |
| **Physical as-built** | `physical_instance_ref` + append-only `as_built_revision` | Actually installed component, physical dimensions, cables, sensors, serials | Authorized human / commissioning evidence; not CAD similarity |
| **Calibration and operation** | exact `calibration_revision` + safety/binding revisions | Measured joint zeros, encoder sign/ratio, extrinsics, validated envelopes | External calibration/safety issuer; not visual import |
| **Experiential Life** | externally issued `life_id` / verified binding revision | Potentially endures physical/model replacement | External Identity/Life authority only; no self-claimed continuity |

A new GLB LOD modifies **only asset-set revision**, never model identity, physical instance or Life by itself. A physically replaced arm changes an **as-built revision**, invalidates affected mechanical/encoder/calibration/binding claims and may trigger a reviewed **design model revision** if the design topology changed. No change here grants an operation or control effect.

## Proposed portable RGD *revision snapshot* representation

RGD canonical **`spec/` files remain immutable once identified by source-root hash**. A ZIP-backed `.rgd` transport MAY eventually carry optional, independently versioned candidate metadata alongside `spec/` without silently changing `OPENRGD_SOURCE_TREE_SHA256_V1`:

```text
robot-snapshot.rgd    # ZIP transport, not a new normative binary format
  spec/                      # immutable source model snapshot
  assets/visual/manifest.json # content-addressed appearance set
  instances/<instance-ref>/as-built.snapshot.json
  evolution/revision-index.json # append-only history *references*/projection, not canonical Chronons
```

For the first **VIS-CONSOLE-0.1A** feature, implement only a **read-only descriptive revision index/manifest projection** and metadata validation; no authoritative lifecycle writer and no physical as-built update API.

A candidate as-built revision record should identify:
- exact `physical_instance_ref` (locally claimed unless enrollment receipt authenticated);
- `model_source_root` (immutable); `visual_manifest_sha256` and `as_built_revision_id` (separate);
- `predecessor_as_built_revision_ref` and `evidence_refs`; explicit update class;
- per-slot `component_slot_id`, prior/next component claims and source serials **only if verified**, installed/removed/unknown status;
- impacted link/joint/sensor refs, `calibration_required` and `verification_state`;
- explicit `event_time_assertion` vs future authenticated `history_commit_ref`/Chronograf anchor (no backdated verified timestamps);
- `author_claim` vs authenticated issuer receipt, and `effect_authorized: false`.

A candidate mutation record can move through **PROPOSED → INSTALLED_UNVERIFIED → CALIBRATION_REQUIRED → VERIFIED → ACTIVE_DECLARED** as documentation, but the receiver must enforce independent, externally authorized transitions. `ACTIVE_DECLARED` is not a runtime safety permit. On history commit failure, do not retroactively claim durability. Previous revisions and superseded asset hashes remain addressable for rollback/forensic comparison; never overwrite in place.

### Examples and required treatment

| Change | Design source root | Visual set | As-built | Required safety/calibration consequence |
| --- | --- | --- | --- | --- |
| Different color/LOD of same CAD | unchanged | new revision | unchanged | NONE for pure preview |
| Cosmetic replacement of actual shell | possibly unchanged | new version | new revision if actually installed | assess mass/edges/collision claims; never infer unchanged safety |
| IMU repositioned | nominal design may remain | optional | new installed revision | invalidate IMU extrinsics; suspend affected pose claims |
| Replace right arm with different actuator/geometry | potentially new design revision | new | new | invalidate joint mapping, motor limits, encoder zero, FK and related effects until separate review |
| Learn improved grasp policy | unchanged | unchanged | unchanged | `03_agency` policy/skill revision under separate Plasticity/Work approval, not CAD change |
| Export a modified RGD ZIP | immutable prior `source_root` retained; new release if spec changed | independently keyed | instance unchanged unless physical evidence | model import is NOT new enrollment/Life/fork |

## What not to adopt from the legacy example without review

- `max_core_replacement_pct_float=0.75` and `MANDATORY_NEW_RIN_REGISTRATION` are **historical proposal values**, not verified legal or identity issuance criteria. Revocation/enrollment/fork belongs outside RGD spec and requires explicit, independently authenticated decision.
- `max_autonomous_gain_float=0.15` and the proposed `0.05` personality drift are not measurable permission semantics and should not be mapped to CAD changes or behavioral authorization.
- A `genealogy.mutation_log_list` embedded in a mutable ZIP is NOT append-only canonical history, regardless of field name. It can include immutable event hashes and references with provenance, under explicit reliability labels.
- A changed file SHA-256 proves byte identity, **not who signed it**, that the physical part is installed, or that the change is safe.

## VIS-CONSOLE-0.1A implementation gates (non-actuating)

1. Preserve current Console `ImportedModel` legacy JSON fields and ZIP-based IDs for backwards compatibility; expose source model revision separately from visual-set and as-built candidate refs. Do NOT reinterpret a ZIP hash as physical robot identity.
2. Preserve **both joint origin XYZ and origin RPY** from `01_foundation.description` and per-link visual XYZ/RPY; no guessed missing angle, no FK from unverified encoder.
3. An uploaded visual manifest must link each asset to a known source-model link, pass exact path/digest/license/size checks, and be explicitly **accepted for preview only**; unknown/unsafe asset -> reject or no-asset fallback.
4. A model is not silently attached to preexisting `paky-01`; no Life enrollment/identity mutation through name similarity.
5. Any pilot import with POST uses a **separate isolated API/workspace**. Existing localhost 8099 canary rejects write methods and proxies GET/HEAD to the production API by design.
6. Add hostile fixtures: altered parent digest, reordered/missing revision history, stale calibration, duplicate slot IDs, future-event-time claims, visual-only revision accidentally marked physical, and robot-ID mismatch. All must fail closed.
7. No normative changes to 05_evolution, canonical kernel selection, RGD source hash, or production Console before explicit decision and cross-project conformance.

**Review questions:** Must companion as-built snapshots be packaged inside a .rgd ZIP or distributed as independently authenticated instance records? Who owns as-built revision issuance and physical maintenance confirmation? Where do we bind authenticated Forge receipts and qualified Chronograf/History anchors? Until answered, remain candidate with no authority.

Related drafts: `contracts/visual/v0.1.0/README.md` (this branch), `contracts/identity/v0.1.0/README.md` (Core-C branch), `contracts/temporal-memory/v0.1.0/README.md` (Core-D branch), and Console issue #14.
