"""
OpenRGD Spec Unifier

Shared utilities for scanning, merging and generating unified specification
documents (Human Twin JSONC + Machine Twin JSON), including per-domain bundles.

This module is intended to be used by:
- the compiler commands (spec compilation and bundling)
- integrity checks (rebuilding unified specs for comparison)
"""

import json
import time
from pathlib import Path
from datetime import datetime
import re

from ..core.utils import strip_jsonc
from ..core.visuals import log, smart_track
from ..core.config import state

# Domain weight mapping for deterministic ordering
DOMAIN_WEIGHTS = {
    "01_": 1,
    "02_": 2,
    "03_": 3,
    "04_": 4,
    "05_": 5,
    "06_": 6,
}


def indent_block(text: str, indent_str: str = "      ") -> str:
    """Indents a block of text so it fits inside a JSON/JSONC structure."""
    lines = text.split("\n")
    return "\n".join(
        [f"{indent_str}{line}" if line.strip() else line for line in lines]
    )


def detect_domain_from_relpath(rel_path: Path) -> tuple[str, int]:
    """
    Detect the domain name and weight from a relative path, e.g.:
        spec/01_foundation/...
    """
    domain = "unknown"
    weight = 999
    for part in rel_path.parts:
        for prefix, w in DOMAIN_WEIGHTS.items():
            if part.startswith(prefix):
                domain = part
                weight = w
                break
    return domain, weight


def scan_spec_records(root_dir: Path, spec_dir: Path):
    """
    Scan the /spec tree and return a list of records describing all JSONC files.

    Each record contains:
    - path: relative path from root_dir (string, POSIX style)
    - id: file stem name
    - domain: inferred domain (e.g. 01_foundation)
    - weight: numeric ordering weight
    - raw_content: original JSONC text (with comments)
    - parsed_content: cleaned JSON object (dict) parsed from JSONC
    """
    log(f"Scanning source: {spec_dir}", "DEBUG")

    records = []
    file_list = sorted(spec_dir.rglob("*.jsonc"))

    for file_path in smart_track(file_list, "[cyan]Compiling Standard...[/]"):
        if "unified_spec" in file_path.name:
            # Avoid including previously generated unified specs
            continue
        if state.get("cinematic"):
            time.sleep(0.05)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()

            clean_content = json.loads(strip_jsonc(raw_text), strict=False)

            rel_path = file_path.relative_to(root_dir)
            domain, weight = detect_domain_from_relpath(rel_path)

            records.append(
                {
                    "path": str(rel_path).replace("\\", "/"),
                    "id": file_path.stem,
                    "domain": domain,
                    "weight": weight,
                    "raw_content": raw_text,
                    "parsed_content": clean_content,
                }
            )
        except Exception as e:
            log(f"Skipping {file_path.name}: {e}", "WARN")

    # Sort by domain weight first, then by id
    records.sort(key=lambda x: (x["weight"], x["id"]))
    return records


def build_domain_maps(records):
    """
    Build domain-oriented views from records.

    Returns:
    - domain_map:    domain_name -> list of records
    - domain_aliases: alias -> canonical domain_name
        e.g. "01", "foundation", "01_foundation" -> "01_foundation"
    """
    domain_map = {}
    for r in records:
        dom = r["domain"]
        if dom == "unknown":
            continue
        domain_map.setdefault(dom, []).append(r)

    domain_aliases = {}
    for dom in domain_map.keys():
        lower_dom = dom.lower()
        domain_aliases[lower_dom] = dom
        if "_" in lower_dom:
            prefix, label = lower_dom.split("_", 1)
            domain_aliases[prefix] = dom
            domain_aliases[label] = dom

    return domain_map, domain_aliases


def generate_machine_unified_from_records(
    records, out_dir: Path, output_base: str, note: str = "Strict JSON for tooling."
):
    """
    Generate the unified Machine Twin JSON directly from records' parsed_content.

    Produces a single JSON file with:
    - meta: OpenRGD metadata
    - files: list of all modules, each with path/id/domain/content
    """
    machine_files = []
    for r in records:
        machine_files.append(
            {
                "path": r["path"],
                "id": r["id"],
                "domain": r["domain"],
                "content": r["parsed_content"],
            }
        )

    machine_doc = {
        "meta": {
            "standard": "OpenRGD",
            "type": "MACHINE_TWIN_CLEAN",
            "version": "0.1.0",
            "generated_at": datetime.now().isoformat(),
            "note": note,
        },
        "files": machine_files,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    path_j = out_dir / f"{output_base}.json"
    with open(path_j, "w", encoding="utf-8") as f:
        json.dump(machine_doc, f, indent=2)
    log(f"Machine Twin generated: {path_j}", "SUCCESS")


def generate_human_unified_from_records(records, out_dir: Path, output_base: str):
    """
    Generate the unified Human Twin JSONC, preserving comments.

    This file acts as the canonical, human-readable aggregation of all modules,
    keeping their original JSONC content, including comments.
    """
    log("Weaving Human Twin (Preserving Comments)...", "DEBUG")

    jsonc_lines = []
    jsonc_lines.append("// ======================================================================")
    jsonc_lines.append("// OPENRGD — UNIFIED SPECIFICATION (HUMAN TWIN)")
    jsonc_lines.append("// ----------------------------------------------------------------------")
    jsonc_lines.append(f"// Generated at: {datetime.now().isoformat()}")
    jsonc_lines.append(
        "// This file contains the raw source code of all modules, comments included."
    )
    jsonc_lines.append("// ======================================================================")
    jsonc_lines.append("")
    jsonc_lines.append("{")

    jsonc_lines.append('  "meta": {')
    jsonc_lines.append('    "standard": "OpenRGD",')
    jsonc_lines.append('    "type": "HUMAN_TWIN_WITH_COMMENTS",')
    jsonc_lines.append('    "version": "0.1.0"')
    jsonc_lines.append("  },")

    jsonc_lines.append('  "files": [')

    total = len(records)
    for i, r in enumerate(records):
        jsonc_lines.append("    {")
        jsonc_lines.append(f'      "path": "{r["path"]}",')
        jsonc_lines.append(f'      "id": "{r["id"]}",')
        jsonc_lines.append(f'      "domain": "{r["domain"]}",')
        jsonc_lines.append('      "content": ')
        indented_raw = indent_block(r["raw_content"], indent_str="      ")
        jsonc_lines.append(indented_raw)

        if i < total - 1:
            jsonc_lines.append("    },")
        else:
            jsonc_lines.append("    }")

    jsonc_lines.append("  ]")
    jsonc_lines.append("}")

    out_dir.mkdir(parents=True, exist_ok=True)
    path_c = out_dir / f"{output_base}.jsonc"
    with open(path_c, "w", encoding="utf-8") as f:
        f.write("\n".join(jsonc_lines))
    log(f"Human Twin generated: {path_c}", "SUCCESS")


def ensure_standard_from_spec(spec_dir: Path, standard_dir: Path):
    """
    Step 1 of the full pipeline:
    Convert all *.jsonc files under /spec into *.json under /standard,
    preserving the folder structure.
    """
    log("Syncing /spec → /standard ...", "SYSTEM")
    standard_dir.mkdir(parents=True, exist_ok=True)

    file_list = sorted(spec_dir.rglob("*.jsonc"))
    for file_path in smart_track(file_list, "[cyan]Mirroring to /standard...[/]"):
        if "unified_spec" in file_path.name:
            # Do not mirror previously generated unified specs
            continue
        rel = file_path.relative_to(spec_dir)
        target = standard_dir / rel
        target = target.with_suffix(".json")
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
        data = json.loads(strip_jsonc(raw), strict=False)

        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    log("Standard mirror updated under /standard.", "SUCCESS")


def generate_machine_unified_from_standard(
    root_dir: Path, standard_dir: Path, output_base: str
):
    """
    Step 3 of the full pipeline:
    Build openrgd_unified_spec.json under /standard by scanning existing
    cleaned JSON files in /standard (mirror of /spec).
    """
    log("Building Machine Twin from /standard ...", "SYSTEM")

    records = []
    file_list = sorted(standard_dir.rglob("*.json"))

    for file_path in file_list:
        name = file_path.name
        # Skip unified specs or domain bundles if they already exist
        if "unified_spec" in name:
            continue
        if name.endswith("_spec.json"):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        rel_path = file_path.relative_to(root_dir)
        domain, weight = detect_domain_from_relpath(rel_path)

        records.append(
            {
                "path": str(rel_path).replace("\\", "/"),
                "id": file_path.stem,
                "domain": domain,
                "weight": weight,
                "parsed_content": content,
            }
        )

    records.sort(key=lambda x: (x["weight"], x["id"]))

    machine_files = []
    for r in records:
        machine_files.append(
            {
                "path": r["path"],
                "id": r["id"],
                "domain": r["domain"],
                "content": r["parsed_content"],
            }
        )

    machine_doc = {
        "meta": {
            "standard": "OpenRGD",
            "type": "MACHINE_TWIN_FROM_STANDARD",
            "version": "0.1.0",
            "generated_at": datetime.now().isoformat(),
            "note": "Built from /standard JSON mirror.",
        },
        "files": machine_files,
    }

    standard_dir.mkdir(parents=True, exist_ok=True)
    path_j = standard_dir / f"{output_base}.json"
    with open(path_j, "w", encoding="utf-8") as f:
        json.dump(machine_doc, f, indent=2)
    log(f"Machine Twin (from /standard) generated: {path_j}", "SUCCESS")


def generate_domain_bundles(
    domain_map: dict,
    jsonc_dir: Path,
    json_dir: Path,
    target_domains: list | None = None,
):
    """
    Generate per-domain bundles, either for all domains or a given subset.

    For each selected domain XX (e.g. 01_foundation), this function outputs:
      - /spec/XX_spec.jsonc    (Human Twin, with comments)
      - /standard/XX_spec.json (Machine Twin, strict JSON)
    """
    if target_domains is None:
        domain_ids = sorted(domain_map.keys())
    else:
        domain_ids = target_domains

    for dom in domain_ids:
        records = sorted(domain_map.get(dom, []), key=lambda x: x["id"])
        if not records:
            log(f"No records found for domain {dom}", "WARN")
            continue

        prefix = dom.split("_", 1)[0]
        base_name = f"{prefix}_spec"

        # Machine Twin (JSON) for the domain
        machine_files = []
        for r in records:
            machine_files.append(
                {
                    "path": r["path"],
                    "id": r["id"],
                    "domain": r["domain"],
                    "content": r["parsed_content"],
                }
            )

        machine_doc = {
            "meta": {
                "standard": "OpenRGD",
                "type": "DOMAIN_MACHINE_TWIN",
                "version": "0.1.0",
                "domain": dom,
                "generated_at": datetime.now().isoformat(),
            },
            "files": machine_files,
        }

        json_dir.mkdir(parents=True, exist_ok=True)
        path_j = json_dir / f"{base_name}.json"
        with open(path_j, "w", encoding="utf-8") as f:
            json.dump(machine_doc, f, indent=2)
        log(f"[Domain {dom}] Machine bundle generated: {path_j}", "SUCCESS")

        # Human Twin (JSONC) for the domain
        jsonc_lines = []
        jsonc_lines.append("// =====================================================")
        jsonc_lines.append(f"// OPENRGD — DOMAIN SPEC (HUMAN TWIN) — {dom}")
        jsonc_lines.append("// -----------------------------------------------------")
        jsonc_lines.append(f"// Generated at: {datetime.now().isoformat()}")
        jsonc_lines.append("// =====================================================")
        jsonc_lines.append("")
        jsonc_lines.append("{")
        jsonc_lines.append('  "meta": {')
        jsonc_lines.append('    "standard": "OpenRGD",')
        jsonc_lines.append('    "type": "DOMAIN_HUMAN_TWIN_WITH_COMMENTS",')
        jsonc_lines.append(f'    "domain": "{dom}",')
        jsonc_lines.append('    "version": "0.1.0"')
        jsonc_lines.append("  },")
        jsonc_lines.append('  "files": [')

        total = len(records)
        for i, r in enumerate(records):
            jsonc_lines.append("    {")
            jsonc_lines.append(f'      "path": "{r["path"]}",')
            jsonc_lines.append(f'      "id": "{r["id"]}",')
            jsonc_lines.append(f'      "domain": "{r["domain"]}",')
            jsonc_lines.append('      "content": ')
            indented_raw = indent_block(r["raw_content"], indent_str="      ")
            jsonc_lines.append(indented_raw)

            if i < total - 1:
                jsonc_lines.append("    },")
            else:
                jsonc_lines.append("    }")

        jsonc_lines.append("  ]")
        jsonc_lines.append("}")

        jsonc_dir.mkdir(parents=True, exist_ok=True)
        path_c = jsonc_dir / f"{base_name}.jsonc"
        with open(path_c, "w", encoding="utf-8") as f:
            f.write("\n".join(jsonc_lines))
        log(f"[Domain {dom}] Human bundle generated: {path_c}", "SUCCESS")


# ---------------------------------------------------------------------------
# JSONC normalization helpers
# ---------------------------------------------------------------------------

_GENERATED_AT_RE = re.compile(r".*Generated at:.*")


def normalize_human_jsonc(text: str) -> str:
    """
    Normalize a Human Twin JSONC document for integrity comparison.

    - Removes lines containing volatile timestamps ("Generated at:")
    - Strips trailing whitespace

    This allows deterministic comparison between regenerated JSONC files
    and their benchmark snapshots.
    """
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        if _GENERATED_AT_RE.search(line):
            # Drop timestamp/comment lines
            continue
        out_lines.append(line.rstrip())
    return "\n".join(out_lines)
