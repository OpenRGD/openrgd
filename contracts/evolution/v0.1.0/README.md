# EVOL-0.1 — HardwareMutationEvent & AsBuiltRevision (CANDIDATE)

**2026-11-17 · NON-NORMATIVE · NON-ACTUATING · NO LIFE/HISTORY AUTHORITY.**

This package defines a source-linked *description of claimed physical evolution* for a robot. It does **not** install parts, read physical sensors, create RIN/Life/robot enrollment, change safety policy, approve self-modification or commit Chronons. `STATUS.json` must remain `candidate`. Source-tree integrity, signed identity, safety readiness, verified time and actual installed components are separate questions.

## Source-derived problem (actual files reviewed)

The legacy reference already includes:
- `spec/05_evolution/hardware_mutation.jsonc`: component replacement/integration and degradation policies; illustrative 75% core-component replacement threshold.
- `spec/05_evolution/plasticity.jsonc`: allowed self-modification and limits on learning, configuration and policy drift.
- `spec/05_evolution/genealogy.jsonc`: origin, forks and a mutable example history list.
- `01_foundation/description.jsonc`: nominal design, link frames, mechanical/visual intent.
- `01_foundation/calibration.jsonc`: instance-specific reported/measured delta from nominal ideal; does not model physical replacement.
- `01_foundation/soft_body_dynamics.jsonc`, `soft_materials_library.jsonc`, `wear_fatigue_model.jsonc`: reference soft-body/degradation models, not live telemetry or physically installed self-healing material proof.

The `05_evolution` domain is `PROPOSAL` and optional in `spec/manifest.jsonc`; its files are **not selected** by the reference kernel's module load order. These historical example values **do not** grant permissions, determine a legal new RIN, or prove Life discontinuity.

## Two records, different purposes

| Record | Question answered | Immutable linking | Authority |
|---|---|---|---|
| **HardwareMutationEvent** | "What physical component change is proposed or operator-reported?" | References exact before/after AsBuiltRevision IDs and content digests, per-slot before/after claims, source/visual revision, affected joints/sensors and calibration invalidation | **Claim only**, NEVER an execution/installation permit |
| **AsBuiltRevision** | "What is the currently declared installed component graph at a specific revision?" | Exact predecessor ID/digest, revision number, stable physical instance reference, design source-root digest, optional visual manifest digest, component slot snapshot and triggering mutation ID | **Source projection only**, never proof of measured hardware or approved calibration |

Both require `schema_version=openrgd.evolution.v0.1-candidate`, `grants_authority=false`, `physical_execution_authorized=false`, `life_identity_issued=false`, `history_committed=false`, `calibration_verified=false`. Unrecognized fields are rejected. `actor_claim_ref`, `physical_enrollment_ref`, `history_commit_receipt_ref`, `claimed_event_time` and `evidence_refs` remain **unverified claims**, even when populated.

**No `life_id`, RIN or self-issued DID field is allowed**. External Identity/Life/physical enrollment trust is not established by model topology, visual identity, matching `robot_instance_ref` strings, a serial number or a SHA.

## Proposed state transitions (claims only, not runtime)

```text
PROPOSED mutation (no after revision; cannot claim installation)
            |
       external real-world work
            |      [NOT implemented by this package]
            v
INSTALLED_REPORTED_UNVERIFIED mutation
            |
            | exact pre/post slot delta + content digest chain,
            | invalidated calibration claims + required safety review
            v
AsBuiltRevision(N+1, calibration_status=REVIEW_REQUIRED)
            |
            +--> separately governed maintenance / calibration / safety authority
            +--> externally authenticated Life/robot binding revalidation
            +--> canonical History writer / qualified Chronograf timestamp
```

Proposals do not claim `after_revision_ref` or `after_revision_digest`. A reported installation must identify at least one evidence reference and claimed actor. A `SlotChange` describes exact before/after physical slot metadata. New slots use `before:null`; removed slots persist as `state:REMOVED_REPORTED` rather than disappearing from history. If only a GLB/LOD/color changes without a physical slot delta, **there is no HardwareMutationEvent or new AsBuiltRevision**.

The `validate_transition(before,event,after)` offline checker requires:
- identical stable robot/claimed-enrollment context across the three records;
- exact before/after revision IDs AND payload digests, and `revision_number+1`;
- exact source root/visual pointers for the records and event;
- exactly matching declared vs actual **physical** slot changes (no hidden slot changes or evidence-only events);
- explicit impact refs for changed joints/links/sensors;
- `calibration_status=REVIEW_REQUIRED`, no carried-forward calibrated position or derived readiness; any old calibration claim listed among invalidations;
- no automatic Life, RIN, History or physical execution authority.

If the as-built change cannot be tied to a valid predecessor, a missing source revision, incompatible frame, stale calibration or conflicting physical identity, **do not reinterpret it as an accepted installation**. Real authority validation is outside this package. A mixed design+hardware update may change `design_source_root`; independent review of topology and mappings is mandatory.

## Plasticity as policy governance, not mutation executor

`HardwareMutationEvent.plasticity_governance` references both canonical policy paths:
`05_evolution/plasticity.jsonc` and `05_evolution/hardware_mutation.jsonc`.
`human_review_required=true`, `external_authorization_verified=false` are mandatory. The loader does **not** read those files and does not interpret old numeric gain, percentage or time-of-maintenance examples as current authority.

Do not confuse:
1. **Behavioral/neural plasticity**: updates to Agency skills/policies with separate governance. No physical mutation event.
2. **Transient elastic deformation**: modeled under Foundation soft-body physics; does not necessarily produce a permanent as-built revision.
3. **Persistent morphological change**: a repair, moved IMU, replaced actuator or head-shell installation; new reported as-built revision and affected calibration/safety claims invalidated.
4. **Appearance-only digital change**: independent `visual_manifest_sha256` / content-addressed GLBs; no physical mutation, as-built revision or Life change.

## Five independently versioned identities

```text
RGD source_root (design) ---┐
visual manifest SHA-256 ----┤
physical instance ID -------+--> candidate AsBuiltRevision (reported)
calibration revision claim -┘          |
                                        +--> external safety/commissioning
Life Identity & binding --> separate, independently verified by Core-C authority
Chronograf/History ------> separate authenticated writer, not this JSON
```

New CAD textures, LODs and geometry blobs cannot re-enroll a robot. A physically replaced component can trigger as-built and model changes, but only an externally reviewed/verified binding may continue the same Life in that new configuration. **No fixed percentage (including legacy 75%) automatically changes RIN or Life.**

## Portable RGD ZIP packaging (proposal, not current Console functionality)

```text
robot-snapshot.rgd                      # currently ZIP alias, not new normative format
  spec/...                              # immutable versioned canonical source
  assets/visual/manifest.json           # VIS candidate, independent digest
  evolution/as-built/r0001.json          # AsBuiltRevision *unverified projection*
  evolution/events/mutation-001.json     # HardwareMutationEvent *unverified projection*
  evolution/revision-index.json          # candidate read-only index of immutable refs
```

The package MUST NOT rewrite a previous canonical source-root or historic record: a new export selects newer immutable revisions while previous refs survive separately. `genealogy.jsonc` may later present an index of externally committed event refs, not the canonical history itself. The exact ZIP index syntax, manifest anchoring under canonical `spec/`, binary-signature format and persistent storage API remain open governance questions.

**Console integration is not performed here.** An opt-in future importer may display `as_built_revision_ref` + `visual_manifest_sha256` as *claimed, versioned metadata*, while keeping the current robot/source snapshot unaltered. The existing Console 8099 canary proxies GET to production and rejects POST: mutation imports require an isolated API/workspace before testing, and no motor/IMU publisher changes.

## Local digest consistency — candidate ONLY

`validate.py` calculates `record_digest` using sorted UTF-8 compact JSON over the record **excluding the `record_digest` field**, prepended with the fixed `OPENRGD-EVOL-0.1-CANDIDATE-SORTED-JSON\0` domain. It detects local field tampering and chained reference mismatches **only within this candidate Python implementation**.

This is **NOT** RFC 8785/JCS cross-language canonicalization, an RGD source-tree hash, a trusted signature, an authenticated receipt, a recognized Chronon commit, or a legal proof of a component installation. The eventual accepted digest profile and external attestation protocol MUST be reviewed and versioned separately.

## Validation and code

```bash
python -m pip install 'jsonschema>=4.22,<5'
python contracts/evolution/v0.1.0/validate.py
python contracts/evolution/v0.1.0/conformance.py
python -O contracts/evolution/v0.1.0/conformance.py
```

`SHAPE_AND_DIGEST_VALID_CANDIDATE` and `CONSISTENT_UNVERIFIED` only mean a parseable local claim chain. Synthetic tests cover physical slot addition/replacement, tampering, duplicate slots/record IDs, fake identity/authority, invalid plasticity grant, missing calibration invalidation, visual-only update misclassified as physical, reversed lineage, and untrusted time/History refs.

## Ownership / explicit promotion blockers

- **OpenRGD standard** owns eventual governance of Evolution semantics and canonical profile compatibility.
- **External Maintenance/physical-instance issuer** must attest actual installed component IDs, evidence, who did the work and approvals.
- **RGD-Calibration/Somatic Safety** own actual calibration and motion authority.
- **External Core-C Identity/Life** owns custody, enrollment, binding/revocation and Life continuity (PR #13 candidate).
- **Chronograf + RGD-Physics/History** own qualified time, immutable Chronons, idempotent commit receipts and genealogy authority (PR #14 candidate).
- **Console** owns optional visualization of *claims* and source model/asset revision metadata, never physical or historical truth.

See [EVOL-0.1 issue #15](https://github.com/OpenRGD/openrgd/issues/15), [VIS PR #7](https://github.com/OpenRGD/openrgd/pull/7), [Console VIS issue #14](https://github.com/OpenRGD/rgd-console/issues/14), and [Console VIS-0.1A PR #15](https://github.com/OpenRGD/rgd-console/pull/15).

**Remaining gates:** test with actual reference BHL source mesh evolution, decide exact as-built authority binding vs canonical RGD source profile, design authenticated mutation receipts and rollback, expose only read-only projections in Console, then obtain explicit steward approval before any normative change to `spec/05_evolution`, mirrors, kernel or source-root hash.
