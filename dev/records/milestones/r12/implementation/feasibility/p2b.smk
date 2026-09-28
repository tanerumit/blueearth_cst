"""P2b: row-derived producer constraints plus exact ancestor input lookup.

Run from an empty directory with --config state=resolvable|missing|no-derived.
This deliberately synthetic fixture shares no production code or model data.
"""

import re
from pathlib import Path


state = config.get("state", "resolvable")
if state not in {"resolvable", "missing", "no-derived"}:
    raise ValueError(f"Unknown P2b state: {state}")

rows = [
    {"run_id": "root-a", "derived_from": ""},
    {"run_id": "root-b", "derived_from": ""},
]
if state != "no-derived":
    rows.extend([
        {"run_id": "child-a", "derived_from": "root-a"},
        {"run_id": "child-b", "derived_from": "root-b"},
    ])
parents = {row["run_id"]: row["derived_from"] for row in rows}
root_ids = [run_id for run_id, parent in parents.items() if not parent]
derived_ids = [run_id for run_id, parent in parents.items() if parent]
root_pattern = "|".join(re.escape(run_id) for run_id in root_ids)
# An empty alternation must match nothing, rather than relaxing the constraint.
derived_pattern = "|".join(re.escape(run_id) for run_id in derived_ids) or "(?!)"


rule all:
    input:
        forcing=expand("forcing/{run_id}.txt", run_id=derived_ids or root_ids),
    default_target: True


if state != "missing":
    rule produce_root:
        output:
            "forcing/{run_id}.txt",
        wildcard_constraints:
            run_id=root_pattern,
        threads: 1
        run:
            Path(output[0]).write_text(f"source:{wildcards.run_id}\n", encoding="utf-8")


rule transform_forcing:
    input:
        ancestor=lambda wc: f"forcing/{parents[wc.run_id]}.txt",
    output:
        "forcing/{run_id}.txt",
    wildcard_constraints:
        run_id=derived_pattern,
    threads: 1
    run:
        ancestor = Path(input.ancestor).read_text(encoding="utf-8")
        Path(output[0]).write_text(
            f"{ancestor}transform:{wildcards.run_id}\n", encoding="utf-8"
        )
