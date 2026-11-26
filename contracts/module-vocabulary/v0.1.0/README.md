# OpenRGD Module Vocabulary — v0.1 candidate

**EXT-01A · 2026-11-26 · NON-NORMATIVE · no installer, new release manifest, catalog, runtime, permission or accepted ABI.**
This vocabulary is a *fragment library*, not a new registry format. See the [authority decision](../../../docs/ecosystem/EXT_01A_MODULE_GOVERNANCE.md) and [publication/OS boundary](../../../docs/ecosystem/MODULE_DISTRIBUTION_AND_OS.md). The schema's $defs are the machine-readable source for the proposed terms. No copies of enum values are maintained in clients. Existing consumers are pinned and remain unchanged.

## Terms and independent dimensions

| Term / dimension | Meaning |
|---|---|
| Module | Named logical unit of distribution managed under a publisher namespace; can contain one or several extension implementations. Not necessarily a repository, native package or process. |
| Module release | Immutable reviewed version of module contents with exact manifest and artifact identities. Key: module_id + module_version; publication decisions are separately authenticated. |
| Artifact | Concrete content addressed material, with media/format, digest, byte length and platform as applicable. A source tree, binary, library, wheel, image, model, data bundle or firmware is not an instance. |
| Extension | Named, versioned contribution exposing/requiring ports. Existing Extension Architecture v0.1 local candidate remains the source of its concept; do not mint a second manifest. |
| Instance | A configured occurrence of an implementation in an explicit host/composition; multiple instances may share a release. Not a Life/robot ID. |
| Capability | Declared function; contract and semantic profile determine matching. No security right. |
| Port | Explicit offered/required connection point associated with a capability, exact interface contract/version and semantic profile. |
| Interface contract | Versioned protocol/ABI/API describing observable behavior and failure semantics. No universal ABI or transport. |
| Functional role | Discovery/classification facet; multi-valued, not dispatch authority or a closed list of vendors. |
| Execution form / activation mode | How code is represented/invoked, independently of artifact packaging, deployment, isolation and measured timing. |
| Composition | Design-time instance/port bindings; not a deployment lock or authority graph. |
| Deployment lock | Resolved exact artifact versions, host profile, bindings and relevant policy revisions; not implemented here. |
| Publication / channel | Registry-owned availability and selection policy. Contract maturity remains a separate governance axis. |
| Host states | Installation, integrity, compatibility, activation, execution and health are separate observations; no flattened universal state or module-wide ALLOW. |

## Classification and identifier profile

Use `schemas/module-vocabulary.schema.json` selectors `#/$defs/ModuleReleaseKey`, `#/$defs/ModuleClassification`, `#/$defs/ExecutionClassification`, and the named vocabulary fragments. These are **candidate shapes only**. Unknown fields and unnegotiated role labels fail validation; clients may report unsupported, but may not reinterpret them or activate a module. Roles are descriptive; extension_kind stays namespaced/extensible in its own contract. ExecutionClassification is per entry point, not per whole module. For a module with library and CLI, classify each exposed entry point separately. An OCI image does not by itself imply supervised_service; a native_binary can be on_demand or supervised_service. Device firmware must not flow through a generic service loader. A valid combination grants no permission or evidence of isolation.

New module IDs use a bounded lowercase ASCII dotted reverse-domain-style namespace (minimum two publisher labels + one local label; ASCII alphabetic label starts, hyphen inside labels only; total maximum 200). A registered namespace/delegation, not the spelling of the ID, proves who may publish it. Reserve `org.openrgd.*` for the project's reviewed namespace, do not claim ownership of arbitrary external IDs. Retain legacy IDs and aliases; no silent normalization, rename, or case folding. Capability IDs, contract IDs, extension IDs, package names, entry-point names and CLI namespaces are separate; existing identifiers such as `calibration.profile.validate` and `rgd.commands` remain as-is until explicit owner-reviewed mappings. New common capability/contract naming requires an allocation procedure, not just prefix concatenation.

ReleaseVersion uses a strict SemVer 2.0.0 subset (including prereleases; excluding build metadata from the registry release key as a proposed profile restriction). Exact package versions (PEP 440, Cargo, etc.) and immutable artifact digests are separately recorded. Do not silently translate `0.1.0a5` to a release ID, sort versions lexically, resolve floating latest or republish the same key with altered content. This does not replace legacy v0.1 validation or implement range resolution. Full signature, version negotiation and publication protocol remain EXT-01B.

## Baseline migration, not a new runtime

`org.openrgd.calibration@0.2.0` is already in the v0.1 Registry. Its pinned producer manifest describes `runtime=rust-library`, while the distribution and consumer expose a compiled native binary and command-line JSON inspect. The library source/API is not evidence of a separately loadable native_library artifact. Proposed discovery facet: calibration; CLI profile: native_binary/on_demand. Do not rewrite the producer manifest or add classification fields to its closed registry schema. The current legacy `ready` state describes the checked installed binary, not a running service, current calibration or authorization. No current lifecycle authority changes.

The historical local extension manifest's implementation.kind is a mixed compatibility vocabulary (python_package, native_library, native_binary, service, model, data, device_firmware). Preserve it unchanged; a future version splits packaging and execution only with source-specific mapping and migration tests. Service does not determine artifact kind. Prior authority.requested_effects are legacy declarations; do not cast them into Core-B effect decisions. The four distinct graphs (software dependency lock, port composition, startup order, runtime data flow; independent authority requirements) must not be collapsed into a single DAG. No automatic provider selection, fallback or permission inheritance. The existing CLI plugin review's metadata-only discovery and explicit local enable remain separate from installation, launch and effect authorization.

## Verification

Run `python contracts/module-vocabulary/v0.1.0/conformance.py` with jsonschema installed and the exact Registry and Calibration checkouts supplied by CI. The tests validate vocabulary semantics, positive and negative examples, unchanged v0.1 manifest/descriptor consistency and actual registry.catalog discovery. No download/build/activation by the test harness; ordinary CI may build the unchanged Core toolchain. Test success is not publication, owner trust, install approval or host health.
