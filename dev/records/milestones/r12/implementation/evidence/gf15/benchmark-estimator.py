"""Run the owner-approved R12 GF15 matrix without changing the estimator.

Commands: pilot measures cost and checks controls; run retains every draw;
summarize evaluates the locked criteria without fitting again. A completed
benchmark may fail scientific criteria while this harness exits successfully.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import inspect
import json
import os
import platform
import subprocess
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from importlib.metadata import distributions, version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import genextreme
from xclim.indices.stats import fit, parametric_quantile

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
SHAPES = (-0.2, 0.0, 0.2)  # SciPy c; extreme-value xi = -c.
COUNTS = (10, 18, 30, 60)
PROBABILITIES = (0.9, 0.5)
RATIOS = (0.0, 0.05, 0.5, 2.0, 10.0)
DRAWS = 1000
SEED = 20260912
ATOL = 1e-6


def write_json(path: Path, data: Any) -> None:
    """Write explicit JSON; undefined statistics are null, never NaN."""
    path.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def digest(path: Path) -> str:
    """Hash the exact retained bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analytic_ppf(probability: Any, shape: float) -> Any:
    """Independent closed-form inverse CDF in SciPy's shape convention."""
    log_t = np.log(-np.log(probability))
    return -log_t if shape == 0 else -np.expm1(shape * log_t) / shape


def samples(shape_index: int, count: int) -> np.ndarray:
    """Generate one schedule-independent base cell from an explicit PCG64 seed."""
    rng = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence([SEED, shape_index, count]))
    )
    uniform = rng.random((DRAWS, count))
    if not ((uniform > 0) & (uniform < 1)).all():
        raise ValueError("Uniform endpoint encountered; do not silently clip or redraw")
    return analytic_ppf(uniform, SHAPES[shape_index])


def fit_sample(
    sample: np.ndarray, probabilities: tuple[float, ...]
) -> list[dict[str, Any]]:
    """Use the production scalar xclim fit and quantile calls, with its checks.

    The baseline shares one deterministic fit for its two scalar quantile calls.
    Each translated sample is actually refitted. The ML path exposes parameters,
    not an optimizer success flag; valid here has exactly that bounded meaning.
    """
    params = None
    raw = None
    fit_error = None
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        try:
            if np.ptp(sample) == 0:
                raise ValueError("constant sample")
            params = fit(
                xr.DataArray(sample, dims=("time",), name="gf15"), dist="genextreme"
            )
            raw = np.asarray(params.values).ravel()
            if not np.isfinite(raw).all() or float(params.sel(dparams="scale")) <= 0:
                raise ValueError(f"invalid fitted parameters {raw.tolist()}")
        except Exception as error:
            fit_error = {"type": type(error).__name__, "message": str(error)}
        fit_warnings = [
            {"type": type(w.message).__name__, "message": str(w.message)}
            for w in captured
        ]
    result = []
    for probability in probabilities:
        value = None
        error_record = fit_error
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            if fit_error is None:
                try:
                    value = float(
                        parametric_quantile(params, q=probability).values.ravel()[0]
                    )
                    if not np.isfinite(value):
                        raise ValueError(f"non-finite quantile {value}")
                except Exception as error:
                    value = None
                    error_record = {"type": type(error).__name__, "message": str(error)}
        result.append(
            {
                "p": probability,
                "valid": error_record is None,
                "estimate": value,
                "parameters_c_loc_scale": None
                if raw is None
                else [float(v) if np.isfinite(v) else str(v) for v in raw],
                "failure": error_record,
                "warnings": fit_warnings
                + [
                    {"type": type(w.message).__name__, "message": str(w.message)}
                    for w in captured
                ],
            }
        )
    return result


def error_summary(values: list[float]) -> dict[str, Any]:
    """Summarize conditional valid-fit errors with NumPy's linear quantiles."""
    array = np.asarray(values, dtype=float)
    if len(array) == 0:
        return {
            "denominator": 0,
            "median_signed": None,
            "median_absolute": None,
            "p90_absolute": None,
        }
    return {
        "denominator": len(array),
        "median_signed": float(np.median(array)),
        "median_absolute": float(np.median(abs(array))),
        "p90_absolute": float(np.quantile(abs(array), 0.9, method="linear")),
    }


def compare_translation(
    baseline_valid: bool,
    translated_valid: bool,
    baseline_error: float | None,
    translated_error: float | None,
) -> dict[str, Any]:
    """Apply the approved paired error and classification checks to numbers."""
    same = baseline_valid == translated_valid
    delta = (
        translated_error - baseline_error
        if baseline_valid and translated_valid
        else None
    )
    return {
        "translation_validity_same": same,
        "paired_scale_error_delta": delta,
        "translation_pass": same and (delta is None or abs(delta) <= ATOL),
    }


def cell_result(
    rows: list[dict[str, Any]], p: float, ratio: float | None
) -> dict[str, Any]:
    """Evaluate every approved condition separately without pooling cells."""
    valid = [row for row in rows if row["valid"]]
    scale = error_summary([row["scale_error"] for row in valid])
    relative = (
        None
        if ratio in (None, 0)
        else error_summary([row["relative_error"] for row in valid])
    )
    limit = 0.5 if p == 0.9 else 0.25
    conditions = {
        "valid_rate_at_least_0.95": len(valid) / len(rows) >= 0.95,
        "absolute_median_scale_at_most_0.10": bool(valid)
        and abs(scale["median_signed"]) <= 0.10,
        "p90_absolute_scale_at_most_limit": bool(valid)
        and scale["p90_absolute"] <= limit,
    }
    relative_conditions = None
    if ratio in (0.5, 2.0, 10.0):
        relative_conditions = {
            "absolute_median_relative_at_most_0.10": bool(valid)
            and abs(relative["median_signed"]) <= 0.10,
            "p90_absolute_relative_at_most_limit": bool(valid)
            and relative["p90_absolute"] <= limit,
        }
    deviations = [row for row in rows if row.get("translation_pass") is False]
    return {
        "p": p,
        "ratio": ratio,
        "draws": len(rows),
        "valid": len(valid),
        "refused": len(rows) - len(valid),
        "valid_rate": len(valid) / len(rows),
        "scale": scale,
        "relative": relative,
        "relative_status": "not_applicable_standardized"
        if ratio is None
        else (
            "undefined_zero"
            if ratio == 0
            else ("diagnostic_near_zero" if ratio == 0.05 else "evaluated")
        ),
        "scale_conditions": conditions,
        "scale_pass": all(conditions.values()),
        "relative_conditions": relative_conditions,
        "scale_and_relative_pass": None
        if relative_conditions is None
        else all(conditions.values()) and all(relative_conditions.values()),
        "translation_comparisons": 0 if ratio is None else len(rows),
        "translation_failures": len(deviations),
        "translation_validity_changes": sum(
            row.get("translation_validity_same") is False for row in rows
        ),
        "translation_max_abs_error_delta": max(
            (
                abs(row["paired_scale_error_delta"])
                for row in rows
                if row.get("paired_scale_error_delta") is not None
            ),
            default=None,
        ),
        "qualified_pass_including_translation": None
        if relative_conditions is None
        else all(conditions.values())
        and all(relative_conditions.values())
        and not deviations,
    }


def controls() -> dict[str, Any]:
    """Check analytical truth, real reducer parity and deliberately bad diagnostics."""
    from blueearth_cst.experiment.metric_registry import declarations, reduce_bundle
    from blueearth_cst.experiment.response_series import ResponseSeries

    probabilities = np.array([0.001, 0.1, 0.5, 0.9, 0.999])
    formula_errors = []
    for shape in SHAPES:
        delta = float(
            np.max(
                abs(
                    analytic_ppf(probabilities, shape)
                    - genextreme.ppf(probabilities, shape)
                )
            )
        )
        assert delta < 1e-12
        formula_errors.append({"scipy_c": shape, "maximum_absolute_delta": delta})
    blocks = np.array([-2, -1.5, -1, -0.5, 0, 0.5, 1, 2, 3.5, 6], dtype=float)
    time_axis = pd.date_range("2000-01-01", "2009-12-31", freq="D")
    parity = []
    for declaration in [item for item in declarations(["q"]) if item.grain == "bundle"]:
        maximum = declaration.statistic == "return_level_max"
        daily = np.full(len(time_axis), -100.0 if maximum else 100.0)
        for i, year in enumerate(range(2000, 2010)):
            index = (
                (time_axis.year == year) & (time_axis.month == 7) & (time_axis.day <= 7)
            )
            daily[index] = blocks[i]
        response = ResponseSeries(
            "01",
            "q",
            "gf15",
            0,
            time_axis,
            "standard",
            timedelta(days=1),
            "interval_end",
            "m3 s-1",
            daily,
            np.isnan(daily),
        )
        actual, evidence = reduce_bundle(
            declaration, [response], expected_run_ids=["01"], anchor="YE-DEC"
        )
        p = 0.9 if maximum else 0.5
        diagnostic = fit_sample(blocks, (p,))[0]
        assert diagnostic["valid"] and actual["gf15"] == diagnostic["estimate"]
        assert list(evidence[0].parameters) == diagnostic["parameters_c_loc_scale"]
        parity.append(
            {
                "metric": declaration.name,
                "estimate": diagnostic["estimate"],
                "parameters": diagnostic["parameters_c_loc_scale"],
                "total_blocks": evidence[0].total,
                "exact": True,
            }
        )
    assert not fit_sample(np.ones(10), (0.9,))[0]["valid"]
    good = [
        {
            "valid": True,
            "scale_error": 0.0,
            "relative_error": 0.0,
            "translation_pass": True,
        }
        for _ in range(1000)
    ]
    assert cell_result(good, 0.5, 0.5)["qualified_pass_including_translation"]
    shifted = [{**row, "scale_error": 1.0, "relative_error": 2.0} for row in good]
    assert not cell_result(shifted, 0.5, 0.5)["scale_and_relative_pass"]
    refused = [{**row, "valid": i >= 51} for i, row in enumerate(good)]
    assert not cell_result(refused, 0.5, 0.5)["scale_conditions"][
        "valid_rate_at_least_0.95"
    ]
    assert cell_result(good, 0.5, 0)["relative"] is None
    assert compare_translation(True, True, 0.0, 0.0)["translation_pass"]
    assert compare_translation(True, True, 0.0, ATOL)["translation_pass"]
    assert not compare_translation(True, False, 0.0, None)["translation_pass"]
    changed = [{**row, **compare_translation(True, True, 0.0, 2e-6)} for row in good]
    assert cell_result(changed, 0.5, 0.5)["translation_failures"] == 1000
    return {
        "status": "passed",
        "analytic_vs_scipy": formula_errors,
        "production_reduce_bundle_exact_parity": parity,
        "discrimination": [
            "constant sample refusal",
            "perfect synthetic errors pass",
            "+1 scale error fails",
            "51/1000 refusals fail",
            "zero relative error is undefined",
            "2e-6 paired perturbation retained as 1000 translation failures",
        ],
        "optimizer_flag": "not exposed by installed xclim ML/dist.fit path; parameter validity is not global-optimum certification",
    }


def provenance() -> dict[str, Any]:
    """Bind approved criteria, production sources and installed estimator files."""
    import scipy.optimize._optimize as optimize_module
    import scipy.stats._distn_infrastructure as infrastructure
    import xclim.indices.stats as stats_module

    paths = [
        Path(__file__),
        ROOT / "blueearth_cst/experiment/metric_registry.py",
        ROOT / "blueearth_cst/experiment/response_series.py",
        ROOT / "blueearth_cst/shared/metrics_definition.py",
        ROOT / "blueearth_cst/shared/indicator_tables.py",
        ROOT / "pixi.lock",
        ROOT / "pixi.toml",
        ROOT / "dev/milestones/r12/wf3-simulation-identity-design.md",
        ROOT
        / "dev/milestones/r12/implementation/evidence/p3/scientific-review-preparation.md",
        Path(inspect.getfile(stats_module)),
        Path(inspect.getfile(type(genextreme))),
        Path(inspect.getfile(infrastructure)),
        Path(inspect.getfile(optimize_module)),
    ]
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "sources": [{"path": str(path), "sha256": digest(path)} for path in paths],
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "versions": {
            name: version(name)
            for name in ("numpy", "scipy", "xclim", "xarray", "pandas")
        },
        "installed_distributions": sorted(
            [
                {"name": item.metadata["Name"], "version": item.version}
                for item in distributions()
            ],
            key=lambda item: item["name"].lower(),
        ),
        "thread_environment": {
            key: os.environ.get(key)
            for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
        },
    }


def criteria() -> dict[str, Any]:
    """Pin the approved matrix and exact decision thresholds before execution."""
    return {
        "approval": "Owner approved exact section 7.5 / P3 scientific-review-preparation criteria on 2026-09-12 before execution; coordinator recorded Master Gate 2.",
        "shapes_scipy_c": SHAPES,
        "extreme_value_shape_xi": "xi=-c",
        "usable_counts": COUNTS,
        "probabilities": PROBABILITIES,
        "ratios_true_quantile_over_generating_scale": RATIOS,
        "draws_per_base_cell": DRAWS,
        "base_cells": 12,
        "total_fits": 132000,
        "total_quantile_rows": 144000,
        "rng": "numpy.Generator(PCG64(SeedSequence([20260912, shape_index, count])))",
        "master_seed": SEED,
        "quantile_formula": "z_p=-expm1(c*log(-log(p)))/c; c=0: -log(-log(p))",
        "generating_scale": 1.0,
        "standardized_location": 0.0,
        "translated_location": "rho-z_p",
        "sample_generation": "inverse CDF of (0,1) PCG64 uniforms; no clipping/truncation/redrawing",
        "valid_rate_min": 0.95,
        "median_scale_abs_max": 0.10,
        "p90_abs_scale_max": {"0.9": 0.50, "0.5": 0.25},
        "translation_paired_abs_max": ATOL,
        "translation_validity_unchanged": True,
        "relative_qualified_ratios": [0.5, 2.0, 10.0],
        "median_relative_abs_max": 0.10,
        "p90_abs_relative_max": {"0.9": 0.50, "0.5": 0.25},
        "quantile_summary_method": "numpy quantile method=linear; summaries conditional on valid fits; refusals/full 1000 denominator",
        "zero_relative": "undefined; null, never epsilon-divided",
        "low_level_meaning": "p=.5: median of annual seven-day minima; IID block fixtures do not simulate block extraction, dependence or real discharge",
        "estimator": "unchanged xclim.indices.stats.fit(DataArray(sample,dims=time,name=gf15),dist=genextreme); separate scalar parametric_quantile(p=.9) and (p=.5); production finite parameters/positive scale/finite quantile/constant-sample checks",
        "scientific_claim_boundary": "tested IID stationary GEV cells only; does not qualify screening floor/ratio or observed bundles; failure returns to owner; no retuning",
    }


def chunk(task: tuple[int, int, int, int, str]) -> dict[str, Any]:
    """Fit one deterministic fifty-draw chunk; retain every row and refusal."""
    shape_index, count, start, stop, output = task
    shape = SHAPES[shape_index]
    base = samples(shape_index, count)
    path = Path(output) / f"draws-c{shape_index}-n{count}-{start:04d}.jsonl.gz"
    begun = time.perf_counter()
    row_count = 0
    with (
        path.open("wb") as raw_file,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw_file, mtime=0) as compressed,
    ):
        for draw in range(start, stop):
            baseline = fit_sample(base[draw], PROBABILITIES)
            for record in baseline:
                p = record["p"]
                truth = float(analytic_ppf(p, shape))
                base_error = record["estimate"] - truth if record["valid"] else None
                identity = {
                    "shape_c": shape,
                    "shape_index": shape_index,
                    "n": count,
                    "draw": draw,
                    "p": p,
                }
                row = {
                    **identity,
                    **record,
                    "ratio": None,
                    "mu": 0.0,
                    "sigma": 1.0,
                    "true_quantile": truth,
                    "scale_error": base_error,
                    "relative_error": None,
                }
                compressed.write((json.dumps(row, allow_nan=False) + "\n").encode())
                row_count += 1
                for ratio in RATIOS:
                    mu = ratio - truth
                    translated = fit_sample(base[draw] + mu, (p,))[0]
                    error = (
                        translated["estimate"] - ratio if translated["valid"] else None
                    )
                    row = {
                        **identity,
                        **translated,
                        "ratio": ratio,
                        "mu": mu,
                        "sigma": 1.0,
                        "true_quantile": ratio,
                        "scale_error": error,
                        "relative_error": error / abs(ratio)
                        if error is not None and ratio != 0
                        else None,
                        **compare_translation(
                            record["valid"], translated["valid"], base_error, error
                        ),
                    }
                    compressed.write((json.dumps(row, allow_nan=False) + "\n").encode())
                    row_count += 1
    return {
        "file": path.name,
        "sha256": digest(path),
        "rows": row_count,
        "fits": (stop - start) * 11,
        "seconds": time.perf_counter() - begun,
    }


def summarize(output: Path) -> None:
    """Read every retained row, verify complete coverage and evaluate all cells."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    failures, warnings_rows, deviations = [], [], []
    for path in sorted(output.glob("draws-*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                groups.setdefault(
                    (row["shape_c"], row["n"], row["p"], row["ratio"]), []
                ).append(row)
                if not row["valid"]:
                    failures.append(row)
                if row["warnings"]:
                    warnings_rows.append(row)
                if row.get("translation_pass") is False:
                    deviations.append(row)
    assert len(groups) == 144
    results = []
    for shape in SHAPES:
        for count in COUNTS:
            for p in PROBABILITIES:
                for ratio in (None, *RATIOS):
                    rows = groups[(shape, count, p, ratio)]
                    assert len(rows) == DRAWS and sorted(
                        row["draw"] for row in rows
                    ) == list(range(DRAWS))
                    results.append(
                        {"shape_c": shape, "n": count, **cell_result(rows, p, ratio)}
                    )
    for name, rows in (
        ("fit-failures", failures),
        ("fit-warnings", warnings_rows),
        ("translation-deviations", deviations),
    ):
        with (
            (output / f"{name}.jsonl.gz").open("wb") as raw_file,
            gzip.GzipFile(
                filename="", mode="wb", fileobj=raw_file, mtime=0
            ) as compressed,
        ):
            for row in rows:
                compressed.write((json.dumps(row, allow_nan=False) + "\n").encode())
    baseline = [cell for cell in results if cell["ratio"] is None]
    qualified = [cell for cell in results if cell["ratio"] in (0.5, 2, 10)]
    passed = (
        all(cell["scale_pass"] for cell in baseline)
        and all(cell["qualified_pass_including_translation"] for cell in qualified)
        and not deviations
    )
    write_json(
        output / "matrix-results.json",
        {
            "status": "passed_bounded_estimator_matrix"
            if passed
            else "failed_owner_method_ruling_required",
            "all_cells_complete": True,
            "cell_count": len(results),
            "quantile_rows": sum(len(rows) for rows in groups.values()),
            "baseline_scale_pass_count": sum(cell["scale_pass"] for cell in baseline),
            "baseline_scale_cell_count": len(baseline),
            "qualified_pass_count_including_translation": sum(
                cell["qualified_pass_including_translation"] for cell in qualified
            ),
            "qualified_cell_count": len(qualified),
            "refused_quantile_rows": len(failures),
            "warning_quantile_rows": len(warnings_rows),
            "translation_deviation_count": len(deviations),
            "cells": results,
        },
    )
    pd.json_normalize(results).to_csv(
        output / "matrix-results.csv", index=False, lineterminator="\n"
    )
    write_json(
        output / "evidence-inventory.json",
        {
            "files": [
                {
                    "path": path.name,
                    "sha256": digest(path),
                    "bytes": path.stat().st_size,
                }
                for path in sorted(output.iterdir())
                if path.is_file() and path.name != "evidence-inventory.json"
            ]
        },
    )
    print(
        json.dumps(
            {
                "status": "passed" if passed else "failed_owner_method_ruling_required",
                "baseline_scale_pass": sum(cell["scale_pass"] for cell in baseline),
                "translation_deviations": len(deviations),
            }
        ),
        flush=True,
    )


def main() -> None:
    """Execute a cost pilot, the full fixed matrix, or a read-only reevaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pilot", "run", "summarize"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.command == "summarize":
        summarize(args.output)
        return
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "criteria.json", criteria())
    write_json(args.output / "provenance.json", provenance())
    write_json(args.output / "controls.json", controls())
    if args.command == "pilot":
        timings = []
        for shape_index in range(3):
            for count in COUNTS:
                sample = samples(shape_index, count)[0]
                started = time.perf_counter()
                fit_sample(sample, PROBABILITIES)
                for p in PROBABILITIES:
                    for ratio in RATIOS:
                        fit_sample(
                            sample + ratio - analytic_ppf(p, SHAPES[shape_index]), (p,)
                        )
                timings.append(
                    {
                        "shape_c": SHAPES[shape_index],
                        "n": count,
                        "fits": 11,
                        "seconds": time.perf_counter() - started,
                    }
                )
        seconds = sum(item["seconds"] for item in timings)
        write_json(
            args.output / "timing.json",
            {
                "pilot": "draw zero only from each approved base cell; timing only, not matrix acceptance",
                "cells": timings,
                "fits": 132,
                "seconds": seconds,
                "estimated_serial_hours": seconds * 1000 / 3600,
                "ideal_workers_hours": seconds * 1000 / 3600 / args.workers,
                "workers": args.workers,
            },
        )
        print((args.output / "timing.json").read_text(), flush=True)
        return
    for shape_index in range(3):
        for count in COUNTS:
            np.save(
                args.output / f"samples-c{shape_index}-n{count}.npy",
                samples(shape_index, count),
                allow_pickle=False,
            )
    tasks = [
        (shape_index, count, start, start + 50, str(args.output))
        for shape_index in range(3)
        for count in COUNTS
        for start in range(0, DRAWS, 50)
    ]
    started = time.perf_counter()
    completed = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(chunk, task) for task in tasks]
        for future in as_completed(futures):
            result = future.result()
            completed.append(result)
            write_json(
                args.output / "execution-progress.json",
                {
                    "completed_chunks": len(completed),
                    "total_chunks": len(tasks),
                    "workers": args.workers,
                    "elapsed_seconds": time.perf_counter() - started,
                    "chunks": sorted(completed, key=lambda item: item["file"]),
                },
            )
            print(
                json.dumps(
                    {"completed": len(completed), "total": len(tasks), **result}
                ),
                flush=True,
            )
    before = json.loads((args.output / "provenance.json").read_text())
    for item in before["sources"]:
        assert digest(Path(item["path"])) == item["sha256"], item["path"]
    write_json(
        args.output / "execution-completion.json",
        {
            "status": "complete",
            "workers": args.workers,
            "fits": sum(item["fits"] for item in completed),
            "rows": sum(item["rows"] for item in completed),
            "elapsed_seconds": time.perf_counter() - started,
            "source_hashes_unchanged": True,
        },
    )
    summarize(args.output)


if __name__ == "__main__":
    main()
