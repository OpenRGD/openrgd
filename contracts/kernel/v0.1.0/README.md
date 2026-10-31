# PR-CORE-B — Kernel / Goal / Effect ABI v0.1

**Candidate / NON-NORMATIVE / not accepted / no runtime implementation.**
Tracking: [CORE-COG #9](https://github.com/OpenRGD/openrgd/issues/9).
Design review: [REVIEW-01 #10](https://github.com/OpenRGD/openrgd/pull/10).
Core baseline: `afe1a831b950a4e6560f0285a0103fc4eaa343b7`.

## Scope and status

`OPENRGD_KERNEL_GOAL_EFFECT_ABI_V0.1` is a **message/data contract candidate**,
not a native linking ABI, a scheduler, an event bus or a command-plugin loader.
Seven public type selectors live in `schemas/kernel-goal-effect.schema.json`.
They share `$defs` rather than repeating seven copies of the common fields.
Use `#/$defs/KernelDescriptor`, `KernelEvent`, `CognitiveGoalCandidate`,
`GoalAdmissionDecision`, `AgendaTransition`, `EffectRequest`, `EffectGateDecision`.
The bundle's root accepts exactly one of these seven shapes.

The exact historical eight microkernel/registry/coordinator/AION source blobs
remain **unavailable to this audit**. This is a new candidate extracted from
REVIEW-01 requirements, not a claim of compatibility with those implementations.
Do not freeze the ABI until their pinned inventory is reviewed.

Implemented here: strict bounded JSON schemas, offline shape validation,
fixture-only reference consumers, negative/positive tests and CI. Not implemented:
autonomous agenda, kernel host, cryptographic identity/grants/leases, distributed
fencing, history writer, effect dispatch, model integration or physical safety.
Merge does not change `STATUS.json` to accepted or modify canonical RGD.

## Ownership: five logical roles, not five mandatory processes

| Role | Responsibility | Boundary |
|---|---|---|
| Safety | Advisory safety interface and independently hosted Somatic reflex | Reflex must not wait on cognition; this JSON envelope is NOT its RT wire format |
| Life | Qualified homeostasis/resource proposals | Life *kernel role* is not the persistent Life identity authority; unknown telemetry stays unknown |
| Work | Task lifecycle for admitted goals, bounded subgoal proposals | Cannot mint grants; no second admission or resource coordinator |
| Relation | Social/communication proposals | A proposal is not permission to speak or send a message |
| Imagination | Hypotheses, counterfactual/oneiric proposals | Synthetic output is not physical observation or a verified milestone |

Mission/aspiration policy remains RGD/Volition + governance. `orchestra` ranks
soft preferences only. One logical `GoalAdmission` owner consumes external policy
and grants. One non-critical Coordinator reserves budgets/preempts cognitive
work. Attention selects cues, never approves goals. Work manages tasks only
after admission. Independent Somatic/Body gates remain the physical authority.
A descriptor declares requested capabilities/events; it never proves ownership.
A conforming host authenticates the descriptor's producer and enforces role-
specific output permissions externally. Claiming role `Safety` grants nothing.

## Contract surfaces

| Selector | Required content / meaning |
|---|---|
| KernelDescriptor | ID, role, implementation reference, ingress/egress kinds, requested capabilities/effects, finite resource bounds, failure policy, provenance; no grants |
| KernelEvent | Producer, versioned kind, correlation, scoped idempotency, context, lifetime, immutable typed payload reference/digest, provenance |
| CognitiveGoalCandidate | Immutable goal ID/revision, origin, task reference, parent/depth, requested effects, finite budget; no dummy ActionIntent |
| GoalAdmissionDecision | Authenticated external admission-owner reference, exact goal revision, ADMIT/REJECT/DEFER, reasons, eligible effect categories, evaluated grant refs and allocated budget |
| AgendaTransition | Work owner, goal/admission refs, sequence and predecessor, explicit from/to states, idempotency, context/fence |
| EffectRequest | Exactly one category, goal/admission refs, target and operation refs, requested grant refs, idempotency; no embedded executable code |
| EffectGateDecision | Independent category gate, exact request, ALLOW/DENY/DEFER, reasons, evaluated grants and verification receipt reference |

All records have `schema_version`; unsupported versions and extra fields fail
closed. Every record includes `grants_authority:false`: it is a declaration or
report of a decision, **not a bearer credential**. Even a valid `ALLOW` record
requires independent verification of the gate/receipt for the exact immutable
request, current policy, target, operation, principal, expiry and fencing.
`eligible_effects` permits a request to proceed to a gate, not execution.
`evaluated_grant_refs`/`verification_receipt_ref` are opaque references, not proofs
verified by this validator. Public-key format, trust roots, issuer revocation
and receipt encoding belong to reviewed identity/authority integration.

## Event payload resolution

Kinds are namespaced `openrgd.kernel.v0_1.*`. `goal_candidate`, `goal_admission`,
`agenda_transition`, `effect_request`, `effect_decision` resolve respectively to
the matching type above. `advisory` reserves an extension point: a consumer MUST
reject it unless its payload schema and producer authority were separately
negotiated. This package does not invent universal homeostasis/safety telemetry.
Payload refs are never fetched by the validator. The receiver verifies the
content digest with the producer's negotiated encoding profile, validates the
resolved type, context and causal binding, and then applies policy. No global
canonical encoding or new OpenRGD source hashing algorithm is introduced here.
An unknown payload digest/profile, unresolvable reference or unauthenticated
producer is not a usable event. Provenance classifications are producer claims,
not self-authentication. Never upgrade SYNTHETIC/FIXTURE evidence to OBSERVED.

Idempotency is scoped at least by producer, session and key. An exact duplicate
is a no-op. Same key/different content is a conflict, not a new operation.
Production consumers need bounded queues and a retention strategy whose window
covers accepted TTL/replay scope; cache eviction must not permit re-execution.
The test consumer rejects overflow rather than evicting or performing effects.
It does not implement durable idempotency across restart.

## Context, lifetime and future identity ABI

Context contains revision, policy revision, session/runtime IDs, scope,
`life_binding_ref`, `life_activation_epoch`, `role_fencing_generation`.
The last two are deliberately independent. In SESSION_SCOPED mode binding and
activation are null; a session-scoped owner can still have a fencing generation.
LIFE_BOUND requires references, but structural validation **does not validate
the binding**. No robot/Life identity is auto-issued. The test consumer supports
only SESSION_SCOPED fixtures; verified bindings/leases are PR-CORE-C's boundary.

A receiver checks context revision, current policy, owner and fencing before
accepting an event and again before each privileged effect. Late remote model
results after reboot/context refresh/lease change must be discarded. Local locks
alone cannot enforce exclusive ownership under network partition.

`Lifetime` uses a declared monotonic session domain, integer milliseconds and
TTL. `[created_ms, created_ms + ttl_ms)` is the valid interval; the upper boundary
is expired. Different domains or UNALIGNED quality cannot be compared directly.
An external trusted receiver must establish clock correspondence/receipt-time
validity or defer. These are NOT Chronograf anchors or historical attestation.
Integer caps and protocol size bounds are defensive candidate limits, not
performance measurements or approved operating rates.

## Admission, budgets and transitions

Goal proposals may request any of the five effect categories. The session-only
lab oracle permits INTERNAL_READ_ONLY only. Admission must be deterministic for
the same *verified* policy/context/resources; model scores are advisory.
The Core provides no admission engine. Tests check acceptance of supplied
fixture decisions against a separate test-owned policy oracle, never policy
embedded in the proposed goal.

A child has a resolvable parent, depth=parent+1, its own ID/revision and a **new**
admission decision. It inherits neither permission nor the parent's remaining
budget. Production Work/Coordinator must atomically reserve aggregate budgets,
cap siblings, steps, total wall time and queues, and reclaim once on completion.
Schema bounds and the synthetic tests are not an operational resource scheduler.

Proposed lifecycle: PROPOSED -> ADMITTED/REJECTED/CANCELLED; ADMITTED ->
RUNNING/CANCELLED; RUNNING -> PAUSED/COMPLETED/FAILED/CANCELLED; PAUSED ->
RUNNING/FAILED/CANCELLED. Terminal states do not reopen. Retry is a new candidate
and admission, not implicit extra authority. Transition sequence and predecessor
must match current state; replay is a no-op. Rejected/deferred admission has no
eligible effects or allocation. The fixture consumer exercises the admitted
path, pause/resume, terminal rejection and owner/chain conflicts, not a daemon.

## Five separate effect domains

- INTERNAL_READ_ONLY: policy-controlled in-memory/query work; not arbitrary
  network/file/tool access and not an exemption from read/privacy policy.
- HISTORY_COMMIT_REQUEST: privileged request to the single authorized history
  writer, subject to consent/retention/idempotency. Not read-only memory work.
- COMMUNICATION_REQUEST: voice/message intent; independent communication gate.
- DIGITAL_EFFECT_REQUEST: write/tool/remote operation intent; digital gate.
- PHYSICAL_ACTION_REQUEST: physical proposal; operation and independent Somatic
  safety gates. No direct adapter access or actuator opcode in this ABI.

`target_ref` and `operation_ref` refer to typed, reviewed downstream requests,
not commands to execute as strings. A physical proposal must eventually pass
existing Somatic contracts; this ABI cannot replace them. Gate selection cannot
be made by the untrusted request. No scheduler or permission fallback on denial.

## Compatibility and migration

This PR adds only `contracts/kernel/v0.1.0/` and its own CI workflow. It does not
change `spec/`, `standard/`, seeds, hashing, `src/openrgd/`, existing Agent schemas,
check/boot, version numbers, or Core draft PRs #6/#7/#8/#10.

COG #1 (`aef3cd4be6c9405d3c8069d90b031484e11d6f4b`) and #3
(`940757af306dc538d3f3e0c70fed5f0671024be9`) retain their contracts.
Do NOT insert these new records into COG-01 InputEvent: it still accepts only
USER_TEXT/OBSERVATION_NOTICE. Do NOT rename CognitiveProposal to the old Core
CognitionProposal (mandatory ActionIntent). Implement a separately versioned
COG consumer/adapter after review. Preserve COG-02's source-root pin and null
positive Life/robot identity. The schema Context here is a new boundary, not a
replacement for `cog_context_slice_v0.2-candidate`.

## Run and interpretation

```
python -m pip install jsonschema==4.26.0 referencing==0.37.0
python contracts/kernel/v0.1.0/validate.py
python contracts/kernel/v0.1.0/conformance.py
python contracts/kernel/v0.1.0/validate.py CognitiveGoalCandidate candidate.json
```

Shape validation returns `SHAPE_VALID_ONLY`, `authorization_verified:false`,
`runtime_executed:false`. It uses an explicit in-memory schema registry and no
network reference retrieval. Local input is limited to 1 MiB; records to 64 KiB,
24 levels and 4096 nodes. Duplicate keys/non-finite numbers are rejected.
These are development tools over operator-selected files, not an OS sandbox.

See `VALIDATION.md` for the tested scope and `COG_HANDOFF.md` for integration.
For JSON Schema resolution implementation see the primary library documentation:
https://python-jsonschema.readthedocs.io/en/stable/referencing/
