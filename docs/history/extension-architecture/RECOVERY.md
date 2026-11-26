# Historical Extension Architecture / Command Plugin recovery

**Evidence only, not installed or accepted.** Three local original archives were reopened and matched against their original checksum manifests on 26 November 2026. These local SHA-256 commitments do not establish equivalence to any historical remote Git branch.

| Archive | SHA-256 |
|---|---|
| openrgd-v0.2-extension-architecture-review.zip | cbd8e7d8a2eaaa05c89683da482771f2cb6e71a4c72cb52aa641c834b6923018 |
| openrgd-v0.2-command-plugin-abi-v0.1-review.zip | d82441d65f6ac0c738c37e2269affddeb9dff13edda8b3b406c871561ac1dd04 |
| openrgd-v0.2.1-somatic-runtime-alignment-review.zip | 0d7c44970c25ae09e281fb485c5f1121e0ec7dc50ea4ab0c89fb628997c90f0f |

The first two use the earlier extension schema; Somatic alignment adds native_binary, E013/E014 and an illustrative manifest; command-plugin schema/loader unchanged across CLI and Somatic reviews. Phase-A extension STATUS says command_plugin_loader_implemented=false for the static architecture; separate Phase-B STATUS says implemented_for_review. Neither means the GitHub main CLI has the loader.

The attached local recovery packet `OpenRGD_EXT-01B_Recovery_2026-11-26.zip` (SHA-256 `29babc14e87b057a3d2400b389d62f9f5a090188a097093f6fc0846b20f3dca4`) retains full exact contract trees, associated guides, loader, tests, entry point and package metadata from all three revisions (23+44+46 member occurrences), original reports and member inventory, with new local validation log. It is **not** published in GitHub. Re-executed against the original full Somatic checkout: both historical validators PASS (2 schemas/11 illustrative extension files; 4 CLI descriptors) and 179 selected original pytest cases PASS (Python environment in local replay, not remote CI). No real providers or hardware tested.

This GitHub draft recovers the following six exact files from Somatic alignment; Git blob IDs matched the locally calculated blob IDs (no whole-archive overlay):

| Relative historical member | SHA-256 | Git blob SHA-1 |
|---|---|---|
| contracts/extensions/v0.1.0/schemas/extension-manifest.schema.json | 8279a0f69737e8f3704e4d09f326c073ad2ad61b3d7b1f10df694803f8f80a33 | dac51b021229d58830ca67f0cc656b0b384cfe21 |
| contracts/extensions/v0.1.0/schemas/composition.schema.json | 16c4d3d88de53ba3f853a805ebbebfcfe837753d457d423a615683d525a6d2cb | 56bff24a10f66b1fad63f606f834353b125f9347 |
| contracts/command-plugin/v0.1.0/schemas/command-plugin.schema.json | 8d666cb1f554223503df3381efd0b43f70a7e7186b44163b2ec1010456f12294 | a5369533d37b0661c6eb813f5bedd095efec1f55 |
| contracts/extensions/v0.1.0/examples/manifests/motion.json | 31eddf1387444f3bce913bd54fbc74d132842bd2935ae9da2de254a3666db3a3 | 22fae50d18b7ef6cbfa37b8ccce1b026e622298e |
| contracts/extensions/v0.1.0/examples/manifests/somatic-runtime.json | fd4abe4d3e9d811194968056c9491ec6624f82ecfdbdc6f917a4222b5ff6474f | 74b1e00d9e685e67ef6ef180735addc311af5192 |
| contracts/command-plugin/v0.1.0/migration/rgd-motion.json | 2f1acd8f46674d4c8329e6a2bf7d096d6a2bfa6d36a091f7d8909d0aea0694f9 | 92e10db59aacad44b67eb4d6563b6211cc6eda6f |

Full historical validator/loader source integration remains separate; the recovered package locally is complete for the scoped files but not an entire standalone Core checkout. The new publication proposal uses the recovered schemas only, not a substitute for semantic validation, runtime review or permission. No historic bytes modified, no archive reinterpreted as a release.
