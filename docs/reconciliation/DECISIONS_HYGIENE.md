# Reconciliation Decision Register — Hygiene Supplement

This supplement continues the primary `DECISIONS.md` register after R-049.

R-046 records the evidence state before the later backup upload. R-050 and later decisions refine the current state without pretending that the mismatched backup is the historical archive identified by the original checksum.

## R-050 — Expected AION archive and recovered backup retain separate identities

**Status:** ADOPTED ON BRANCH  
**Decision:** Preserve the historical expected ZIP SHA-256 and the uploaded backup SHA-256 as two distinct identities. The recovered backup is classified as a later same-lineage variant; byte identity with the expected archive and an “only `.env` changed” claim are not proven.

## R-051 — Secret-bearing backup material is excluded from evidence imports

**Status:** IMPLEMENTED / SECURITY REQUIRED  
**Decision:** The `.env` credential is not copied, fingerprinted or quoted in repository evidence. The secret is treated as exposed and requires revocation. Current GitHub evidence contains no tracked `.env`, but this limited finding is not represented as proof of universal non-exposure.

## R-052 — AION recovery enters through a separate evidence-delta pull request

**Status:** ADOPTED ON BRANCH  
**Decision:** The uploaded backup is not a source for reconciliation PR #1 and does not block its merge. After PR #1 merges, sanitize the backup, preserve a source-only inventory commitment, compare every source file against merged `main`, harden the AION codec/validator/claims and open a separate pull request.

## R-053 — Active-surface cleanup is evidence-based, not authorship-based

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Remove stale promotional, onboarding, Docker, maintenance, plugin and branding-proposal surfaces from current authority because their claims are unsupported, their code is unreachable/permissive or they lack tests. Do not require or assert a human/AI authorship classification to justify removal. Preserve original blob/tree identities under `docs/history/stale-prototypes/`.

## R-054 — External plugin loading remains disabled pending an accepted ABI

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Remove the dormant plugin manager, permissive policy, entry-point loader and bundled Time Travel prototype from the canonical toolchain. A future plugin system requires a versioned accepted ABI, fail-closed trust policy, isolation rules, provenance and conformance tests.

## R-055 — Known draft assertions are registered rather than silently rewritten

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Preserve unverified institutional, contact, model, dataset, citation, future-snapshot and placeholder-hash literals in the historical draft source, but register exact expected occurrences. They do not block PR #1, but they block a stable standard release until independently verified, replaced or removed through a normative content audit.

## R-056 — Secret and repository hygiene is a required CI invariant

**Status:** IMPLEMENTED ON BRANCH  
**Decision:** Fail CI on tracked secret filenames, common credential/private-key patterns, non-placeholder secret assignments, generated debris, machine-local paths outside approved evidence scopes, reintroduced stale surfaces and unregistered draft assertions. Keep the assignment parser line-bounded and regression-tested.

## R-057 — Recovered AION maturity is experimental codec/validator

**Status:** EVIDENCE CLASSIFICATION  
**Decision:** Classify the recovered AION Python implementation as an executable experimental codec and limited validator, not a production microkernel/runtime. Passing roundtrips and six snapshot tests support the narrow implementation claim; they do not support zero-copy, real-time, process-isolation, scheduling, Chronograf, middleware or physical-execution claims.

## R-058 — AION hardening findings must be resolved or explicitly deferred

**Status:** REQUIRED FOR FUTURE AION DELTA  
**Decision:** A future AION evidence-delta PR must address the findings registered as AION-H-001 through AION-H-010, including non-finite/range validation, integer-type coercion, required core dimensions, fail-closed threshold configuration, semantic-first authority, exact CLI claims, runtime-evidence separation, somatic-boundary compatibility, anchor semantics and header/type consistency.
