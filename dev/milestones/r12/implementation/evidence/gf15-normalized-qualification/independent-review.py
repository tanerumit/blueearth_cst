"""Independently audit full GF15 B records without importing fitting helpers."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def number(value: object) -> float | None:
    """Decode explicit nonfinite JSON diagnostics for arithmetic only."""
    return None if value is None else float(value)


def same(actual: object, expected: object) -> None:
    """Compare scalar arithmetic with a tight audit-only rounding allowance."""
    if expected is None:
        assert actual is None, (actual, expected)
        return
    a, b = number(actual), number(expected)
    assert a is not None and b is not None
    assert (
        (math.isnan(a) and math.isnan(b))
        or a == b
        or math.isclose(a, b, rel_tol=2e-14, abs_tol=1e-14)
    ), (actual, expected)


def percentile(values: list[float], probability: float) -> float:
    """Compute a linear order statistic using standard-library arithmetic."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summary(values: list[float | None]) -> dict:
    """Keep attempted and finite summary denominators distinct."""
    finite = [value for value in values if value is not None and math.isfinite(value)]
    absolute = [abs(value) for value in finite]
    return {
        "requested": len(values),
        "finite_denominator": len(finite),
        "missing_or_nonfinite": len(values) - len(finite),
        "median_signed": percentile(finite, 0.5) if finite else None,
        "median_absolute": percentile(absolute, 0.5) if finite else None,
        "p90_absolute": percentile(absolute, 0.9) if finite else None,
        "maximum_absolute": max(absolute) if finite else None,
    }


def controls() -> None:
    """Demonstrate order statistics, nonfinite counting and mismatch detection."""
    same(percentile([0.0, 1.0, 10.0], 0.9), 8.2)
    result = summary([None, math.inf, math.nan, -2.0, 0.0, 2.0])
    assert result["requested"] == 6 and result["finite_denominator"] == 3
    assert result["median_signed"] == 0 and result["p90_absolute"] == 2
    try:
        same(0.0, 2e-6)
    except AssertionError:
        return
    raise AssertionError("Independent comparison failed to detect injected mismatch")


def audit(results: Path) -> dict:
    """Recompute every scalar error, pair outcome and scientific cell decision."""
    controls()
    evidence = Path(__file__).resolve().parent.parent
    for name in ("gf15", "gf15-investigation", "gf15-candidates"):
        root = evidence / name
        inventory = json.loads((root / "artifact-inventory.json").read_text())
        expected = {entry["path"] for entry in inventory["files"]}
        assert expected == {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path != root / "artifact-inventory.json"
        }
        for entry in inventory["files"]:
            raw = (root / entry["path"]).read_bytes()
            assert len(raw) == entry["bytes"]
            assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    criteria = json.loads((results / "criteria.json").read_text())
    assert criteria == json.loads((evidence / "gf15/results/criteria.json").read_text())
    cells = defaultdict(list)
    expected_pairs = {}
    statuses, outcomes = Counter(), Counter()
    identifiers = set()
    accepted_fits = quantiles = 0
    max_mapping_error = max_accepted_change = 0.0
    paths = sorted(results.glob("fits-*.jsonl.gz"))
    assert len(paths) == 240
    samples = {}
    for path in paths:
        baseline = {}
        count = 0
        receipt = json.loads(path.with_suffix("").with_suffix(".json").read_text())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"]
        assert receipt["fits"] == 550 and receipt["quantiles"] == 600
        original_path = (
            evidence / "gf15/results" / path.name.replace("fits-", "draws-", 1)
        )
        with gzip.open(original_path, "rt", encoding="utf-8") as stream:
            original = {
                (r["draw"], r["p"], r["ratio"]): r
                for r in (json.loads(line) for line in stream)
            }
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                count += 1
                fit_id = row["fit_id"]
                assert fit_id not in identifiers
                identifiers.add(fit_id)
                c, n, draw, p, rho = (
                    row[key] for key in ("shape_c", "n", "draw", "p", "ratio")
                )
                ci = criteria["shapes_scipy_c"].index(c)
                ni = criteria["usable_counts"].index(n)
                slot = (
                    0
                    if p is None
                    else 1
                    + criteria["probabilities"].index(p) * 5
                    + criteria["ratios_true_quantile_over_generating_scale"].index(rho)
                )
                assert fit_id == (ci * 4 + ni) * 11000 + draw * 11 + slot
                assert 0 <= draw < 1000
                if (ci, n) not in samples:
                    samples[(ci, n)] = np.load(
                        evidence / f"gf15/results/samples-c{ci}-n{n}.npy",
                        allow_pickle=False,
                    ).tolist()
                optimizer = row["optimizer"]
                status = optimizer["status"] if optimizer else None
                statuses[str(status)] += 1
                if optimizer:
                    assert row["evaluation_count_verified"] == optimizer["nfev"]
                physical = row["raw_physical_parameters"]
                estimates = [number(q["estimate"]) for q in row["quantiles"]]
                valid = (
                    optimizer is not None
                    and status == 0
                    and optimizer["success"]
                    and row["estimator_exception"] is None
                    and physical is not None
                    and all(math.isfinite(float(v)) for v in physical)
                    and float(physical[2]) > 0
                    and all(v is not None and math.isfinite(v) for v in estimates)
                    and len(estimates) == (2 if p is None else 1)
                )
                assert row["accepted"] == valid
                assert bool(row["refusal_reasons"]) != valid
                accepted_fits += valid
                normalized = row["raw_normalized_parameters"]
                mean, std = (
                    row["normalization_mean"],
                    row["normalization_population_std"],
                )
                assert std > 0 and math.isfinite(std) and math.isfinite(mean)
                physical_sample = [x + row["mu"] for x in samples[(ci, n)][draw]]
                reference_mean = math.fsum(physical_sample) / n
                reference_std = math.sqrt(
                    math.fsum((x - reference_mean) ** 2 for x in physical_sample) / n
                )
                same(mean, reference_mean)
                same(std, reference_std)
                if normalized is not None:
                    for actual, expected in zip(
                        physical,
                        [
                            normalized[0],
                            mean + std * float(normalized[1]),
                            std * float(normalized[2]),
                        ],
                        strict=True,
                    ):
                        same(actual, expected)
                assert [q["p"] for q in row["quantiles"]] == (
                    [0.9, 0.5] if p is None else [p]
                )
                for q in row["quantiles"]:
                    quantiles += 1
                    probability = q["p"]
                    old = original[(draw, probability, rho)]
                    assert q["original_estimate"] == old["estimate"]
                    assert q["original_scale_error"] == old["scale_error"]
                    assert row["original_parameters"] == old["parameters_c_loc_scale"]
                    loglog = math.log(-math.log(probability))
                    z = -math.expm1(c * loglog) / c if c else -loglog
                    same(q["true_quantile"], z if rho is None else rho)
                    same(row["mu"], 0.0 if rho is None else rho - z)
                    estimate = number(q["estimate"])
                    error = None if estimate is None else estimate - q["true_quantile"]
                    relative = (
                        None if rho in (None, 0) or error is None else error / abs(rho)
                    )
                    same(q["scale_error"], error)
                    same(q["relative_error"], relative)
                    if "normalized_estimate" in q:
                        mapped = mean + std * float(q["normalized_estimate"])
                        same(estimate, mapped)
                        if valid:
                            max_mapping_error = max(
                                max_mapping_error, abs(estimate - mapped)
                            )
                    if valid:
                        max_accepted_change = max(
                            max_accepted_change, abs(estimate - q["original_estimate"])
                        )
                    key = (c, n, probability, rho)
                    cells[key].append((valid, error, relative))
                    if rho is None:
                        baseline[(draw, probability)] = (valid, error)
                    else:
                        base_valid, base_error = baseline[(draw, probability)]
                        delta = (
                            None
                            if error is None or base_error is None
                            else error - base_error
                        )
                        outcome = (
                            (
                                "passed"
                                if delta is not None and abs(delta) <= 1e-6
                                else "failed_numeric"
                            )
                            if valid and base_valid
                            else (
                                "both_refused_no_numerical_proof"
                                if valid == base_valid
                                else "validity_changed"
                            )
                        )
                        expected_pairs[fit_id] = (
                            key,
                            outcome,
                            delta,
                            valid and base_valid,
                            valid == base_valid,
                        )
                        outcomes[outcome] += 1
        assert count == 550
    assert identifiers == set(range(132000)) and quantiles == 144000
    pair_counts = defaultdict(Counter)
    seen = set()
    max_accepted_pair_delta = 0.0
    with gzip.open(
        results / "paired-translations.jsonl.gz", "rt", encoding="utf-8"
    ) as stream:
        for line in stream:
            pair = json.loads(line)
            fit_id = pair["fit_id"]
            assert fit_id not in seen
            seen.add(fit_id)
            key, outcome, delta, both, same_validity = expected_pairs[fit_id]
            assert tuple(pair[k] for k in ("shape_c", "n", "p", "ratio")) == key
            assert pair["draw"] == (fit_id % 11000) // 11
            assert pair["outcome"] == outcome
            assert (
                pair["both_accepted"] == both and pair["validity_same"] == same_validity
            )
            same(pair["raw_paired_scale_error_delta"], delta)
            assert pair["accepted_pair_within_existing_atol"] == (
                outcome == "passed" if both else None
            )
            pair_counts[key][outcome] += 1
            if both:
                max_accepted_pair_delta = max(max_accepted_pair_delta, abs(delta))
    assert seen == set(expected_pairs) and len(seen) == 120000
    matrix = json.loads((results / "matrix-results.json").read_text())["cells"]
    assert len(matrix) == len(cells) == 144
    assert {
        tuple(cell[k] for k in ("shape_c", "n", "p", "ratio")) for cell in matrix
    } == set(cells)
    passes = Counter()
    for cell in matrix:
        key = tuple(cell[k] for k in ("shape_c", "n", "p", "ratio"))
        rows = cells[key]
        assert len(rows) == cell["attempted"] == 1000
        accepted = [r for r in rows if r[0]]
        assert len(accepted) == cell["accepted"] == 1000 - cell["refused"]
        same(cell["accepted_rate"], len(accepted) / 1000)
        for name, source, column in (
            ("raw_scale", rows, 1),
            ("accepted_scale", accepted, 1),
            ("raw_relative", rows, 2),
            ("accepted_relative", accepted, 2),
        ):
            expected = summary([r[column] for r in source])
            for field, value in expected.items():
                same(cell[name][field], value)
        rate_pass = len(accepted) >= 950
        scale = summary([r[1] for r in accepted])
        relative = summary([r[2] for r in accepted])
        limit = 0.5 if cell["p"] == 0.9 else 0.25
        scale_pass = (
            rate_pass
            and bool(accepted)
            and abs(scale["median_signed"]) <= 0.1
            and scale["p90_absolute"] <= limit
        )
        rho = cell["ratio"]
        relative_pass = (
            None
            if rho in (None, 0)
            else rate_pass
            and bool(accepted)
            and abs(relative["median_signed"]) <= 0.1
            and relative["p90_absolute"] <= limit
        )
        assert cell["valid_rate_pass"] == rate_pass and cell["scale_pass"] == scale_pass
        assert cell["relative_pass"] == relative_pass
        counts = pair_counts[key]
        assert cell["pair_outcomes"] == counts
        base_accepted = sum(r[0] for r in cells[(*key[:3], None)])
        translation_pass = (
            None
            if rho is None
            else rate_pass
            and base_accepted >= 950
            and counts["passed"] > 0
            and counts["failed_numeric"] == counts["validity_changed"] == 0
        )
        assert cell["translation_gate_pass"] == translation_pass
        if rho is None:
            passes["baseline_scale_passed"] += scale_pass
        if rho in (0.5, 2.0, 10.0):
            passes["eligible_scale_and_relative_passed"] += scale_pass and relative_pass
        if rho is not None:
            passes["translation_cells_passed"] += translation_pass
    retained = json.loads((results / "qualification-summary.json").read_text())
    for key, value in passes.items():
        assert retained[key] == value
    assert retained["optimizer_status_counts"] == statuses
    assert retained["totals"]["accepted_fits"] == accepted_fits
    qualified = (
        passes["baseline_scale_passed"] == 24
        and passes["eligible_scale_and_relative_passed"] == 72
        and passes["translation_cells_passed"] == 120
    )
    assert retained["qualification_passed"] == qualified
    return {
        "audit_passed": True,
        "qualification_passed": qualified,
        "fits": len(identifiers),
        "quantiles": quantiles,
        "pairs": len(seen),
        "cells": len(cells),
        "accepted_fits": accepted_fits,
        "optimizer_status_counts": statuses,
        "pair_outcomes": outcomes,
        "cell_passes": passes,
        "maximum_accepted_pair_delta": max_accepted_pair_delta,
        "maximum_accepted_affine_quantile_residual": max_mapping_error,
        "maximum_accepted_estimate_change_from_original": max_accepted_change,
        "prior_inventories_exact": True,
        "criteria_exact": True,
        "method": "Independent standard-library arithmetic and linear order statistics; no fitting/helper imports or additional fits",
    }


def main() -> None:
    """Write a new independent audit without changing the retained results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    result = audit(args.results)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
