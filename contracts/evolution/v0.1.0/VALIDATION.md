# EVOL-0.1 — Conformance gates (candidate only)

All checks are **offline**, hermetic, synthetic, non-actuating and must keep `normative:false` and `maturity:candidate`. For the shape validator install Python 3.10/3.12 and `jsonschema>=4.22,<5`.

## Validity matrix

| Claim | Expected | Checker |
| --- | --- | --- |
| Schema-valid `HardwareMutationEvent` / `AsBuiltRevision`, with locally recomputed record digest | ACCEPT AS CANDIDATE SHAPE | `validate(record)` |
| Valid synthetic, single-instance, serially numbered mutation from revision N to N+1 | `CONSISTENT_UNVERIFIED` | `validate_transition` |
| Requested/declared plasticity policy, human review pending | Always remains **non-authorized** | Schema `const:false`, conformance |
| Actual motor command, Life issuance, RIN reassignment, physical proof, calibration verified, authenticated Chronon commit | NOT PROVIDED | All status bits `false`, unknown fields forbidden |
| GLB material/LOD-only update, component claims unchanged | REJECT AS PHYSICAL MUTATION | `physical_slot` equality |
| Missing/double physical slot or serial claims | REJECT | duplicate/conflict checks |
| Wrong robot identity, enrollment ref, predecessor digest, revision number, missing evidence | REJECT | `validate_transition`, schema |
| Hardware change with previously claimed calibration not invalidated | REJECT | `STALE_CALIBRATION_NOT_INVALIDATED` |
| Unreported change to any physical component slot | REJECT | exact declared/actual delta |
| Changed appearance/source hashes without matching event context | REJECT | model/visual context matching |
| Fake positive `plasticity.external_authorization_verified:true` | REJECT | schema |
| Duplicate JSON keys, NaN/Infinity, too many nodes/bytes, bad UTF-8 | REJECT | bounded parser |
| Event-time string supplied as history proof | NOT A VERIFIED TIMESTAMP | only claimed_clock data, `history_committed:false` |
| Proposed event with no installed revision | ACCEPT AS PROPOSAL; REJECT as successful transition | schema / transition |
| Synthetic event + candidate digest, with no actual signer | NO REAL EVIDENCE / NO AUTHORIZATION | always unverified |

## Use

```bash
python contracts/evolution/v0.1.0/validate.py
python contracts/evolution/v0.1.0/conformance.py
python -O contracts/evolution/v0.1.0/conformance.py
```

The conformance test **builds and hashes its own synthetic robot fixtures**; no site-specific serial numbers or physical Paky-01 status are embedded. The candidate digest is a Python compact sorted-JSON comparison function, **not RFC 8785, not RGD source-root hashing, and not a trusted attestation**.

## Still missing before normative acceptance

- Stewards to define accepted `05_evolution` module activation and migration from original `spec/05_evolution`.
- Authenticated maintenance issuer, immutable as-built reference store and authorization workflow for real physical changes.
- Verified per-component binding to actual serial/robot/enrollment, and external calibration/safety status.
- Accepted canonical record serialization, signature and real asset manifest digest semantics.
- Verified Chronograf event and commit-time clocks, History idempotent write/commit receipt, recovery and privacy/retention.
- Console read-only materialization from trusted refs in its **isolated** importer, with audited error states and compatibility tests.
