# PR-CORE-C — Life / Agent / Runtime / Binding ABI v0.1 candidate

**2026-11-01. NON-NORMATIVE. No identity, permission or runtime is created by this package.** Follows CORE-COG-0001, review #10, Core-B #11 and P0 reconciliation #12. This independent PR does not modify those branches, COG, Agent contracts or canonical source.

`OPENRGD_LIFE_AGENT_RUNTIME_BINDING_ABI_V0.1` is a typed JSON record contract, not a Rust binary ABI, issuer implementation, registry, key store, lease manager or lifecycle daemon. Schemas describe claims. The verifier's authenticated conclusions are separate from the submitted record.

## Seven strict record types

All have candidate schema_version, record_type, record_id, issuer_ref, proof_refs and grants_authority=false. Unknown fields fail shape validation; credentials/private keys are never embedded.

| Record | Distinction |
|---|---|
| LifeIdentity | Durable experiential life_id. LOCAL_PROVISIONAL and ATTESTED_CLAIM are declarations, not proof of registration. Creation requires explicit enrollment/fork, never implicit reboot. |
| AgentDescriptor | Software agent and role, possibly unbound. Life kernel is not the Life issuer. Requested capabilities do not become grants. |
| RobotLifeBinding | Links Life, physical robot enrollment reference and exact RGD source_root; optional forge/artifact references remain independent dimensions. |
| LifeActivation | Binding activation epoch. Reboot need not increment it; replacing/activating a binding follows the external authority policy. |
| RuntimeInstance | Runtime, boot and session separate from Life; source/model/policy revisions; INITIALIZE/REBOOT/RESTORE/MIGRATION/FORK are not aliases. |
| RoleLease | Requested/claimed exclusive role owner with scope, authority clock domain, validity and fencing generation. PRIMARY_COORDINATOR and HISTORY_WRITER are the initial candidate exclusive roles, not all agents. |
| ContinuityStatus | UNBOUND/UNKNOWN/STALE/CONFLICT/RECOVERY_REQUIRED or CONTINUITY_CLAIMED; a submitted positive claim never authenticates itself. Physical execution remains false. |

Each record_id/proof must bind the exact versioned record contents, not an unversioned mutable alias. A consumer must resolve life_binding_ref against the exact authorized binding revision and include that revision in its context commitment; merely resolving the current value of a name is insufficient. This package does not freeze credential formats, canonical signature encoding or a public registry protocol. In the synthetic tests the trusted fixture table commits exact JSON record contents; that is NOT a production signing scheme.

## Ownership and authority

Core owns shared definitions and conformance requirements. External Identity/Life authority owns issuance/custody/revocation. RGD-EXT owns local forge and official publication receipts. Chronograf owns qualified time. History owns durable commit and watermark. Effect gates own separate privileged permissions. Nothing in Core-C appoints a process to one of these roles.

Source integrity != publisher identity != artifact registration != physical enrollment != Life binding != current role ownership != permission to perform an effect. In particular a valid RoleLease and continuity record do not authorize a history write, speech, a digital mutation or movement.

## Receiver obligations (candidate semantics)

Before accepting a privileged operation, the receiver must authenticate the caller/session and exact records/receipts; validate current custody, enrollment, binding, activation and source/context; resolve revocations; verify that the current exclusive owner/generation for the Life/role/resource matches; compare deadline only in an authenticated compatible clock domain; and check the separate effect grant for the exact operation/target. A stale preverified snapshot is not sufficient. Unknown authority, inconsistent evidence or expired/stale ownership means reject/defer, never synthesize identity/history.

A sequence counter supplied by a producer is not proof of authority. C0 task generation is callback invalidation, not role_fencing_generation. One primary owner per exclusive role is the initial profile; this does not decide universal Life multi-body semantics. Counter ranges are bounded to match Core-B's candidate types; exhaustion must fail closed, not wrap or silently widen without negotiation.

## Reboot, restore, migration and fork

- Reboot may preserve life_id and activation epoch while allocating a new runtime/boot/session and fencing old role owners. Missing custody/record -> RECOVERY_REQUIRED, not auto-enrollment.
- RGD or model revision may change without creating a new Life, after explicitly revalidated binding/context evidence.
- Restore is not trust rollback. A derived checkpoint must match the authoritative Life/history watermark and current policies/revocations; it cannot revive old grants or writer ownership.
- Migration/fork require their own procedure and approval. A backup copy is not proof of the original Life. Fork requires distinct lineage and cannot reference itself as predecessor.
- Schema-valid SESSION_SCOPED records keep Life binding fields null. They do not enter a positive Life-bound privileged path.

A real deployment must prevent two processes with copied IDs/credentials from impersonating the same session using custody, authenticated channels and external fencing. These schemas and the fake sink do **not** solve identical-clone attacks, distributed consensus or network partitions. The test's offline flag only exercises fail-closed policy when authority availability is explicitly false.

## Relationship to Core-B and cognition

Core-B Context already separates session/runtime, optional Life binding and activation, and role fence. A test constructs a LIFE_BOUND context from known synthetic fixture records and validates its SHAPE against the exact Core-B JSON schema. That does not implement a live identity resolver.

COG #1/#3/#4/#5 keep their current null robot/Life identity and their source-integrity-only context. No positive Core-C record may be inserted into COG-02 v0.2 unchanged: it rejects positive identities by design. A future opt-in versioned resolver/adapter needs actual authority integration and explicit review. Preserve the existing CognitionProposal and CognitiveProposal distinction; no ActionIntent is created here.

## Minimal use

Install test dependencies matching the pinned COG CI, then:

```sh
python contracts/identity/v0.1.0/validate.py
python contracts/identity/v0.1.0/validate.py candidate-record.json
python contracts/identity/v0.1.0/conformance.py
```

Validator reads local JSON/schema only; it never resolves proof URIs or connects to registries/hardware. SHAPE_VALID reports identity_verified=false and authorization_verified=false. Fixture generation and the fake authority are confined to conformance.py, not shipped as a production identity service. Bounded JSON loading rejects duplicate keys, nonfinite numbers and excessive size/depth.

## Remaining gates

Trust roots and proof formats; credential custody/recovery; exact immutable binding-revision resolution; actual lease expiry/clock uncertainty; network partition and identical-clone resistance; durable idempotency/ledger receipts; privacy/retention; real COG/History/Identity producer-consumer reference flow. All require owners and tests before acceptance. Merge preserves candidate status; no release or deployment is implied.
