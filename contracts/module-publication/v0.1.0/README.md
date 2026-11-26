# EXT-01B — Module publication envelope (candidate)

**26 November 2026.** Candidate/non-normative. This is a bounded, offline review profile, not an accepted manifest format, publication transaction, signature scheme, package verifier, dependency solver, installer, host manager or loader. It builds on EXT-01A (#18). No current module must migrate to it.

## One declaration at each level

The historical `OPENRGD_EXTENSION_ARCHITECTURE_V0.1` is preserved; its extension manifests own provided/required ports (exact capability, contract version, semantic profile), permissions and effect requests, placement, timing target and lifecycle. Composition owns explicit instance bindings and startup ordering; it is not a software lock. `OPENRGD_COMMAND_PLUGIN_ABI_V0.1` owns optional CLI facade metadata, lazy reviewed/explicit enable, isolated registration root and namespace conflict rules. Loading Python is not sandboxing. Do not restore the archived loader into live Core during this PR.

The **module** is a distribution unit, not an extension. A proposed module.openrgd.json wraps one or more existing extension descriptors by relative path and **raw byte SHA-256**. It references optional command-facade descriptors and declares artifact slots with exact package name/version, format/profile labels and extension membership. It contains no duplicate capability lists, CLI target, effect requests, runtime host or lifecycle policy. Multiple slots can carry one extension; the candidate supports one CLI facade binding per extension (platform-specific/multi-wheel selection requires a future profile). A producer declares exact direct module dependencies; no version-range, provider selection or transitive resolution here. Logical provider binding and software dependency locks remain separate.

The proposed `ReleaseProposal` is a generated review request, not a release catalog record. It references the exact module manifest bytes, which bind exact descriptor bytes. It records actual hashes and byte sizes of explicitly supplied small test artifacts and the submitted source URI/commit **claim**. Artifact format, source checkout membership, publisher authority, build provenance and compatibility are unverified. No copying of metadata into another editable manifest. Published release identity and approvals/revocations belong to the official `rgd-modules` catalog, not this proposal. Registry should validate the same producer inputs and independently establish trust before an admitted release can be generated. Unknown catalogs, unsupported release schema or missing proof never become installable by default.

## Digest and version distinctions

- Old composition metadata: `OPENRGD_EXTENSION_JSON_DIGEST_V0.1`, normalized unordered fields and documented JSON encoding. Preserve existing pins unchanged. It is NOT a raw bytes, Git commit, source-root, package or artifact digest.
- New raw-byte SHA-256 references: exact manifest, descriptor and supplied artifact bytes, including whitespace. No claim of semantic canonicalization; changing bytes requires a new commitment.
- Module release keys: EXT-01A vocabulary SemVer subset. Extension versions and package-native versions remain independent and exact (e.g. legacy `0.1.13.dev0` is not a valid module release key).
- Source claim: syntactically bounded HTTPS repository/commit, not fetched or authenticated. No use of claimed URL as an input to network/file resolution.
- Candidate same-key comparison detects changed exact commitments, not actual publication immutability under concurrency. Registry trust and durable compare-and-publish are separate gates.

## Initial conformance scope

Three original historical schemas and three illustrative examples are recovered byte-exact under docs/history, not promoted to live contracts. This package uses them through a fixed in-memory schema registry, with no remote ref retrieval. It tests **shape and linkage only**: exact descriptor hash, matching extension/CLI identity and common CLI object, wheel package declaration, one binding per facade, duplicates, unsupported selectors, exact artifact set and conflict. It does not substitute for the recovered historical static composition validator, package metadata/installed-code verifier or trust authority; those are separate required checks before publication. Small supplied artifact blobs (1 MiB each, 4 MiB total) deliberately keep the lab profile bounded. Test wheel bytes are synthetic and not executable or valid wheel archives.

## Legacy v0.1 Registry / Calibration

The actual Calibration 0.2.0 source-pinned producer manifest declares capabilities and a rust-library label; the registry builds a CLI native binary and exposes inspect. It has no full extension ports/semantic profile, artifact slot, CLI entry point declaration or approved manifest mapping. Preserve it as a separately supported legacy v0.1 release. Do not invent ports, infer a CLI plugin hook, or fabricate an artifact from a source commit. The v0.1 registry's closed schema does not accept the new proposal; no conversion to a live entry. Future CAL producer migration is opt-in and must preserve existing inspect and exact source pin until reviewed.

## Handoff

Registry: EXT-01B proposal-only conformance; keep REG-INDEX-01 and existing index/installer unchanged. Before actual release publication, verify source checkout and exact metadata bytes, producer namespace/delegation, artifact contents and format, build provenance, independent release review, stable snapshot and rollback/revocation. Core: recover/port historical full validator/CLI loader as separate reviewed candidates; approve mapping of legacy mixed implementation.kind to packaging/entry points, scoped effects and concrete contract profiles. Console/OS: read a future approved catalog/lock only, no changes now. No grant or automatic activation.
