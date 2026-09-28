"""Independently review completed GF15 draws; never change their criteria.

Uses standard-library order statistics and recomputes decisions from estimates,
not the benchmark summary's decision flags. Replays only 36 fixed fits to check
retained samples and scheduling-independent reproducibility.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.stats import genextreme
from xclim.indices.stats import fit, parametric_quantile


def sha(path: Path) -> str:
    """Return the retained byte digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def order_summary(values: list[float]) -> dict:
    """Compute the approved linear order statistics independently."""
    if not values:
        return {
            "denominator": 0,
            "median_signed": None,
            "median_absolute": None,
            "p90_absolute": None,
        }
    absolute = sorted(abs(value) for value in values)
    position = (len(values) - 1) * 0.9
    low, high = math.floor(position), math.ceil(position)
    fraction = position - low
    return {
        "denominator": len(values),
        "median_signed": statistics.median(values),
        "median_absolute": statistics.median(absolute),
        "p90_absolute": absolute[low] * (1 - fraction) + absolute[high] * fraction,
    }


def main() -> None:
    """Verify raw evidence, decisions, errors and a fixed replay subset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.results
    inventory = json.loads((root / "evidence-inventory.json").read_text())
    for entry in inventory["files"]:
        assert sha(root / entry["path"]) == entry["sha256"], entry["path"]
    declared = json.loads((root / "matrix-results.json").read_text())
    lookup = {
        (row["shape_c"], row["n"], row["p"], row["ratio"]): row
        for row in declared["cells"]
    }
    cells: dict[tuple, list[dict]] = {}
    unique_fits = set()
    refused_fits = set()
    warning_fits = set()
    translation_ids = set()
    failed_rows = 0
    for file in sorted(root.glob("draws-*.jsonl.gz")):
        with gzip.open(file, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                c, n, p, ratio = (row[key] for key in ("shape_c", "n", "p", "ratio"))
                cells.setdefault((c, n, p, ratio), []).append(row)
                identity = (c, n, row["draw"], None if ratio is None else p, ratio)
                unique_fits.add(identity)
                if not row["valid"]:
                    refused_fits.add(identity)
                    failed_rows += 1
                    assert row["failure"] is not None and row["estimate"] is None
                if row["warnings"]:
                    warning_fits.add(identity)
                truth = float(genextreme.ppf(p, c)) if ratio is None else ratio
                assert math.isclose(
                    row["true_quantile"], truth, rel_tol=0, abs_tol=1e-12
                )
                assert row["sigma"] == 1.0
                expected_mu = (
                    0.0 if ratio is None else ratio - float(genextreme.ppf(p, c))
                )
                assert math.isclose(row["mu"], expected_mu, rel_tol=0, abs_tol=1e-12)
                if row["valid"]:
                    parameters = row["parameters_c_loc_scale"]
                    assert (
                        all(math.isfinite(value) for value in parameters)
                        and parameters[2] > 0
                    )
                    assert row["estimate"] - row["true_quantile"] == row["scale_error"]
                    if ratio not in (None, 0):
                        assert row["relative_error"] == row["scale_error"] / abs(ratio)
                if ratio in (None, 0):
                    assert row["relative_error"] is None
    assert len(cells) == 144 and len(unique_fits) == 132000
    independent = []
    for key, rows in cells.items():
        c, n, p, ratio = key
        assert len(rows) == 1000 and sorted(row["draw"] for row in rows) == list(
            range(1000)
        )
        valid = [row for row in rows if row["valid"]]
        errors = [row["estimate"] - row["true_quantile"] for row in valid]
        scale = order_summary(errors)
        relative = (
            None
            if ratio in (None, 0)
            else order_summary([error / abs(ratio) for error in errors])
        )
        limit = 0.5 if p == 0.9 else 0.25
        scale_pass = (
            len(valid) >= 950
            and abs(scale["median_signed"]) <= 0.1
            and scale["p90_absolute"] <= limit
            if valid
            else False
        )
        relative_pass = (
            (
                bool(valid)
                and abs(relative["median_signed"]) <= 0.1
                and relative["p90_absolute"] <= limit
            )
            if ratio in (0.5, 2, 10)
            else None
        )
        deviations, deltas, validity_changes = 0, [], 0
        if ratio is not None:
            baseline = {row["draw"]: row for row in cells[(c, n, p, None)]}
            for row in rows:
                before = baseline[row["draw"]]
                changed = before["valid"] != row["valid"]
                validity_changes += int(changed)
                delta = None
                if before["valid"] and row["valid"]:
                    delta = (row["estimate"] - ratio) - (
                        before["estimate"] - before["true_quantile"]
                    )
                    deltas.append(abs(delta))
                bad = changed or (delta is not None and abs(delta) > 1e-6)
                assert row["translation_pass"] == (not bad)
                assert row["translation_validity_same"] == (not changed)
                assert row["paired_scale_error_delta"] == delta
                if bad:
                    translation_ids.add((c, n, p, ratio, row["draw"]))
                    deviations += 1
        summary = lookup[key]
        for field, values in (("scale", scale), ("relative", relative)):
            if values is None:
                assert summary[field] is None
                continue
            for name, value in values.items():
                assert value == summary[field][name] or math.isclose(
                    value, summary[field][name], rel_tol=1e-12, abs_tol=1e-12
                )
        assert scale_pass == summary["scale_pass"]
        assert summary["translation_failures"] == deviations
        combined = scale_pass and relative_pass if relative_pass is not None else None
        assert combined == summary["scale_and_relative_pass"]
        qualified = combined and deviations == 0 if combined is not None else None
        assert qualified == summary["qualified_pass_including_translation"]
        independent.append(
            {
                "shape_c": c,
                "n": n,
                "p": p,
                "ratio": ratio,
                "valid": len(valid),
                "refused": 1000 - len(valid),
                "scale": scale,
                "relative": relative,
                "scale_pass": scale_pass,
                "relative_pass": relative_pass,
                "scale_and_relative_pass": combined,
                "qualified_pass_including_translation": qualified,
                "translation_failures": deviations,
                "translation_validity_changes": validity_changes,
                "translation_max_abs_delta": max(deltas, default=None),
                "translation_abs_delta_summary": order_summary(deltas),
            }
        )
    with gzip.open(
        root / "translation-deviations.jsonl.gz", "rt", encoding="utf-8"
    ) as stream:
        retained_ids = [
            (row["shape_c"], row["n"], row["p"], row["ratio"], row["draw"])
            for row in map(json.loads, stream)
        ]
    assert (
        len(retained_ids) == len(set(retained_ids))
        and set(retained_ids) == translation_ids
    )
    with gzip.open(root / "fit-failures.jsonl.gz", "rt", encoding="utf-8") as stream:
        assert sum(1 for _ in stream) == failed_rows
    replay = []
    sample_diagnostics = []
    for ci, c in enumerate((-0.2, 0.0, 0.2)):
        for n in (10, 18, 30, 60):
            data = np.load(root / f"samples-c{ci}-n{n}.npy", allow_pickle=False)
            assert data.shape == (1000, n) and np.isfinite(data).all()
            rng = np.random.Generator(
                np.random.PCG64(np.random.SeedSequence([20260912, ci, n]))
            )
            generated = genextreme.ppf(rng.random((1000, n)), c)
            assert np.allclose(data, generated, rtol=1e-12, atol=1e-12)
            sample_diagnostics.append(
                {
                    "shape_c": c,
                    "n": n,
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "negative_values": int((data < 0).sum()),
                    "npy_sha256": sha(root / f"samples-c{ci}-n{n}.npy"),
                }
            )
            for ratio in (None, 10.0):
                # Baseline's fit may be shared; scalar quantile calls stay separate.
                baseline_params = (
                    fit(
                        xr.DataArray(data[0], dims=("time",), name="gf15"),
                        dist="genextreme",
                    )
                    if ratio is None
                    else None
                )
                for p in (0.9, 0.5):
                    retained = next(
                        row for row in cells[(c, n, p, ratio)] if row["draw"] == 0
                    )
                    params = (
                        baseline_params
                        if ratio is None
                        else fit(
                            xr.DataArray(
                                data[0] + retained["mu"], dims=("time",), name="gf15"
                            ),
                            dist="genextreme",
                        )
                    )
                    value = float(parametric_quantile(params, q=p).values.ravel()[0])
                    assert value == retained["estimate"]
                    assert np.array_equal(
                        params.values, retained["parameters_c_loc_scale"]
                    )
                    replay.append(
                        {
                            "shape_c": c,
                            "n": n,
                            "p": p,
                            "ratio": ratio,
                            "draw": 0,
                            "exact": True,
                        }
                    )
    baseline = [row for row in independent if row["ratio"] is None]
    eligible = [row for row in independent if row["ratio"] in (0.5, 2, 10)]
    passed = (
        all(row["scale_pass"] for row in baseline)
        and all(row["qualified_pass_including_translation"] for row in eligible)
        and not translation_ids
    )
    assert declared["status"] == (
        "passed_bounded_estimator_matrix"
        if passed
        else "failed_owner_method_ruling_required"
    )
    result = {
        "reviewer": "Astra model-validator /root/model_validator_p3",
        "date": "2026-09-12",
        "verification_status": "passed",
        "scientific_verdict": "passed_bounded_estimator_matrix"
        if passed
        else "failed_owner_method_ruling_required",
        "criteria_unchanged": True,
        "hashed_files_verified": len(inventory["files"]),
        "evidence_inventory_sha256": sha(root / "evidence-inventory.json"),
        "matrix_sha256": sha(root / "matrix-results.json"),
        "review_script_sha256": sha(Path(__file__)),
        "unique_fits": len(unique_fits),
        "refused_fits": len(refused_fits),
        "fits_with_warnings": len(warning_fits),
        "quantile_rows": sum(len(rows) for rows in cells.values()),
        "refused_quantile_rows": failed_rows,
        "translation_pairs": 120000,
        "translation_deviations": len(translation_ids),
        "baseline_scale_pass_count": sum(row["scale_pass"] for row in baseline),
        "qualified_scale_and_relative_pass_count": sum(
            row["scale_and_relative_pass"] for row in eligible
        ),
        "qualified_pass_including_translation_count": sum(
            row["qualified_pass_including_translation"] for row in eligible
        ),
        "fixed_replay_fits": 36,
        "fixed_replay_quantiles": replay,
        "sample_diagnostics": sample_diagnostics,
        "cells": independent,
        "summary_crosscheck": "independent sorted linear interpolation and standard-library median from raw estimates; <=1e-12 numerical agreement only checks summary implementation, never changes scientific thresholds",
        "limitations": [
            "IID stationary GEV mathematical fixtures, no truncation",
            "no observed basin validation",
            "no independence/nonstationarity or screening-policy qualification",
            "point estimates; no actual-bundle fit intervals",
            "production metadata remains provisional_operational / not assessed; standalone report requires owner ruling and any later identity-bearing annotation must create new sets",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "verification_status",
                    "scientific_verdict",
                    "unique_fits",
                    "refused_fits",
                    "translation_deviations",
                    "baseline_scale_pass_count",
                    "qualified_scale_and_relative_pass_count",
                    "qualified_pass_including_translation_count",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
