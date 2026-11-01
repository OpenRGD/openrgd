# Core-C validation evidence and limits

2026-11-01. Candidate-only tests; no robot, enrollment, real credentials, history writer, deploy or distributed safety proof.

## Local authoring

Linux Python 3.13.5, jsonschema 4.26.0, referencing 0.37.0. Schema/shape validator passes. Conformance collects 86 cases: 85 passed locally, **one Core-B cross-schema case skipped** because the authoring container cannot resolve GitHub to download the exact pinned source. Seven additional parser regressions pass. Thus 93 distinct cases are collected, **92 locally executed and one pending upstream-schema input**. Normal and python -O runs execute the same cases and are not counted twice.

Seven fixture records, 31 shape-valid cross-record negative mutations, unknown-field/self-grant tests and lifecycle/clock/revocation/idempotency tests live in conformance.py. Parser regressions cover unhashable discriminators, non-object input, duplicate keys, nonfinite values, excessive integer digits, bounded bytes and invalid UTF-8 with stable error codes. No fabricated real identity or external attestation. Test receipts are exact-record digests in an in-memory trusted table. They are not signatures, registry results or a canonical source hash algorithm.

## CI design (results must be checked on the actual PR head)

Dedicated read-only workflow on Python 3.10/3.12 pins Core-B `55a034ceb1cdaab8bed6848fcdde85c9436bc9e0` and COG-C1 `a8ae925c9cacbce8bd7a6db01833d4159445d47a`. CI sets CORE_B_SCHEMA explicitly and verifies the file exists, so the cross-schema test runs rather than silently skipping. It runs new normal/optimized conformance and parser regressions, existing Core-B fixtures/conformance, unchanged COG-01/02/C0/C1 unit tests and real Core integration tests against this branch. Existing Core CI remains independent and unchanged.

Expected COG baseline from its PR #5: 133 unit/regression + 32 Core integration cases. Treat these as expected until actual logs from this branch confirm them. These checks prove legacy compatibility, NOT COG adoption of Core-C or the new Core-B ABI.

## What the tests do not establish

FixtureBoundary is an adversarial test harness, not a permission verifier or deployable runtime. It cannot detect identical copied credentials/IDs, implement distributed leases/consensus, authenticate channels, resolve clock skew or provide durable idempotency. The synthetic receiver checks current test-owned state every call. No effect is dispatched; its small volatile dedup set only models a rejection case.

Local schema limits do not prove authenticity. Positive continuity claims do not imply source/issuer/robot registration, physical calibration, real Chronon persistence or authorization. Unknown history/authority must remain explicit. No hidden model reasoning, private raw media or actual instance keys are included.

Record source-byte fingerprints and actual CI run/job IDs in the PR evidence comment after the checks complete. Any contract acceptance still requires governance, external authority integration and producer/consumer review.
