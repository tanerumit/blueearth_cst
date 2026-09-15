"""Compare two approved diagnostic candidates on the fixed186 GF15 cases.

A exposes optimizer failure with the original numerical path. B additionally
normalizes by sample mean and population standard deviation, then maps back.
Neither candidate changes production or qualifies a1000-draw benchmark cell.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import runpy
import subprocess
import sys
import time
import warnings
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr
from scipy.stats import genextreme
from xclim.indices.stats import fit, parametric_quantile

ROOT = Path(__file__).resolve().parents[6]
HOME = ROOT / "dev/milestones/r12/implementation/evidence"
ORIGINAL = HOME / "gf15"
INVESTIGATION = HOME / "gf15-investigation"
sys.dont_write_bytecode = True
HELPERS = runpy.run_path(
    str(INVESTIGATION / "investigate-estimator.py"),
    run_name="readonly_investigation_helpers",
)
PLAIN = HELPERS["plain"]
CAPTURE = HELPERS["capture_optimizer"]
ATOL = 1e-6


def sha(path: Path) -> str:
    """Hash exact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Retain explicit nonfinite values and LF JSON."""
    path.write_text(
        json.dumps(PLAIN(value), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def verify_inputs() -> dict[str, Any]:
    """Verify both complete immutable inventories, including absence of extras."""
    result = {}
    for root in (ORIGINAL, INVESTIGATION):
        inventory = json.loads((root / "artifact-inventory.json").read_text())
        expected = {item["path"] for item in inventory["files"]}
        actual = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path != root / "artifact-inventory.json"
        }
        assert expected == actual, root
        for item in inventory["files"]:
            path = root / item["path"]
            assert (
                path.stat().st_size == item["bytes"] and sha(path) == item["sha256"]
            ), path
        result[root.name] = {
            "inventory_sha256": sha(root / "artifact-inventory.json"),
            "files_verified": len(expected),
            "no_extra_files": True,
        }
    return result


def refusal_reasons(
    status: int | None, success: bool, params: Any, quantiles: list[float], failure: Any
) -> list[str]:
    """Apply explicit status handling plus the original finite-value checks."""
    reasons = []
    if failure is not None:
        reasons.append("estimator_exception")
    if status != 0 or not success:
        reasons.append(f"optimizer_status_{status}")
    if params is None or not np.isfinite(params).all() or params[2] <= 0:
        reasons.append("invalid_parameters_or_scale")
    if not quantiles or not np.isfinite(quantiles).all():
        reasons.append("invalid_quantile")
    return reasons


def pair_result(before: dict, after: dict, probability: float) -> dict[str, Any]:
    """Separate numerical evidence from both-refused and validity-changed pairs."""
    base = next(item for item in before["quantiles"] if item["p"] == probability)
    translated = next(item for item in after["quantiles"] if item["p"] == probability)
    delta = (
        translated["scale_error"] - base["scale_error"]
        if translated["scale_error"] is not None and base["scale_error"] is not None
        else None
    )
    both = before["accepted"] and after["accepted"]
    same = before["accepted"] == after["accepted"]
    outcome = (
        ("passed" if delta is not None and abs(delta) <= ATOL else "failed_numeric")
        if both
        else ("both_refused_no_numerical_proof" if same else "validity_changed")
    )
    return {
        "raw_paired_scale_error_delta": delta,
        "raw_within_existing_atol": delta is not None and abs(delta) <= ATOL,
        "both_accepted": both,
        "validity_same": same,
        "outcome": outcome,
        "accepted_pair_within_existing_atol": outcome == "passed" if both else None,
    }


def controls() -> dict[str, Any]:
    """Use toy and analytical controls only; add no candidate GEV fits."""
    optimizer = HELPERS["controls"]()
    params = np.array([0.1, 0.25, 0.7])
    assert not refusal_reasons(0, True, params, [1.0], None)
    assert refusal_reasons(1, False, params, [1.0], None) == ["optimizer_status_1"]
    assert "invalid_parameters_or_scale" in refusal_reasons(
        0, True, [0, 0, 0], [1.0], None
    )
    data = np.array([-2.0, 0.0, 1.0, 3.0])
    mean, scale = data.mean(), data.std(ddof=0)
    normalized = (data - mean) / scale
    mapped = params.copy()
    mapped[1] = mean + scale * params[1]
    mapped[2] *= scale
    likelihood_delta = -genextreme.logpdf(data, *mapped).sum() - (
        -genextreme.logpdf(normalized, *params).sum() + len(data) * np.log(scale)
    )
    assert abs(likelihood_delta) < 1e-12
    p = 0.9
    mapping_delta = (
        mean + scale * genextreme.isf(1 - p, *params) - genextreme.isf(1 - p, *mapped)
    )
    assert abs(mapping_delta) < 1e-12
    before = {"accepted": True, "quantiles": [{"p": p, "scale_error": 0.0}]}
    good = {"accepted": True, "quantiles": [{"p": p, "scale_error": 0.0}]}
    bad = {"accepted": True, "quantiles": [{"p": p, "scale_error": 2e-6}]}
    assert pair_result(before, good, p)["outcome"] == "passed"
    assert pair_result(before, bad, p)["outcome"] == "failed_numeric"
    assert (
        pair_result({**before, "accepted": False}, {**good, "accepted": False}, p)[
            "outcome"
        ]
        == "both_refused_no_numerical_proof"
    )
    assert (
        pair_result(before, {**good, "accepted": False}, p)["outcome"]
        == "validity_changed"
    )
    return {
        "status": "passed",
        "additional_GEV_fits": 0,
        "optimizer_toy_controls": optimizer,
        "finite_failed_status_refused_without_losing_raw_values": True,
        "normalization_quantile_delta": mapping_delta,
        "normalization_likelihood_delta": likelihood_delta,
        "numeric_2e_minus6_perturbation_detected": True,
        "both_refused_not_counted_as_numerical_proof": True,
        "validity_change_detected": True,
    }


def fit_case(
    candidate: str, case: dict, sample: np.ndarray, original_rows: dict
) -> tuple[dict, list]:
    """Run one same-settings fit and retain raw results even when refused."""
    normalization_mean = float(sample.mean()) if candidate == "B" else 0.0
    normalization_scale = float(sample.std(ddof=0)) if candidate == "B" else 1.0
    assert (
        np.isfinite(sample).all()
        and np.isfinite(normalization_scale)
        and normalization_scale > 0
    )
    fit_input = (
        (sample - normalization_mean) / normalization_scale
        if candidate == "B"
        else sample
    )
    captured = []
    failure = None
    fitted = None
    normalized_params = mapped_params = None
    quantiles = []
    probabilities = (0.9, 0.5) if case["p"] is None else (case["p"],)
    with warnings.catch_warnings(record=True) as caught, CAPTURE(captured):
        warnings.simplefilter("always")
        try:
            fitted = fit(
                xr.DataArray(fit_input, dims=("time",), name="gf15"), dist="genextreme"
            )
            normalized_params = np.array(fitted.values)
            mapped_params = normalized_params.copy()
            if candidate == "B":
                mapped_params[1] = (
                    normalization_mean + normalization_scale * normalized_params[1]
                )
                mapped_params[2] = normalization_scale * normalized_params[2]
            for p in probabilities:
                normalized_q = float(parametric_quantile(fitted, q=p).values.ravel()[0])
                mapped_q = (
                    normalization_mean + normalization_scale * normalized_q
                    if candidate == "B"
                    else normalized_q
                )
                old = original_rows[(case["shape_c"], case["n"], p, case["ratio"])][
                    case["draw"]
                ]
                parameter_q = (
                    genextreme.isf(1 - p, *mapped_params)
                    if p > 0.5
                    else genextreme.ppf(p, *mapped_params)
                )
                quantiles.append(
                    {
                        "p": p,
                        "true_quantile": old["true_quantile"],
                        "original_estimate": old["estimate"],
                        "original_scale_error": old["scale_error"],
                        "normalized_estimate": normalized_q,
                        "estimate": mapped_q,
                        "scale_error": mapped_q - old["true_quantile"],
                        "relative_error": (mapped_q - old["true_quantile"])
                        / abs(case["ratio"])
                        if case["ratio"] not in (None, 0)
                        else None,
                        "mapped_parameter_quantile": parameter_q,
                        "quantile_mapping_roundoff_delta": mapped_q - parameter_q,
                    }
                )
        except Exception as error:
            failure = {"type": type(error).__name__, "message": str(error)}
    optimizer = captured[0]["result"] if captured else None
    if captured:
        assert len(captured) == 1
        assert (
            PLAIN(captured[0]["options_passed_unchanged"])
            == case["optimizer_options_passed_unchanged"]
        )
    status = None if optimizer is None else int(optimizer["status"])
    reasons = refusal_reasons(
        status,
        optimizer is not None and bool(optimizer["success"]),
        mapped_params,
        [item["estimate"] for item in quantiles],
        failure,
    )
    if len(quantiles) != len(probabilities):
        reasons.append("missing_requested_quantile")
        for p in probabilities:
            if not any(item["p"] == p for item in quantiles):
                old = original_rows[(case["shape_c"], case["n"], p, case["ratio"])][
                    case["draw"]
                ]
                quantiles.append(
                    {
                        "p": p,
                        "true_quantile": old["true_quantile"],
                        "original_estimate": old["estimate"],
                        "original_scale_error": old["scale_error"],
                        "estimate": None,
                        "scale_error": None,
                        "relative_error": None,
                    }
                )
    nll_fit = nll_physical = likelihood_delta = None
    bad_fit = bad_physical = None
    if normalized_params is not None:
        fit_logpdf = genextreme.logpdf(fit_input, *normalized_params)
        physical_logpdf = genextreme.logpdf(sample, *mapped_params)
        nll_fit, nll_physical = float(-fit_logpdf.sum()), float(-physical_logpdf.sum())
        bad_fit, bad_physical = (
            int((~np.isfinite(fit_logpdf)).sum()),
            int((~np.isfinite(physical_logpdf)).sum()),
        )
        with np.errstate(invalid="ignore"):
            likelihood_delta = nll_physical - (
                nll_fit + len(sample) * np.log(normalization_scale)
            )
    parity = None
    if candidate == "A":
        assert failure is None and np.array_equal(mapped_params, case["parameters"])
        assert status == case["optimizer_result"]["status"]
        assert all(item["estimate"] == item["original_estimate"] for item in quantiles)
        parity = True
    identity = {
        key: case[key]
        for key in ("trace_id", "selection", "shape_c", "n", "draw", "p", "ratio", "mu")
    }
    return {
        **identity,
        "candidate": candidate,
        "accepted": not reasons,
        "refusal_reasons": reasons,
        "estimator_exception": failure,
        "normalization_mean": normalization_mean,
        "normalization_population_std": normalization_scale,
        "normalization_applied": candidate == "B",
        "raw_normalized_parameters": normalized_params,
        "raw_physical_parameters": mapped_params,
        "quantiles": quantiles,
        "original_parameters": case["parameters"],
        "original_optimizer_status": case["optimizer_result"]["status"],
        "optimizer": optimizer,
        "optimizer_options_unchanged": None
        if not captured
        else captured[0]["options_passed_unchanged"],
        "warnings": [
            {"type": type(w.message).__name__, "message": str(w.message)}
            for w in caught
        ],
        "original_exact_parity": parity,
        "normalized_nll": nll_fit,
        "physical_nll": nll_physical,
        "likelihood_mapping_delta": likelihood_delta,
        "normalized_nonfinite_log_density_count": bad_fit,
        "physical_nonfinite_log_density_count": bad_physical,
        "likelihood_diagnostic_not_extra_refusal_rule": True,
    }, [] if not captured else captured[0]["evaluations"]


def error_summary(values: list[float]) -> dict:
    """Describe available values with explicit denominators, not qualification."""
    array = np.array(
        [value for value in values if value is not None and np.isfinite(value)]
    )
    return {
        "requested": len(values),
        "finite_denominator": len(array),
        "missing_or_nonfinite": len(values) - len(array),
        "median_signed": np.median(array) if len(array) else None,
        "median_absolute": np.median(abs(array)) if len(array) else None,
        "p90_absolute": np.quantile(abs(array), 0.9) if len(array) else None,
        "maximum_absolute": np.max(abs(array)) if len(array) else None,
    }


def summarize(output: Path, results: list[dict]) -> None:
    """Retain every applicable pair and raw/accepted-only descriptive stratum."""
    pairs = []
    summary = []
    strata = []
    for candidate in ("A", "B"):
        rows = [row for row in results if row["candidate"] == candidate]
        baseline = {
            (row["shape_c"], row["n"], row["draw"]): row
            for row in rows
            if row["ratio"] is None
        }
        for row in rows:
            if row["ratio"] is None:
                continue
            before = baseline[(row["shape_c"], row["n"], row["draw"])]
            pairs.append(
                {
                    key: row[key]
                    for key in (
                        "candidate",
                        "trace_id",
                        "selection",
                        "shape_c",
                        "n",
                        "draw",
                        "p",
                        "ratio",
                    )
                }
                | pair_result(before, row, row["p"])
            )
        selected_pairs = [pair for pair in pairs if pair["candidate"] == candidate]
        assert len(rows) == 186 and len(selected_pairs) == 147
        for selection in ("predetermined", "witness"):
            selected = [row for row in rows if row["selection"] == selection]
            selection_pairs = [
                pair for pair in selected_pairs if pair["selection"] == selection
            ]
            summary.append(
                {
                    "candidate": candidate,
                    "selection": selection,
                    "attempted_fits": len(selected),
                    "accepted_fits": sum(row["accepted"] for row in selected),
                    "refused_fits": sum(not row["accepted"] for row in selected),
                    "attempted_quantiles": sum(
                        len(row["quantiles"]) for row in selected
                    ),
                    "accepted_quantiles": sum(
                        len(row["quantiles"]) for row in selected if row["accepted"]
                    ),
                    "optimizer_status_counts": {
                        str(status): sum(
                            row["optimizer"] is not None
                            and row["optimizer"]["status"] == status
                            for row in selected
                        )
                        for status in (0, 1, 2)
                    },
                    "estimator_exceptions": sum(
                        row["estimator_exception"] is not None for row in selected
                    ),
                    "warning_records": sum(len(row["warnings"]) for row in selected),
                    "attempted_pairs": len(selection_pairs),
                    "pair_outcomes": {
                        status: sum(
                            pair["outcome"] == status for pair in selection_pairs
                        )
                        for status in (
                            "passed",
                            "failed_numeric",
                            "both_refused_no_numerical_proof",
                            "validity_changed",
                        )
                    },
                    "raw_pair_delta": error_summary(
                        [
                            pair["raw_paired_scale_error_delta"]
                            for pair in selection_pairs
                        ]
                    ),
                    "both_accepted_pair_delta": error_summary(
                        [
                            pair["raw_paired_scale_error_delta"]
                            for pair in selection_pairs
                            if pair["both_accepted"]
                        ]
                    ),
                }
            )
        keys = sorted(
            {
                (row["selection"], row["shape_c"], row["n"], q["p"], row["ratio"])
                for row in rows
                for q in row["quantiles"]
            },
            key=lambda key: (*key[:-1], -1.0 if key[-1] is None else key[-1]),
        )
        for selection, c, n, p, ratio in keys:
            selected = [
                (row, q)
                for row in rows
                if (row["selection"], row["shape_c"], row["n"], row["ratio"])
                == (selection, c, n, ratio)
                for q in row["quantiles"]
                if q["p"] == p
            ]
            strata.append(
                {
                    "candidate": candidate,
                    "selection": selection,
                    "shape_c": c,
                    "n": n,
                    "p": p,
                    "ratio": ratio,
                    "raw_scale_error": error_summary(
                        [q["scale_error"] for _, q in selected]
                    ),
                    "accepted_only_scale_error": error_summary(
                        [q["scale_error"] for row, q in selected if row["accepted"]]
                    ),
                    "raw_relative_error": None
                    if ratio in (None, 0)
                    else error_summary([q["relative_error"] for _, q in selected]),
                    "accepted_only_relative_error": None
                    if ratio in (None, 0)
                    else error_summary(
                        [q["relative_error"] for row, q in selected if row["accepted"]]
                    ),
                    "note": "descriptive subset only, no 1000-draw-cell pass claim; relative error undefined at ratio zero",
                }
            )
    write_json(
        output / "paired-translations.json",
        {"attempted_pairs": 294, "original_atol": ATOL, "pairs": pairs},
    )
    write_json(
        output / "candidate-summary.json",
        {
            "status": "bounded_candidate_diagnostics_complete_no_qualification_claim",
            "fits": 372,
            "primary_scalar_quantiles": 450,
            "summary": summary,
            "descriptive_error_strata": strata,
        },
    )


def main() -> None:
    """Run precisely the approved two-candidate study and preserve old evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    before = verify_inputs()
    old_provenance = json.loads((ORIGINAL / "results/provenance.json").read_text())
    sources = {item["path"]: item["sha256"] for item in old_provenance["sources"]}
    for name, expected in sources.items():
        assert sha(Path(name)) == expected, name
    sources[str(Path(__file__).resolve())] = sha(Path(__file__))
    sources[str(INVESTIGATION / "investigate-estimator.py")] = sha(
        INVESTIGATION / "investigate-estimator.py"
    )
    cases = json.loads((INVESTIGATION / "results/optimizer-traces.json").read_text())[
        "cases"
    ]
    assert len(cases) == 186 and [case["trace_id"] for case in cases] == list(
        range(186)
    )
    write_json(
        args.output / "protocol.json",
        {
            "approval": "Owner explicitly approved status-only plus normalization candidates on the same186 cases, production unchanged",
            "candidates": {
                "A": "original input/path/defaults plus explicit optimizer-status refusal",
                "B": "z=(x-sample_mean)/sample_population_std(ddof0), same xclim scalar GEV fit/current optimizer defaults; backtransform parameters and scalar quantiles; same explicit status refusal",
            },
            "candidate_fits": 372,
            "primary_scalar_quantiles": 450,
            "pairs_per_candidate": 147,
            "additional_GEV_control_fits": 0,
            "selections": "exact186 prior trace IDs:180 predetermined plus6 purposive extreme witnesses; no new draws",
            "original_criteria": json.loads(
                (ORIGINAL / "results/criteria.json").read_text()
            ),
            "acceptance": "status0 AND success AND original finite-parameters/positive-scale/finite-quantile checks; rejected raw outputs retained; no fallback",
            "paired_denominators": "all attempted, both-accepted, both-refused and validity-changed kept separately; both-refused is not numerical equivalence proof",
            "likelihood": "diagnostic mapped likelihood and quantile consistency retained; not a silently added refusal criterion",
            "no_full_matrix_or_cell_qualification": True,
            "no_solver_setting_changes": True,
        },
    )
    write_json(
        args.output / "provenance.json",
        {
            "utc": datetime.now(timezone.utc).isoformat(),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "input_inventories": before,
            "sources": sources,
            "python": sys.version,
            "versions": {
                name: version(name)
                for name in ("numpy", "scipy", "xclim", "xarray", "pandas")
            },
            "case_source_sha256": sha(INVESTIGATION / "results/optimizer-traces.json"),
            "bytecode_writes_disabled": True,
        },
    )
    write_json(args.output / "controls.json", controls())
    original_rows, arrays = HELPERS["load_retained"]()
    results = []
    started = time.perf_counter()
    with (
        (args.output / "optimizer-evaluations.jsonl.gz").open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream,
    ):
        for candidate in ("A", "B"):
            for case in cases:
                sample = arrays[(case["shape_c"], case["n"])][case["draw"]] + case["mu"]
                record, evaluations = fit_case(candidate, case, sample, original_rows)
                results.append(record)
                for number, evaluation in enumerate(evaluations):
                    stream.write(
                        (
                            json.dumps(
                                PLAIN(
                                    {
                                        "candidate": candidate,
                                        "trace_id": case["trace_id"],
                                        "evaluation": number,
                                        **evaluation,
                                    }
                                ),
                                allow_nan=False,
                            )
                            + "\n"
                        ).encode()
                    )
            print(
                json.dumps(
                    {
                        "candidate": candidate,
                        "completed_fits": 186,
                        "accepted": sum(
                            row["accepted"]
                            for row in results
                            if row["candidate"] == candidate
                        ),
                    }
                ),
                flush=True,
            )
    write_json(args.output / "candidate-results.json", {"cases": results})
    summarize(args.output, results)
    assert before == verify_inputs()
    assert sources == {name: sha(Path(name)) for name in sources}
    write_json(
        args.output / "completion.json",
        {
            "status": "complete",
            "candidate_fits": 372,
            "primary_scalar_quantiles": 450,
            "seconds": time.perf_counter() - started,
            "original_evidence_and_sources_unchanged": True,
            "A_all_raw_parity_exact": True,
            "qualification_claim": False,
        },
    )
    print(
        "Candidate study complete; old evidence unchanged; no qualification claimed.",
        flush=True,
    )


if __name__ == "__main__":
    main()
