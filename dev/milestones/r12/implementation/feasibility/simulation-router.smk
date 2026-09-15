"""Synthetic module selection; the runner owns top-level target enforcement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(workflow.source_path("fixture_contracts.py")).parent))
from fixture_contracts import (
    file_digest, metric_plan, metric_publication, preserve_json, read_json, validate_inventory,
    verify_metric_plan, write_json,
)

operation = config["operation"]
if operation == "simulate-and-metrics":
    include: "simulate-and-metrics.smk"
elif operation == "metrics-only":
    include: "metrics-only.smk"
else:
    raise ValueError(f"UnsupportedOperation: {operation}")

include: "metric-checkpoint.smk"
