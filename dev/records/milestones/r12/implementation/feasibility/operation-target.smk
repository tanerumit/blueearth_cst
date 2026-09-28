"""Counterexample: conditional rules alone cannot enforce R12 target selection.

This is a rejected feasibility candidate, not a proposed production interface.
Uses only documented rule/config surfaces; does not inspect private workflow
state or reparse Snakemake's command line.
"""

import json
from pathlib import Path


operation = config.get("operation", "simulate-and-metrics")
if operation not in {"simulate-and-metrics", "metrics-only"}:
    raise ValueError("Supported operations: simulate-and-metrics, metrics-only")

if operation == "metrics-only":
    inventory_path = Path("retained/inventory.json")
    if not inventory_path.is_file():
        raise ValueError("MissingResponseRequirement: retained/inventory.json")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if "q" not in inventory["variables"]:
        raise ValueError("MissingResponseRequirement: q")
    if not Path(inventory["artifact"]).is_file():
        raise ValueError(f"MissingResponseRequirement: {inventory['artifact']}")

print(f"P0_PARSE_COMPLETE operation={operation}", flush=True)

if operation == "simulate-and-metrics":
    rule all:
        input:
            metrics="metrics/selected/result.txt",
        default_target: True

    rule simulate_response:
        output:
            "hydrology/wflow/output.csv",
        run:
            Path(output[0]).write_text("q\n1\n", encoding="utf-8")
else:
    rule metrics:
        input:
            metrics="metrics/selected/result.txt",
        default_target: True

rule reduce_metric:
    input:
        "hydrology/wflow/output.csv",
    output:
        "metrics/selected/result.txt",
    run:
        response = Path(input[0]).read_text(encoding="utf-8")
        Path(output[0]).write_text(response, encoding="utf-8")
