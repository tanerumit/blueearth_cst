"""Console summaries from already-validated retained artifacts; no model calculations."""

import csv
import math
from pathlib import Path

from blueearth_cst.shared.run_log_core import log_row


def report_metric_set(root: Path, manifest: dict) -> None:
    """Count actual estimates in a validated published metric set, not planned keys."""
    finite = nonfinite = 0
    for table in manifest["tables"]:
        with (root / table["file"]["path"]).open(
            encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                value = row["value"]
                if value and math.isfinite(float(value)):
                    finite += 1
                else:
                    nonfinite += 1
    log_row(
        f"Metric set ready: {manifest['metric_set_id']}; {finite} finite and {nonfinite} "
        f"non-finite result estimates; manifest → {root / manifest['engine_root'] / 'metrics.json'}",
        module="metrics",
    )
