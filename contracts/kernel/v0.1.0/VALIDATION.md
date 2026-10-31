# Validation evidence and limitations — PR-CORE-B

**2026-10-31 / candidate / no normative promotion.**

## Local checks actually executed

Linux, Python 3.13.5, jsonschema 4.26.0, referencing 0.37.0.
- Draft 2020-12 schema check and all seven selectors.
- 11 positive fixture records (five roles plus six other types).
- 24 negative mutation fixtures, rejected by shape validation.
- 86 distinct unittest cases PASS; also PASS under optimized Python `-O`.
- 25 individually shape-valid cross-record fault cases are included in the 86:
  stale context/runtime/session/policy/fence, unaligned/future/expired time,
  self-admission, competing owner, foreign goal/revision, scope/budget escalation,
  unverified grants, changed request/gate/receipt and stale gate decisions.
- Other tests exercise bounded queues, duplicate/conflicting replay, child limits,
  transition ordering/pause/resume/terminal behavior, duplicate JSON keys,
  non-finite values, size/depth limits, no mutation and offline validation.
- Tested paths disable socket creation and process launch while validating and
  consuming synthetic records. This is not OS sandboxing or full I/O mediation.

The test oracle is controlled by the test, independently of untrusted records.
It does NOT verify a real signature, lease, identity, registry or writer. Positive
receipts are fixture strings, not credentials. No requested effect is executed.
All data is synthetic/fixture_only; no private robot-instance or human evidence.

## Remote CI configured; inspect run results, not this document, for outcome

`.github/workflows/kernel-contracts.yml` runs Python 3.10 and 3.12:
1. Verify protected Core paths unchanged against baseline and exact COG commit.
2. Install pinned COG dependencies and this branch's unchanged Core implementation.
3. Validate fixtures and run the 86 cases normally and with `-O`.
4. Run the unchanged COG #3 pinned source's 70 unit tests and 18 actual-Core
   producer/consumer tests. These are legacy compatibility tests, NOT a new
   Kernel ABI implementation by COG.

Existing Core CI remains unchanged and separately checks source/mirror/hash,
CLI/regressions and Windows executable. No release tag is created here.
CI checkout may use GitHub's synthetic PR merge ref; inspect head/base metadata.
Repeating tests on several interpreters does not multiply distinct test counts.

## Known limitations / review gates

The authoring container could not resolve github.com, so cloning and executing
all current Core/COG code locally was unavailable. GitHub connector reads/writes
were successful. Full current-repo regression evidence must come from CI; do not
substitute the older locally attached ZIPs for the live main baseline.

Historical microkernel source-blob inventory remains unaudited. New schemas are
candidate message contracts, not demonstrated legacy ABI compatibility. No new
production GoalAdmission, Coordinator, Work loop, persisted Life identity,
Chronon memory or effect gate is implemented here. Distributed split-brain,
real proof verification, durable idempotency and aggregate resource reservations
require external implementations and adversarial integration tests.

`LIFE_BOUND` is structurally representable but not verified. The reference test
consumer handles SESSION_SCOPED lab data only. Generic advisory payloads, native
RT events and final cryptographic wire encodings remain negotiated/deferred.
No physical performance, N150 timing, safety certification or robot test claimed.
