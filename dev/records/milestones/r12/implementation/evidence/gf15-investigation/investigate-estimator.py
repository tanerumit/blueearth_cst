"""Diagnose retained GF15 fits and trace a fixed subset with unchanged settings.

This script produces investigation evidence, never new qualification results.
It reads immutable GF15 samples/results and writes only a new output directory.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import inspect
import json
import subprocess
import time
import warnings
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import scipy.optimize._optimize as optimize_source
import xarray as xr
import xclim.indices.stats as xclim_stats
from scipy import optimize
from scipy.stats import genextreme, norm
from xclim.indices.stats import fit, parametric_quantile

ROOT = Path(__file__).resolve().parents[6]
OLD = ROOT / "dev/milestones/r12/implementation/evidence/gf15"
SHAPES = (-0.2, 0.0, 0.2)
COUNTS = (10, 18, 30, 60)
DRAW_IDS = (0, 499, 999)


def sha(path: Path) -> str:
    """Hash exact retained bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value: Any) -> Any:
    """Preserve nonfinite diagnostics explicitly without invalid JSON numbers."""
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [plain(item) for item in value]
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


def write_json(path: Path, value: Any) -> None:
    """Write LF JSON with all undefined/nonfinite diagnostics explicit."""
    path.write_text(
        json.dumps(plain(value), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def summary(values: np.ndarray) -> dict[str, Any]:
    """Describe finite values while retaining counts of nonfinite values."""
    data = np.asarray(values, dtype=float)
    finite = data[np.isfinite(data)]
    return {
        "total": data.size,
        "finite": finite.size,
        "nonfinite": data.size - finite.size,
        "min": np.min(finite) if finite.size else None,
        "p50": np.quantile(finite, 0.5) if finite.size else None,
        "p90": np.quantile(finite, 0.9) if finite.size else None,
        "p95": np.quantile(finite, 0.95) if finite.size else None,
        "p99": np.quantile(finite, 0.99) if finite.size else None,
        "max": np.max(finite) if finite.size else None,
    }


def verify_original() -> dict[str, Any]:
    """Check the full original evidence manifest without rewriting anything."""
    path = OLD / "artifact-inventory.json"
    inventory = json.loads(path.read_text())
    for item in inventory["files"]:
        target = OLD / item["path"]
        assert (
            target.stat().st_size == item["bytes"] and sha(target) == item["sha256"]
        ), target
    return {"inventory_sha256": sha(path), "files_verified": len(inventory["files"])}


def protocol() -> dict[str, Any]:
    """Pin the bounded selection before running diagnostic calculations."""
    return {
        "approved_scope": "Owner approved bounded fitting-stability and sample-size investigation on 2026-09-12 after GF15 failure; production unchanged",
        "original_evidence": str(OLD),
        "whole_retained_fit_count": 132000,
        "trace_selection": {
            "predetermined_draw_ids": DRAW_IDS,
            "shapes_scipy_c": SHAPES,
            "counts": COUNTS,
            "per_draw": "baseline once plus p={.9,.5} x rho={0,10}; five fits",
            "predetermined_fits": 180,
            "witness_fits": 6,
            "total_fits": 186,
            "witness_source": "original translation-outlier-review.json, same three distinct worst cases and their baselines",
            "interpretation": "fixed diagnostic grid plus purposive extremes; no frequency extrapolation to entire matrix from traces",
        },
        "tracing": "spy on _minimize_neldermead; forward every positional and keyword argument unchanged; wrap objective to record identical returned values; record result object; no optimizer/tolerance/start/full_output/retall overrides",
        "likelihood": "public unpenalized genextreme.logpdf across all retained fits; feasibility/nonfinite log-density counts retained; actual penalized objective recorded in traces",
        "sampling": "all24 baseline cells; robust error quantiles, all extremes, top10/1000 contribution and explicitly diagnostic trim; original acceptance decisions untouched",
        "oracle_scale": "asymptotic empirical-quantile standard error sqrt(p*(1-p)/n)/f(qp), descriptive only; not a GEV-MLE bound, interval or alternative estimator run",
        "no_new_qualification": True,
        "no_modified_method_runs": True,
        "no_screening_policy_change": True,
    }


def load_retained() -> tuple[dict[tuple, list[dict]], dict[tuple, np.ndarray]]:
    """Load every quantile record and every original standardized sample."""
    cells: dict[tuple, list[dict]] = {}
    for path in sorted((OLD / "results").glob("draws-*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                cells.setdefault(
                    (row["shape_c"], row["n"], row["p"], row["ratio"]), []
                ).append(row)
    for rows in cells.values():
        rows.sort(key=lambda row: row["draw"])
        assert [row["draw"] for row in rows] == list(range(1000))
    arrays = {
        (c, n): np.load(OLD / "results" / f"samples-c{i}-n{n}.npy", allow_pickle=False)
        for i, c in enumerate(SHAPES)
        for n in COUNTS
    }
    assert len(cells) == 144
    return cells, arrays


def likelihood(
    data: np.ndarray, params: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate row-wise raw likelihood and boundary margins, without fitting."""
    c, loc, scale = params.T
    logpdf = genextreme.logpdf(data, c[:, None], loc[:, None], scale[:, None])
    nll = -logpdf.sum(axis=1)
    nonfinite = (~np.isfinite(logpdf)).sum(axis=1)
    support_margin = (1 - c[:, None] * (data - loc[:, None]) / scale[:, None]).min(
        axis=1
    )
    return nll, nonfinite, support_margin


def analyze(output: Path, cells: dict, arrays: dict) -> None:
    """Inspect every retained parameter vector and baseline error distribution."""
    started = time.perf_counter()
    group_summaries = []
    total = 0
    with (
        (output / "retained-fit-diagnostics.jsonl.gz").open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream,
    ):
        for key, rows in cells.items():
            c, n, p, ratio = key
            if ratio is None and p == 0.5:
                # Identical baseline fit appears at both quantiles in original evidence.
                assert [row["parameters_c_loc_scale"] for row in rows] == [
                    row["parameters_c_loc_scale"] for row in cells[(c, n, 0.9, None)]
                ]
                continue
            base = arrays[(c, n)]
            data = base + rows[0]["mu"]
            params = np.array([row["parameters_c_loc_scale"] for row in rows])
            true_params = np.tile([c, rows[0]["mu"], 1.0], (1000, 1))
            fitted_nll, bad, margin = likelihood(data, params)
            true_nll, true_bad, _ = likelihood(data, true_params)
            assert not true_bad.any()
            baseline_params = np.array(
                [row["parameters_c_loc_scale"] for row in cells[(c, n, 0.9, None)]]
            )
            mapped_params = baseline_params.copy()
            mapped_params[:, 1] += rows[0]["mu"]
            mapped_nll, mapped_bad, mapped_margin = likelihood(data, mapped_params)
            with np.errstate(invalid="ignore"):
                true_gap = fitted_nll - true_nll
                mapped_gap = fitted_nll - mapped_nll
            group = {
                "shape_c": c,
                "n": n,
                "p": None if ratio is None else p,
                "ratio": ratio,
                "fits": 1000,
                "fitted_shape": summary(params[:, 0]),
                "fitted_scale": summary(params[:, 2]),
                "shape_below_minus_one": int((params[:, 0] < -1).sum()),
                "shape_above_one": int((params[:, 0] > 1).sum()),
                "nonfinite_raw_likelihood_fits": int((bad > 0).sum()),
                "min_support_margin": summary(margin),
                "fit_minus_true_nll": summary(true_gap),
                "fit_worse_than_true_raw_count": int((true_gap > 0).sum()),
                "fit_minus_mapped_baseline_nll": summary(mapped_gap),
                "mapped_baseline_feasible_count": int((mapped_bad == 0).sum()),
                "fit_worse_than_feasible_mapped_baseline_raw_count": int(
                    ((mapped_bad == 0) & (mapped_gap > 0)).sum()
                ),
                "note": "Positive raw floating-point objective gaps are descriptive; tiny positive gaps may be roundoff. No new acceptance threshold.",
            }
            group_summaries.append(group)
            for i, row in enumerate(rows):
                item = {
                    "shape_c": c,
                    "n": n,
                    "draw": i,
                    "p": group["p"],
                    "ratio": ratio,
                    "parameters": params[i],
                    "fitted_nll": fitted_nll[i],
                    "true_nll": true_nll[i],
                    "fit_minus_true_nll": true_gap[i],
                    "nonfinite_log_density_count": bad[i],
                    "min_support_margin": margin[i],
                    "mapped_baseline_nll": mapped_nll[i],
                    "mapped_baseline_nonfinite_log_density_count": mapped_bad[i],
                    "mapped_baseline_min_support_margin": mapped_margin[i],
                    "fit_minus_mapped_baseline_nll": mapped_gap[i],
                }
                stream.write((json.dumps(plain(item), allow_nan=False) + "\n").encode())
                total += 1
    assert total == 132000
    write_json(
        output / "parameter-likelihood-summary.json",
        {
            "fits": total,
            "groups": group_summaries,
            "seconds": time.perf_counter() - started,
        },
    )
    accuracy = []
    for c in SHAPES:
        for n in COUNTS:
            for p in (0.9, 0.5):
                rows = cells[(c, n, p, None)]
                errors = np.array([row["scale_error"] for row in rows])
                absolute = abs(errors)
                order = np.argsort(absolute, kind="stable")
                top = order[-10:]
                rest = order[:-10]
                limit = 0.5 if p == 0.9 else 0.25
                true_q = genextreme.ppf(p, c)
                density = p * (-np.log(p)) ** (1 - c)
                assert np.isclose(
                    density, genextreme.pdf(true_q, c), atol=1e-12, rtol=0
                )
                empirical_se = np.sqrt(p * (1 - p) / n) / density
                accuracy.append(
                    {
                        "shape_c": c,
                        "n": n,
                        "p": p,
                        "draws": 1000,
                        "signed_error": summary(errors),
                        "absolute_error": summary(absolute),
                        "p90_abs_times_sqrt_n": np.quantile(absolute, 0.9) * np.sqrt(n),
                        "mae": np.mean(absolute),
                        "rmse": np.sqrt(np.mean(errors**2)),
                        "top_10_absolute_error_draw_ids": top.tolist(),
                        "top_10_share_of_total_absolute_error": absolute[top].sum()
                        / absolute.sum(),
                        "top_10_share_of_total_squared_error": (errors[top] ** 2).sum()
                        / (errors**2).sum(),
                        "diagnostic_excluding_largest_10": {
                            "retained": 990,
                            "dropped": 10,
                            "p90_absolute": np.quantile(absolute[rest], 0.9),
                            "median_signed": np.median(errors[rest]),
                            "note": "descriptive sensitivity only; not qualification; all1000 retained and original decisions unchanged",
                        },
                        "fraction_exceeding_original_absolute_error_target": np.mean(
                            absolute > limit
                        ),
                        "asymptotic_empirical_quantile_se": empirical_se,
                        "asymptotic_empirical_quantile_p90_abs_normal": norm.ppf(0.95)
                        * empirical_se,
                        "oracle_scope": "known generating density; empirical-quantile asymptotic scale, NOT a GEV-MLE bound or finite-n interval",
                    }
                )
    write_json(
        output / "sample-size-accuracy.json",
        {"original_baseline_cells": 24, "new_fits": 0, "cells": accuracy},
    )
    print(
        json.dumps(
            {
                "stage": "retained_analysis",
                "fits_read": total,
                "seconds": time.perf_counter() - started,
            }
        ),
        flush=True,
    )


@contextmanager
def capture_optimizer(capture: list[dict]):
    """Observe the original Nelder-Mead function and result with unchanged options."""
    original = optimize_source._minimize_neldermead

    def spy(func, x0, *args, **kwargs):
        evaluations = []

        def objective(parameters, *objective_args):
            value = func(parameters, *objective_args)
            evaluations.append(
                {"parameters": np.array(parameters).copy(), "objective": value}
            )
            return value

        result = original(objective, x0, *args, **kwargs)
        capture.append(
            {
                "x0": np.array(x0).copy(),
                "options_passed_unchanged": kwargs,
                "positional_extra_count": len(args),
                "evaluations": evaluations,
                "result": {
                    name: result[name]
                    for name in (
                        "x",
                        "fun",
                        "nit",
                        "nfev",
                        "status",
                        "success",
                        "message",
                        "final_simplex",
                    )
                },
            }
        )
        return result

    with patch.object(optimize_source, "_minimize_neldermead", spy):
        yield


def controls() -> dict[str, Any]:
    """Prove the spy observes convergence and default-budget failure exactly."""
    plain_result = optimize.fmin(lambda x: (x[0] - 2) ** 2, [1.0], disp=0)
    captured = []
    with capture_optimizer(captured):
        traced_result = optimize.fmin(lambda x: (x[0] - 2) ** 2, [1.0], disp=0)
    assert np.array_equal(plain_result, traced_result)
    assert captured[0]["result"]["status"] == 0
    limit = []
    with capture_optimizer(limit):
        optimize.fmin(lambda x: -x[0], [1.0], disp=0)
    assert limit[0]["result"]["status"] == 1 and limit[0]["result"]["nfev"] == 200
    test_data = np.array([[-1.0, 0.0, 1.0]])
    test_params = np.array([[0.0, 0.0, 1.0]])
    value, bad, _ = likelihood(test_data, test_params)
    assert (
        bad[0] == 0
        and abs(value[0] - genextreme._penalized_nnlf(test_params[0], test_data[0]))
        < 1e-12
    )
    _, invalid, _ = likelihood(np.array([[2.0, 3.0]]), np.array([[1.0, 0.0, 1.0]]))
    assert invalid[0] == 2
    return {
        "status": "passed",
        "toy_quadratic_exact": True,
        "toy_success_status": 0,
        "toy_monotone_status": 1,
        "toy_monotone_nfev": 200,
        "scalar_penalized_objective_equals_finite_vectorized_nll": True,
        "unsupported_sample_detected": True,
        "toy_cases_not_GEV_performance_evidence": True,
    }


def trace(output: Path, cells: dict, arrays: dict) -> None:
    """Trace all186 fixed fits and require exact replay against original results."""
    selected = []
    for c in SHAPES:
        for n in COUNTS:
            for draw in DRAW_IDS:
                selected.append(("predetermined", c, n, draw, None, None))
                selected.extend(
                    ("predetermined", c, n, draw, p, ratio)
                    for p in (0.9, 0.5)
                    for ratio in (0.0, 10.0)
                )
    witnesses = json.loads((OLD / "translation-outlier-review.json").read_text())
    for case in witnesses["cases"]:
        row = case["translated"]
        selected.extend(
            [
                ("witness", row["shape_c"], row["n"], row["draw"], None, None),
                (
                    "witness",
                    row["shape_c"],
                    row["n"],
                    row["draw"],
                    row["p"],
                    row["ratio"],
                ),
            ]
        )
    assert len(selected) == 186
    results = []
    started = time.perf_counter()
    with (
        (output / "optimizer-evaluations.jsonl.gz").open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream,
    ):
        for number, (selection, c, n, draw, p, ratio) in enumerate(selected):
            original_row = cells[(c, n, 0.9 if p is None else p, ratio)][draw]
            data = arrays[(c, n)][draw] + original_row["mu"]
            captured = []
            with (
                warnings.catch_warnings(record=True) as caught,
                capture_optimizer(captured),
            ):
                warnings.simplefilter("always")
                params = fit(
                    xr.DataArray(data, dims=("time",), name="gf15"), dist="genextreme"
                )
            assert len(captured) == 1
            captured = captured[0]
            assert np.array_equal(
                params.values, original_row["parameters_c_loc_scale"]
            ), (c, n, draw, p, ratio)
            quantiles = []
            for probability in (0.9, 0.5) if p is None else (p,):
                value = float(
                    parametric_quantile(params, q=probability).values.ravel()[0]
                )
                assert value == cells[(c, n, probability, ratio)][draw]["estimate"]
                quantiles.append(
                    {"p": probability, "estimate": value, "exact_replay": True}
                )
            optimizer = captured["result"]
            vertices, values = optimizer["final_simplex"]
            simplex = [row["parameters"] for row in captured["evaluations"][:4]]
            initial_shape, start_keywords = xclim_stats._fit_start(data, "genextreme")
            expected_start = np.array(
                [initial_shape[0], start_keywords["loc"], start_keywords["scale"]]
            )
            assert np.array_equal(expected_start, captured["x0"])
            expected_simplex = np.tile(expected_start, (4, 1))
            for dimension in range(3):
                expected_simplex[dimension + 1, dimension] = (
                    1.05 * expected_start[dimension]
                    if expected_start[dimension] != 0
                    else 0.00025
                )
            assert np.array_equal(expected_simplex, simplex)
            case = {
                "trace_id": number,
                "selection": selection,
                "shape_c": c,
                "n": n,
                "draw": draw,
                "p": p,
                "ratio": ratio,
                "mu": original_row["mu"],
                "sample_min": data.min(),
                "sample_max": data.max(),
                "parameters": params.values,
                "quantiles": quantiles,
                "exact_parameter_replay": True,
                "xclim_start": expected_start,
                "first_four_evaluation_simplex": simplex,
                "optimizer_options_passed_unchanged": captured[
                    "options_passed_unchanged"
                ],
                "optimizer_result": optimizer,
                "final_max_coordinate_spread": np.max(abs(vertices[1:] - vertices[0])),
                "final_max_objective_spread": np.max(abs(values[1:] - values[0])),
                "objective_evaluations_recorded": len(captured["evaluations"]),
                "actual_penalized_final_objective": genextreme._penalized_nnlf(
                    params.values, data
                ),
                "actual_penalized_true_objective": genextreme._penalized_nnlf(
                    [c, original_row["mu"], 1.0], data
                ),
                "warnings": [
                    {"type": type(w.message).__name__, "message": str(w.message)}
                    for w in caught
                ],
            }
            assert len(captured["evaluations"]) == optimizer["nfev"]
            for evaluation_index, evaluation in enumerate(captured["evaluations"]):
                stream.write(
                    (
                        json.dumps(
                            plain(
                                {
                                    "trace_id": number,
                                    "evaluation": evaluation_index,
                                    **evaluation,
                                }
                            ),
                            allow_nan=False,
                        )
                        + "\n"
                    ).encode()
                )
            results.append(case)
            if (number + 1) % 30 == 0:
                print(
                    json.dumps(
                        {"stage": "traces", "completed": number + 1, "total": 186}
                    ),
                    flush=True,
                )
    write_json(
        output / "optimizer-traces.json",
        {
            "traces": len(results),
            "all_exact_replays": True,
            "seconds": time.perf_counter() - started,
            "settings_changed": False,
            "source_status_meaning": {
                "0": "success",
                "1": "maximum function evaluations",
                "2": "maximum iterations",
            },
            "cases": results,
        },
    )


def main() -> None:
    """Run the approved bounded investigation with immutable-input checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "protocol.json", protocol())
    before = verify_original()
    paths = [
        Path(__file__),
        Path(inspect.getfile(optimize_source)),
        Path(inspect.getfile(xclim_stats)),
        Path(inspect.getfile(type(genextreme))),
        ROOT / "blueearth_cst/experiment/metric_registry.py",
    ]
    source = {str(path): sha(path) for path in paths}
    write_json(
        args.output / "provenance.json",
        {
            "utc": datetime.now(timezone.utc).isoformat(),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "sources": source,
            "original_evidence": before,
            "environment_source": str(OLD / "results/provenance.json"),
            "environment_source_sha256": sha(OLD / "results/provenance.json"),
        },
    )
    write_json(args.output / "controls.json", controls())
    cells, arrays = load_retained()
    analyze(args.output, cells, arrays)
    trace(args.output, cells, arrays)
    assert source == {str(path): sha(path) for path in paths}
    assert before == verify_original()
    write_json(
        args.output / "completion.json",
        {
            "status": "complete",
            "original_evidence_unchanged": True,
            "diagnostic_sources_unchanged": True,
            "retained_fits_diagnosed": 132000,
            "traced_fits": 186,
            "all_traces_exact": True,
            "new_qualification_or_method": False,
        },
    )
    print(
        "Investigation complete; all original evidence unchanged; no qualification decision altered.",
        flush=True,
    )


if __name__ == "__main__":
    main()
