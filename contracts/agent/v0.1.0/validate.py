from pathlib import Path
import json

root=Path(__file__).parent
schemas=list((root/"schemas").glob("*.json"))
for p in schemas:
    data=json.loads(p.read_text())
    assert data.get("$schema")
    assert data.get("title")
example=json.loads((root/"examples/so101-causal-flow.json").read_text())
assert len(example["chronon_flow"]) >= 6
print(f"PASS: {len(schemas)} schemas + SO-101 causal-flow example")
