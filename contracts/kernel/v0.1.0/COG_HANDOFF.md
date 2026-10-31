# CORE -> COG: PR-CORE-B candidate integration handoff

**2026-10-31 / candidate / non-normative / non-actuating.**

Keep COG PR #1 and stacked #3 unchanged. Core baseline stays
`afe1a831b950a4e6560f0285a0103fc4eaa343b7`; do not re-pin source-root or mutate
InputEvent/CognitiveProposal/RGDContextSlice merely to adopt this draft.

## New opt-in boundary

Use `schemas/kernel-goal-effect.schema.json#/$defs/<TYPE>` for:
KernelDescriptor, KernelEvent, CognitiveGoalCandidate, GoalAdmissionDecision,
AgendaTransition, EffectRequest, EffectGateDecision. `STATUS.json` explicitly
refuses normative acceptance. Import no Core runtime; the validator is offline
tooling and the fixture consumer is test code, not a production policy engine.

A COG-C0 consumer can be a NEW namespace/adapter with SESSION_SCOPED context,
null Life binding/activation and restrictive INTERNAL_READ_ONLY policy. It must
resolve policy from the trusted operator/authority, never from model payloads.

1. A model/Life/Relation/Imagination may propose a goal, not admit it.
2. One deterministic admission function validates current context, TTL,
   verified policy and resource availability. Attention only selects cues.
3. Work runs only admitted goals under Coordinator reservations. Every child
   needs a fresh admission; no inherited grants or unbounded recursion.
4. A report/proposal remains inert. History commits, voice, digital tools and
   physical actions use distinct external gates. A valid schema is no grant.
5. Check session, runtime, context/policy revision and fence again when accepting
   remote model results or committing an effect. Reject old RTX responses.
6. Retain bounded, scoped idempotency through accepted TTL; collisions are errors.

## Compatibility gates

Do not feed the new goal records to the old two-kind InputEvent API. Add explicit
translation only where semantically faithful; never fabricate ActionIntent,
Life identity, Chronon ID, temporal anchor or persistence. Context shape here is
not COG-02's existing schema. `advisory` event payloads require negotiated typed
schemas; reject unknown kinds rather than dispatching arbitrary tools.

Real Life continuity/enrollment, durable/exclusive role leases, authenticated
gate receipts, memory writer and oneiric commit integration remain PR-C/PR-D.
The Life *kernel role* does not issue `life_id`. This branch does not change any
COG file. Pin a reviewed candidate commit before adopting; candidate may change
and breaking changes require an explicit adapter/version, not silent mutation.

## Producer/consumer tests to implement in COG

Use Core fixtures plus genuine COG producers/consumers in a new reviewed PR:
valid read-only goal, model self-admission rejected, stale/future/unaligned time,
context/fence mismatch, child budget exhaustion, unauthorized history/voice/
digital/physical requests, exact duplicate no-op, changed duplicate conflict,
paused/terminal lifecycle, unknown schema/version. Test owner authentication and
aggregate reservations in the real consumer, not only JSON shape validation.

Core CI additionally reruns the unchanged pinned COG-02's existing 70 unit tests
and 18 producer/consumer integration tests against this branch. That verifies
legacy compatibility; it does NOT prove COG implements the new Kernel ABI.

## Remaining review blockers

The historical eight kernel/registry/coordinator/AION blobs still need exact
source inventory and comparison before ABI stabilization. No global ownership,
safety certification, actual robot deployment or runtime availability is implied.
