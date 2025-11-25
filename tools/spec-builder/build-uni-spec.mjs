// tools/spec-builder/build-uni-spec.mjs

import { readdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import { parse } from "jsonc-parser";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Repository layout
const ROOT_DIR = path.resolve(__dirname, "..", "..");
const SPEC_DIR = path.join(ROOT_DIR, "spec");
const OUTPUT_FILE = path.join(SPEC_DIR, "openrgd_unified_spec_document.jsonc");

// Official OpenRGD domain prefixes
const DOMAIN_PREFIXES = ["01_", "02_", "03_", "04_", "05_"];

/* --------------------------------------------------------------------------
   Utility: recursive directory walk to find all .jsonc files
-------------------------------------------------------------------------- */
async function walkDir(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walkDir(fullPath)));
    } else if (entry.isFile() && entry.name.endsWith(".jsonc")) {
      files.push(fullPath);
    }
  }

  return files;
}

/* --------------------------------------------------------------------------
   Utility: infer logical metadata from a relative path
   Example: "spec/01_foundation/robot_identity.jsonc"
-------------------------------------------------------------------------- */
function inferMetadataFromPath(relPath) {
  const parts = relPath.split(path.sep);
  const filename = parts[parts.length - 1];

  const domain =
    parts.find((p) => DOMAIN_PREFIXES.some((prefix) => p.startsWith(prefix))) ||
    null;

  const id = filename.replace(".jsonc", "");

  return { id, domain };
}

/* --------------------------------------------------------------------------
   Sorting strategy:
   1) by domain order (01_ → 05_)
   2) by id (alphabetical)
-------------------------------------------------------------------------- */
function sortRecords(records) {
  const domainWeight = (domain) => {
    if (!domain) return 999;
    const prefix = DOMAIN_PREFIXES.find((pre) => domain.startsWith(pre));
    return prefix ? DOMAIN_PREFIXES.indexOf(prefix) : 999;
  };

  return records.sort((a, b) => {
    const wa = domainWeight(a.domain);
    const wb = domainWeight(b.domain);
    if (wa !== wb) return wa - wb;
    return a.id.localeCompare(b.id);
  });
}

/* --------------------------------------------------------------------------
   BUILD: Unified Specification Document
-------------------------------------------------------------------------- */
async function build() {
  console.log("🔧 OpenRGD — Building Unified Specification Document...");

  const files = await walkDir(SPEC_DIR);

  const records = [];
  for (const file of files) {
    const relPath = path.relative(ROOT_DIR, file);
    const raw = await readFile(file, "utf8");

    // JSONC → JSON (comments are removed)
    const content = parse(raw);

    const meta = inferMetadataFromPath(relPath);

    records.push({
      path: relPath.replace(/\\/g, "/"),
      id: meta.id,
      domain: meta.domain,
      content,
    });
  }

  const sortedRecords = sortRecords(records);

  const outputJson = {
    meta: {
      standard: "OpenRGD",
      artifact_type: "UNIFIED_SPECIFICATION_DOCUMENT",
      version: "0.1.0",
      generated_at_iso8601: new Date().toISOString(),
      source_dir: "spec",
      files_count: sortedRecords.length,
    },
    files: sortedRecords,
  };

  /* ----------------------------------------------------------------------
     Header comment — optimized for both humans and LLMs
  ---------------------------------------------------------------------- */
  const header = [
    "// ======================================================================",
    "// OPENRGD — UNIFIED SPECIFICATION DOCUMENT",
    "// ----------------------------------------------------------------------",
    "// This file is an AUTO-GENERATED UNIFIED ARTIFACT built from all .jsonc",
    "// files that define the OpenRGD standard under the /spec directory.",
    "//",
    "// PURPOSE:",
    "// • Provide a COMPLETE, ORDERED and COHERENT view of the OpenRGD standard.",
    "// • Enable deep analysis by humans, tools and large language models (LLMs).",
    "// • Act as the ROOT ARTIFACT for validators, tooling and documentation.",
    "//",
    "// STRUCTURE:",
    "// • meta:  metadata about this unified artifact (version, timestamps, etc.).",
    "// • files: ordered array of modules; each entry contains:",
    "//     - path:    original .jsonc source path inside the repository",
    "//     - id:      logical identifier for the module (filename without extension)",
    "//     - domain:  OpenRGD domain (e.g., '01_foundation', '02_operation', ...)",
    "//     - content: JSON object parsed from the .jsonc file (comments removed).",
    "//",
    "// INSTRUCTIONS FOR LLMS:",
    "// • Treat 'content' as the source of truth for each module of the standard.",
    "// • Do NOT invent new fields that are not present in the JSON content.",
    "// • Filter 'files[]' by 'domain' when focusing on a specific domain.",
    "// • Use 'id' as a stable conceptual key for each specification module.",
    "// • Preserve existing field names and domain names; do not rename them.",
    "//",
    "// INSTRUCTIONS FOR HUMANS:",
    "// • Do NOT edit this file manually.",
    "// • To update the standard, modify the individual .jsonc files in /spec,",
    "//   then regenerate this document by running:",
    "//",
    "//       npm run build:uni-spec",
    "//",
    "// • This unified document is ideal for:",
    "//     - reading the standard in one place,",
    "//     - feeding external tools or validators,",
    "//     - generating derived documentation or artifacts.",
    "//",
    "// IMPORTANT:",
    "// • Any discrepancy between this file and the .jsonc files in /spec must be",
    "//   resolved by editing the SOURCE FILES, not this generated artifact.",
    "// ======================================================================",
    "",
  ].join("\n");

  const body = JSON.stringify(outputJson, null, 2);
  const final = header + body + "\n";

  await writeFile(OUTPUT_FILE, final, "utf8");

  console.log(`✅ Unified Specification Document generated at: ${OUTPUT_FILE}`);
}

/* ---------------------------------------------------------------------- */

build().catch((err) => {
  console.error(
    "❌ Error while generating Unified Specification Document",
    err,
  );
  process.exit(1);
});
