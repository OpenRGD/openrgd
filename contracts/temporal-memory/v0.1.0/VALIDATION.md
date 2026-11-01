# CORE-D — Verification and acceptance gates

**Candidate only.** Ten strict schemas; 12 positive synthetic fixtures and 28 negative/adversarial fixtures; additional fake Chronograf/History/Memory behavior tests. These do NOT test a real Chronograf, certified physical event, credential, distributed writer or GDPR erasure.

```sh
python contracts/temporal-memory/v0.1.0/validate.py
python contracts/temporal-memory/v0.1.0/conformance.py
python -O contracts/temporal-memory/v0.1.0/conformance.py
```

CI runs both Python 3.10 and 3.12, this candidate's tests, unchanged Core-B/Core-C tests and unchanged COG #6 regressions on exact pinned revisions. Existing Core CI (including Windows) must remain green. Count distinct tests once, not once per interpreter/optimized rerun.

**Remaining acceptance:** Chronograf/History/Memory owners approve legacy-time delta; actual time/commit proof and reader; independent effect/identity/role enforcement; cross-repo Oneiric producer/Memory consumer; privacy/retention and legal erasure; fail-closed restart, clocks, duplication and split-brain experiments; governance maturity decision. Mock PASS does not satisfy these.
