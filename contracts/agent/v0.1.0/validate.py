from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    status = json.loads((ROOT / "STATUS.json").read_text(encoding="utf-8"))
    assert status["package"] == "openrgd-agent-contracts"
    assert status["version"] == "0.1.0"
    assert status["maturity"] == "candidate"
    assert status["normative"] is False
    assert status["accepted"] is False
    assert status["stable_release_allowed"] is False
    assert len(status["source_snapshot_sha256"]) == 64
    assert len(status["promotion_requires"]) >= 6

    schemas = sorted((ROOT / "schemas").glob("*.json"))
    assert schemas, "no schemas found"
    for path in schemas:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("$schema"), f"missing $schema in {path.name}"
        assert data.get("title"), f"missing title in {path.name}"

    example = json.loads(
        (ROOT / "examples" / "so101-causal-flow.json").read_text(encoding="utf-8")
    )
    assert len(example["chronon_flow"]) >= 6

    print(
        "PASS: candidate status + "
        f"{len(schemas)} schemas + SO-101 causal-flow example"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
