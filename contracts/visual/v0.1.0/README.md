# RFC — OpenRGD Visual Assets v0.1 (NON-NORMATIVE CANDIDATE)

**State:** design / interoperable manifest draft. Not part of the approved Standard 0.2.0; must not be represented as an accepted RGD normative update. No physical safety or motor authority changes.

## Why

A user's Paky-01 build has a real physical torso IMU live in OpenRGD Console. The existing Console `CORPO 3D` preview renders a reference skeleton from Berkeley Humanoid Lite V1 URDF 26-joint topology (22 actuated) but **does not load the actual visual meshes**.

The repository already contains an example `spec/01_foundation/description.jsonc` > `embodiment_config.assets_manifest` declaring `visual_usd_uri_str`, `collision_usd_uri_str` and `mesh_scale_vec3_float`. The referenced USD paths are **not bundled** under `assets/` today. The active `rgd import` URDF importer parses source-supported link/joint/inertial data, not `<visual>` or mesh files; Console's ZIP preview importer only reads JSONC for structural topology (8MiB compressed / 16MiB uncompressed). Consequently an `.rgd` ZIP with a link topology cannot currently produce a photorealistic body in the browser. Adding declared visual assets and a bounded delivery path solves this without overloading the canonical cognitive/physical contracts.

## Decision proposal

**An OpenRGD *source profile* remains the canonical modular `spec/` tree.** The `.rgd` filename is **not** newly standardized as a binary format by this RFC. Console currently accepts an `.rgd` suffix only when bytes are a ZIP archive of a valid source tree. This remains true.

Propose a supplemental **`assets/visual/manifest.json`** inside the ZIP profile (or in an integrity-addressed companion artifact) as a **non-actuating descriptive payload**. A future approved extension to Foundation `embodiment_config.assets_manifest` may include a relative manifest path + **SHA-256 of the entire visual manifest**, anchoring it into the `spec/` source-tree integrity root. This must be discussed/reconciled under ordinary governance before modifying spec/standard/seed mirrors or hashes.

### Logical bundle example

```text
robot-source-profile.rgd               # ZIP transport: not a new canonical RGD serialization
├── spec/
│   ├── manifest.jsonc
│   ├── 00_core/kernel.jsonc
│   └── 01_foundation/description.jsonc
└── assets/
    ├── visual/manifest.json           # candidate: link-to-mesh map + metadata
    ├── visual/link_base_low.glb        # lightweight runtime glTF binary
    ├── visual/link_left_leg_low.glb
    ├── collision/...
    └── cad/optional_original.step     # exchange/manufacture, NOT browser render
```

Each entry identifies:
- **link_id** corresponding to the source RGD topology, no guessing based on file name;
- **role** `visual_runtime`, `visual_source`, or `collision_preview`;
- relative **package-local path**, exact bytes, size, SHA-256;
- **visual origin XYZ metres, RPY radians, per-axis mesh scale** in declared model coordinates;
- **provenance, source/license attribution, optional derivation chain** (e.g. STL → optimized GLB);
- observed/declared category **UPSTREAM_MODEL_REFERENCE_UNVERIFIED** vs **AS_BUILT_OVERLAY_OPERATOR_REPORTED_UNVERIFIED**.

The model can therefore carry precise BHL vendor meshes and then a Paky-01 **as-built layer** for custom head/neck, body modifications and additional cameras. A source-model mesh is **not automatically the physical robot**. Original mesh/CAD and renderer-optimized assets are different artifacts and must not be conflated.

### Format policy

| Layer | Typical file | Purpose | Authority |
| --- | --- | --- | --- |
| URDF / OpenRGD Foundation | JSONC/URDF transforms | topology, joint origins, axes, ideal limits | source description only |
| Original CAD | STEP/STP / Onshape export | design/manufacturing/editability | vendor or operator source |
| Source visual | STL / USD | link geometric appearance and provenance | not calibrated physical pose |
| Runtime visual | **glTF 2.0 GLB** | fast browser rendering, materials/LOD | non-authoritative visualization |
| Collision | convex/primitive/USD dedicated | approximate physical interactions | **never** implied safe by a visual mesh |
| As-built overlay | newer mesh + evidence | Paky-01 modifications | operator reported until measured and reviewed |

GLB is recommended for Console/browser distribution; the canonical RGD body does **not** need to embed raw STEP bytes into JSONC. A profile can package multiple variants/LODs by distinct asset IDs. Hiding unverified/missing assets is preferred to filling them with guessed geometry.

### Security and compatibility requirements for a Console consumer

1. Existing ZIP structural importer **remains fail-closed**. Mesh import requires a separate reviewed allocation budget (current 8MiB upload cap is insufficient for 26 raw BHL STL files); no unbounded increase or ZIP decompression to host paths.
2. Only fixed, package-relative paths allowed; reject absolute paths, dot segments, symlinks, duplicate entries, path aliases, oversized files, count/aggregate expansion, unsupported file magic, external reference URLs and GLB external resources/scripts.
3. Verify SHA-256 of each blob **before serving**; bind manifest digest to source profile when the spec extension is approved. Avoid trusting a filename extension as format evidence.
4. Serve read-only with fixed media types, size limits, cache keyed by content hash; no shell execution or network fetch of asset references at runtime.
5. Keep joint transforms in the **model frame**; mesh `origin_xyz_m`, `origin_rpy_rad`, `mesh_scale_xyz` are per-link local visual frames. Consumers must compose forward kinematics, never rotate all pieces about the same world origin.
6. A model may lack assets or only provide partial sets. The current CORPO 3D skeleton must remain usable as a fallback. Never change motor policy if an asset is absent or stale.
7. `source_kind`, `calibration_revision`, `mapping_verified` and physical encoder provenance stay **separate**. Rendered shape cannot authorize CAN writes, physical FK or a safe collision model.
8. Keep manufacturer copyright and attribution. The upstream `HybridRobotics/berkeley-humanoid-lite-assets` repository has a `LICENCE` with **CC BY-SA 4.0**; downstream redistributed/modified geometry must retain its applicable notices and share-alike conditions. Do not silently copy those bytes into a MIT-only repo without the CC BY-SA attribution.
9. Performance: a mini-PC without reliable Intel GPU acceleration may rely on software WebGL; prepare decimated/LOD GLBs and load incrementally. Do not deploy 26 unoptimized raw STLs blindly.

### Staged delivery

- **VIS-0.1 (this PR)**: candidate schema, documented package conventions, security and provenance contract. No normative standard mutation.
- **VIS-0.2:** a deterministic offline URDF visual exporter: read `<link><visual><origin><geometry><mesh>`, validate paths, pack source meshes & converted GLBs under bounded limits, preserve SHA/licence. The exporter emits a candidate visual manifest and source attribution, never edits robot calibration.
- **VIS-0.3:** Console opt-in importer + **read-only** model-linked asset API, content hashing, streaming budget and WebGL GLB link-hierarchy view. First Paky-01 BHL reference should display the full genuine original geometry at neutral URDF joint angles; existing IMU cage stays separate until extrinsic alignment is reviewed.
- **VIS-0.4:** Paky-01-specific **as-built variants**, preview CAD overlays, verified encoder → joint mapping when separately available, and then PBR textures/lighting/facial shell ("hyperrealism"). Appearance fidelity and physical-kinematics certification have separate acceptance gates.

### Repo boundaries and governance

- **`OpenRGD/openrgd`** owns the draft visual manifest contract and eventual Standard authority review.
- **`OpenRGD/rgd-console`** owns a separate candidate ZIP/asset **viewer** feature, not normative interpretation.
- **`italiarobotica/paky-01`** owns actual CAD modifications, physical evidence, and later mapping to individual robots.
- **`OpenRGD/rgd-calibration`** remains the authority for calibration; visual mesh import does not replace it.
- Existing `rgd check`, compiled bundle and hardware driver boundaries are unchanged by this RFC.

See `visual-assets.schema.json` for the first candidate JSON schema. It is descriptive, not yet an accepted parser or runtime loader.
