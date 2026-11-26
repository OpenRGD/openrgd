# EXT-01B — historical-to-current crosswalk

**Candidate, no normative promotion.** References: Core #18, original archive inventory, actual registry #3 at 8c50645b6fbc73d73a87a278bf2009fa83f3705d, Calibration producer 81700401e2fa6d370a86b6c1f5a48802bc5f1fc7, Console a0ef857cf425c1bb14ad8f62acec21f8c1324866. This is review, not a schema migration of installed software.

| Historical/legacy surface | Source of truth and mapping | Decision / gate |
|---|---|---|
| extension_id / extension_version | extension descriptor, not module release ID | Preserve exact; do not infer a release key from package versions. |
| extension_kind | namespaced implementation family | Do not replace with the 19 descriptive role facets. |
| provides/requires.port, capability, contract.id/version, semantic_profile, optional, phase | existing Extension Architecture schema | Keep intact; no guessed capabilities or contracts, no implicit fallback. |
| implementation.name/version/kind/evidence_status | legacy declaration | Initial bounded direct artifact mapping only; service is not a format, firmware separate. Evidence status is claim. |
| permissions_requested, authority.requested_effects | legacy declaration | Preserve requested scope; no mapping to approved Core-B gate or Core-C lease. |
| execution.host/isolation/realtime; lifecycle.replacement/on_failure | external deployment/implementation requirements | Never derive from artifact kind or start automatically. A hard-real-time target is not achieved latency. |
| cli (entry point group/name/target, namespace, registration contract, registration_only) | existing extension/CLI projection | New descriptor generated from source declaration; existing descriptors matched exactly on common cli fields, preserve package name/version, description may differ. No import/attach. |
| CLI distribution.name/version | exact package identity | Not module version or module ID; no implicit normalization. Installed wheel metadata and local review/enable remain separate. |
| composition.manifests/instances/bindings and normalized manifest_digest | static design review | Preserve old digest profile and exact bindings; not package lock, install order or authority. |
| Registry v0.1 id/version/display_name/publisher/category/summary | reviewed legacy release descriptor | No retroactive rename; module_id/module_version and functional_roles proposed for new wrapper. Publisher trust is external. |
| Registry v0.1 capabilities | matches subset of producer capability declarations | No fabricated typed ports for Calibration. Future projection uses original port metadata, not a hand-maintained list. |
| Registry v0.1 safety/permissions_required | existing narrow non-actuating profile | Preserve zero device permissions, no motion on load. No relaxed allowlist. |
| Registry v0.1 source.git_url/commit_sha/module_manifest | existing reviewed source pin | New proposal records source claim separately and does not fetch it. No Git commit as substitute for artifact hash. |
| Registry v0.1 distribution.kind/hosts/package/binary and integration.interface/read_only_command | pinned_git_cargo / inspect | Remains supported independently; new slot and raw commitments do not imply installed binaries. |
| registry/index.json | generated projection of reviewed v0.1 descriptors (#3 candidate) | New ReleaseProposal is NOT a descriptor, may not be added by the generator. Future versioned catalog and publication records must be reviewed. |
| Module Agent / Console | installed state and supported install policy, local snapshot pinned | No new frontend/backend route; no upgrade or repin. OS consumes same future manager API. |

## Proposed review flow

Producer writes one wrapper plus typed extension declarations; CLI facade is generated for new producers when applicable. Recompute exact descriptor/manifest/artifact commitments; retain a deterministic review proposal. Registry independently repeats verification and checks existing release identity under current trusted snapshot. Do not overwrite a legacy key whose content cannot be compared under the new protocol. Actual source/build/artifact verification, publisher delegation, signed snapshot, review/admission and durable race-safe publication are still required. Unknown dependencies or missing semantic validation never become verified. Cross-repo source pins and no privilege are conformance evidence only, not readiness.

## Required next work

1. Restore full historical validators/loader selectively and test actual CLI consumers (not a ZIP overlay).
2. Reconcile old capability port IDs and semantic profiles with concrete producer contracts, e.g. Calibration inspect. No auto-port generation from legacy strings.
3. Design approved registry release/catalog version, trust and withdrawal/revocation; run an actual artifact verification pipeline (wheel metadata/RECORD, native build provenance, etc.).
4. Validate a real second module with registry and manager in independent clients. No installation until supported profile and explicit policy.
