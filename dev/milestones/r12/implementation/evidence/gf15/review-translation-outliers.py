"""Replay three distinct draws with the largest observed translation deviations.

Post-result diagnosis only: no estimator option, criterion or fit validity rule
changes. The likelihood values describe the retained fits; they are not a new
acceptance criterion or an alternative estimate.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.stats import genextreme
from xclim.indices.stats import fit, parametric_quantile


def main() -> None:
    """Retain exact replays, sample values and descriptive likelihood checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = []
    baseline = {}
    for path in sorted(args.results.glob("draws-*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                key = (row["shape_c"], row["n"], row["p"], row["draw"])
                if row["ratio"] is None:
                    baseline[key] = row
                elif row.get("paired_scale_error_delta") is not None:
                    rows.append(row)
    rows.sort(key=lambda row: abs(row["paired_scale_error_delta"]), reverse=True)
    selected = []
    seen = set()
    for row in rows:
        key = (row["shape_c"], row["n"], row["p"], row["draw"])
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) == 3:
            break
    evidence = []
    for row in selected:
        key = (row["shape_c"], row["n"], row["p"], row["draw"])
        before = baseline[key]
        path = args.results / f"samples-c{row['shape_index']}-n{row['n']}.npy"
        sample = np.load(path, allow_pickle=False)[row["draw"]]
        checks = []
        for record, data in ((before, sample), (row, sample + row["mu"])):
            params = fit(
                xr.DataArray(data, dims=("time",), name="gf15"), dist="genextreme"
            )
            estimate = float(parametric_quantile(params, q=row["p"]).values.ravel()[0])
            assert estimate == record["estimate"]
            assert np.array_equal(params.values, record["parameters_c_loc_scale"])
            log_density = genextreme.logpdf(data, *params.values)
            nll = float(-log_density.sum())
            checks.append(
                {
                    "ratio": record["ratio"],
                    "exact_parameter_and_quantile_replay": True,
                    "negative_log_likelihood": nll if np.isfinite(nll) else str(nll),
                    "nonfinite_log_density_count": int(
                        (~np.isfinite(log_density)).sum()
                    ),
                }
            )
        shifted_baseline = np.array(before["parameters_c_loc_scale"])
        shifted_baseline[1] += row["mu"]
        mapped_nll = float(
            -genextreme.logpdf(sample + row["mu"], *shifted_baseline).sum()
        )
        evidence.append(
            {
                "baseline": before,
                "translated": row,
                "sample": sample.tolist(),
                "sample_file": path.name,
                "sample_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "replays": checks,
                "baseline_parameters_mapped_to_translated_sample_nll": mapped_nll
                if np.isfinite(mapped_nll)
                else str(mapped_nll),
            }
        )
    result = {
        "verification_status": "passed",
        "reviewer": "Astra model-validator /root/model_validator_p3",
        "date": "2026-09-12",
        "selection": "Three distinct shape/count/probability/draw keys with largest absolute observed paired scale-error deltas; selected after complete matrix for diagnosis only",
        "fits_replayed": 6,
        "criterion_and_estimator_changes": False,
        "review_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": evidence,
    }
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "verification_status": "passed",
                "exact_replays": 6,
                "maximum_abs_delta": abs(rows[0]["paired_scale_error_delta"]),
            }
        )
    )


if __name__ == "__main__":
    main()
