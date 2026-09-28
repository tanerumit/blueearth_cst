"""Characterize Linux GF15 quantile controls without changing frozen tests."""

import json
import math
import struct
from pathlib import Path

from blueearth_cst.experiment import gev_lmoments as gev
from blueearth_cst.experiment.metric_plan import resolve_metric_environment

root = Path(__file__).resolve().parents[7]
controls_path = (
    root
    / "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/attempt-2/numerical-controls.json"
)
controls = json.loads(controls_path.read_text(encoding="utf-8"))


def bits(value):
    return struct.pack(">d", float(value)).hex()


rows = []
for control in controls["quantiles"]:
    normalized = control["normalized"]
    produced = float(gev._quantile(normalized["parameters"], normalized["p"]))
    reference = float(normalized["output"])
    error = abs(produced - reference)
    tolerance = 1e-10 * max(1.0, abs(reference))
    rows.append(
        {
            "label": control["label"],
            "reference_bits": normalized["output_bits"],
            "linux_bits": bits(produced),
            "absolute_error": error,
            "tolerance": tolerance,
            "within_fixed_tolerance": math.isfinite(produced) and error <= tolerance,
        }
    )

mutant_count = 0
for control in controls["quantiles"]:
    normalized = control["normalized"]
    baseline = float(gev._quantile(normalized["parameters"], normalized["p"]))
    mutant = baseline * (1.0 + 1e-9)
    tolerance = 1e-10 * max(1.0, abs(baseline))
    mutant_count += abs(mutant - baseline) > tolerance

result = {
    "quantile_controls": len(rows),
    "bit_equal": sum(row["reference_bits"] == row["linux_bits"] for row in rows),
    "within_fixed_tolerance": sum(row["within_fixed_tolerance"] for row in rows),
    "max_absolute_error": max(row["absolute_error"] for row in rows),
    "wrong_result_mutant_caught": mutant_count,
    "different_bits": [
        row for row in rows if row["reference_bits"] != row["linux_bits"]
    ],
    "metric_environment": resolve_metric_environment(),
}
print(json.dumps(result, indent=2, sort_keys=True))
