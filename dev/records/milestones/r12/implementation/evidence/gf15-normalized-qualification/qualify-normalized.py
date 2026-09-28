"""Qualify approved candidate B on the immutable original GF15 sample matrix.

The committed candidate helper owns every numerical operation and refusal rule.
This runner schedules fixed chunks, retains every outcome, and applies the
unchanged criteria. Objective histories are not retained for this full matrix.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import runpy
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
HOME = HERE.parent
OLD = HOME / "gf15"
CANDIDATES = HOME / "gf15-candidates"
HELP = runpy.run_path(str(CANDIDATES / "compare-candidates.py"), run_name="readonly_B")
PLAIN = HELP["PLAIN"]
CRITERIA = json.loads((OLD / "results/criteria.json").read_text())
TRACES = json.loads(
    (HOME / "gf15-investigation/results/optimizer-traces.json").read_text()
)["cases"]
OPTIONS = TRACES[0]["optimizer_options_passed_unchanged"]
assert all(row["optimizer_options_passed_unchanged"] == OPTIONS for row in TRACES)


def sha(path: Path) -> str:
    """Hash exact retained bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def gzip_writer(path: Path):
    """Write reproducible gzip bytes without file name or timestamp metadata."""
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as stream:
                yield stream


def numeric_errors(row: dict) -> dict:
    """Decode explicit nonfinite error tokens for arithmetic, preserving raw rows."""
    return row | {
        "quantiles": [
            q
            | {
                key: float(q[key]) if q[key] is not None else None
                for key in ("scale_error", "relative_error")
            }
            for q in row["quantiles"]
        ]
    }


def write_json(path: Path, value: object) -> None:
    """Write explicit nonfinite representations and LF newlines."""
    path.write_text(
        json.dumps(PLAIN(value), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_inputs() -> dict:
    """Check all three complete predecessor inventories and installed sources."""
    inputs = HELP["verify_inputs"]()
    inventory = json.loads((CANDIDATES / "artifact-inventory.json").read_text())
    actual = {
        p.relative_to(CANDIDATES).as_posix()
        for p in CANDIDATES.rglob("*")
        if p.is_file() and p.name != "artifact-inventory.json"
    }
    assert actual == {row["path"] for row in inventory["files"]}
    for row in inventory["files"]:
        path = CANDIDATES / row["path"]
        assert sha(path) == row["sha256"] and path.stat().st_size == row["bytes"], path
    inputs[CANDIDATES.name] = {
        "inventory_sha256": sha(CANDIDATES / "artifact-inventory.json"),
        "files_verified": len(actual),
        "no_extra_files": True,
    }
    previous = json.loads((CANDIDATES / "results/provenance.json").read_text())
    for name, expected in previous["sources"].items():
        assert sha(Path(name)) == expected, name
    return {
        "inputs": inputs,
        "sources": previous["sources"]
        | {str(Path(__file__).resolve()): sha(Path(__file__))},
        "python": sys.version,
        "versions": {name: version(name) for name in previous["versions"]},
    }


def prepare(output: Path) -> None:
    """Freeze protocol and run analytical/discriminating controls without GEV fits."""
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "criteria.json", CRITERIA)
    write_json(
        output / "protocol.json",
        {
            "candidate": "B, committed compare-candidates.py fit_case unchanged",
            "matrix": {
                "base_cells": 12,
                "draws_per_cell": 1000,
                "fits": 132000,
                "quantiles": 144000,
                "pairs": 120000,
                "summary_cells": 144,
            },
            "samples": "Original immutable .npy arrays; no RNG invocation, clipping, filtering or additional draws",
            "translation": "original retained mu=rho-z_p; generating sigma=1; same arrays plus mu",
            "normalization": "sample mean and population std(ddof=0); same optimizer defaults; affine back-transform scalar xclim quantiles",
            "status": "Exact committed B refusal policy; preserve all raw unsuccessful outputs; no fallback",
            "baseline_acceptance": "One baseline fit requests both scalar quantiles, both must be finite; fit-level refusal shared",
            "pair_qualification": "Separate both-accepted numerical pass/fail, both-refused no numerical proof, validity-changed. Require unchanged classifications on all 1000 pairs, no failed both-accepted numerical comparison, nonempty comparisons, and >=95% accepted in each baseline/translated cell. Both-refused never numerical pass.",
            "accuracy": "Unchanged criteria, conditional accepted errors with 1000 attempted denominator; all 24 baseline scale cells and 72 eligible translated scale+relative cells must pass; all 120 translated cells must pass translation/validity gates",
            "zero_near_zero": "rho=0 relative error undefined; rho=.05 diagnostic only; all raw and accepted scale and relative summaries retained",
            "chunks": 240,
            "draws_per_chunk": 50,
            "workers": 4,
            "retention": "Every fit/status/parameter/quantile/normalization/warning/failure and final optimizer simplex retained; objective evaluation counts checked but full per-evaluation histories not retained",
            "resume": "Only completed chunk files with exact companion hash/count and frozen source/protocol binding reused",
            "validation": "Prior inventories and installed sources; inherited discriminating controls plus summary gate controls; 186 embedded exact B replays; coordinator independent raw arithmetic audit",
            "qualification_boundary": "IID stationary GEV fixtures only; no production integration, screening-floor ruling or observed hydrological adequacy",
        },
    )
    controls = HELP["controls"]()
    refused = numeric_errors(
        {
            "accepted": False,
            "quantiles": [{"p": 0.9, "scale_error": "inf", "relative_error": "nan"}],
        }
    )
    assert (
        HELP["error_summary"](
            [
                refused["quantiles"][0]["scale_error"],
                refused["quantiles"][0]["relative_error"],
            ]
        )["finite_denominator"]
        == 0
    )
    assert (
        HELP["pair_result"](refused, refused, 0.9)["outcome"]
        == "both_refused_no_numerical_proof"
    )
    controls["serialized_refused_inf_nan_safe_and_not_numerical_proof"] = True
    good = {
        "accepted": 950,
        "pairs": Counter(passed=950, both_refused_no_numerical_proof=50),
    }
    assert translation_gate(good, 950)
    assert not translation_gate(
        {
            **good,
            "pairs": Counter(
                passed=949, failed_numeric=1, both_refused_no_numerical_proof=50
            ),
        },
        950,
    )
    assert not translation_gate(
        {"accepted": 0, "pairs": Counter(both_refused_no_numerical_proof=1000)}, 0
    )
    assert not translation_gate(
        {
            "accepted": 949,
            "pairs": Counter(passed=949, both_refused_no_numerical_proof=51),
        },
        949,
    )
    controls["full_denominator_and_translation_gate_discrimination"] = True
    write_json(output / "controls.json", controls)
    write_json(
        output / "provenance.json",
        {"utc": datetime.now(timezone.utc).isoformat(), **verify_inputs()},
    )
    write_json(
        output / "preflight.json",
        {
            "files": {p.name: sha(p) for p in output.iterdir() if p.is_file()},
            "GEV_fits_executed": 0,
        },
    )
    print("Prepared frozen protocol and controls; zero GEV fits", flush=True)


def frozen_binding(output: Path) -> str:
    """Check the prepared source/input binding before any execution or reuse."""
    preflight = json.loads((output / "preflight.json").read_text())
    for name, expected in preflight["files"].items():
        assert sha(output / name) == expected, name
    current = verify_inputs()
    previous = json.loads((output / "provenance.json").read_text())
    assert all(current[key] == previous[key] for key in current)
    return sha(output / "preflight.json")


def chunk(output_text: str, shape_index: int, n: int, start: int, binding: str) -> dict:
    """Execute fifty original draws using the unchanged committed B function."""
    output = Path(output_text)
    name = f"fits-c{shape_index}-n{n}-{start:04d}"
    target, receipt = output / f"{name}.jsonl.gz", output / f"{name}.json"
    if receipt.exists():
        result = json.loads(receipt.read_text())
        assert result["binding"] == binding and result["sha256"] == sha(target)
        assert result["fits"] == 550 and result["quantiles"] == 600
        return result | {"reused": True}
    assert not target.exists(), f"Unreceipted chunk requires inspection: {target}"
    started = time.perf_counter()
    c = CRITERIA["shapes_scipy_c"][shape_index]
    rows = defaultdict(dict)
    with gzip.open(
        OLD / f"results/draws-c{shape_index}-n{n}-{start:04d}.jsonl.gz", "rt"
    ) as stream:
        for line in stream:
            row = json.loads(line)
            rows[(c, n, row["p"], row["ratio"])][row["draw"]] = row
    samples = np.load(
        OLD / f"results/samples-c{shape_index}-n{n}.npy", allow_pickle=False
    )
    fits = quantiles = accepted = evals = 0
    slots = [(None, None)] + [
        (p, rho)
        for p in CRITERIA["probabilities"]
        for rho in CRITERIA["ratios_true_quantile_over_generating_scale"]
    ]
    part = target.with_suffix(".part")
    with gzip_writer(part) as stream:
        for draw in range(start, start + 50):
            for slot, (p, rho) in enumerate(slots):
                old = rows[(c, n, 0.9 if p is None else p, rho)][draw]
                fit_id = (
                    (shape_index * 4 + CRITERIA["usable_counts"].index(n)) * 11000
                    + draw * 11
                    + slot
                )
                case = {
                    "trace_id": fit_id,
                    "selection": "full_original_matrix",
                    "shape_c": c,
                    "n": n,
                    "draw": draw,
                    "p": p,
                    "ratio": rho,
                    "mu": old["mu"],
                    "parameters": old["parameters_c_loc_scale"],
                    "optimizer_result": {"status": None},
                    "optimizer_options_passed_unchanged": OPTIONS,
                }
                record, evaluations = HELP["fit_case"](
                    "B", case, samples[draw] + old["mu"], rows
                )
                record["fit_id"] = record.pop("trace_id")
                record["evaluation_count_verified"] = len(evaluations)
                if record["optimizer"] is not None:
                    assert len(evaluations) == record["optimizer"]["nfev"]
                stream.write(
                    json.dumps(PLAIN(record), separators=(",", ":"), allow_nan=False)
                    + "\n"
                )
                fits += 1
                quantiles += len(record["quantiles"])
                accepted += record["accepted"]
                evals += len(evaluations)
    part.replace(target)
    result = {
        "file": target.name,
        "sha256": sha(target),
        "binding": binding,
        "fits": fits,
        "quantiles": quantiles,
        "accepted": accepted,
        "evaluations": evals,
        "seconds": time.perf_counter() - started,
    }
    assert fits == 550 and quantiles == 600
    write_json(receipt, result)
    return result


def translation_gate(cell: dict, baseline_accepted: int) -> bool:
    """Apply unchanged tolerance/validity gates without credit for both-refused."""
    counts = cell["pairs"]
    return (
        cell["accepted"] >= 950
        and baseline_accepted >= 950
        and counts.get("passed", 0) > 0
        and counts.get("failed_numeric", 0) == 0
        and counts.get("validity_changed", 0) == 0
    )


def summarize(output: Path) -> None:
    """Reduce every retained outcome with explicit raw and accepted denominators."""
    cells = defaultdict(
        lambda: {
            "raw": [],
            "accepted_errors": [],
            "relative_raw": [],
            "relative_accepted": [],
            "accepted": 0,
            "attempted": 0,
            "pairs": Counter(),
        }
    )
    status_counts, reasons = Counter(), Counter()
    totals = Counter()
    known = {
        tuple(row[key] for key in ("shape_c", "n", "draw", "p", "ratio")): row
        for row in json.loads(
            (CANDIDATES / "results/candidate-results.json").read_text()
        )["cases"]
        if row["candidate"] == "B"
    }
    exact_replays = []
    with gzip_writer(output / "paired-translations.jsonl.gz") as pair_stream:
        for path in sorted(output.glob("fits-*.jsonl.gz")):
            baseline = {}
            with gzip.open(path, "rt") as stream:
                for line in stream:
                    row = json.loads(line)
                    identity = tuple(
                        row[key] for key in ("shape_c", "n", "draw", "p", "ratio")
                    )
                    if identity in known:
                        old = known[identity]
                        for key in (
                            "accepted",
                            "refusal_reasons",
                            "normalization_mean",
                            "normalization_population_std",
                            "raw_normalized_parameters",
                            "raw_physical_parameters",
                            "optimizer",
                            "quantiles",
                        ):
                            assert row[key] == old[key], (identity, key)
                        exact_replays.append(row["fit_id"])
                    row = numeric_errors(row)
                    totals["fits"] += 1
                    totals["accepted_fits"] += row["accepted"]
                    totals["warnings"] += len(row["warnings"])
                    totals["estimator_exceptions"] += (
                        row["estimator_exception"] is not None
                    )
                    status_counts[
                        str(row["optimizer"]["status"] if row["optimizer"] else None)
                    ] += 1
                    reasons.update(row["refusal_reasons"])
                    if row["ratio"] is None:
                        baseline[row["draw"]] = row
                    for q in row["quantiles"]:
                        totals["quantiles"] += 1
                        cell = cells[(row["shape_c"], row["n"], q["p"], row["ratio"])]
                        cell["attempted"] += 1
                        cell["accepted"] += row["accepted"]
                        cell["raw"].append(q["scale_error"])
                        cell["relative_raw"].append(q["relative_error"])
                        if row["accepted"]:
                            cell["accepted_errors"].append(q["scale_error"])
                            cell["relative_accepted"].append(q["relative_error"])
                        if row["ratio"] is not None:
                            pair = HELP["pair_result"](
                                baseline[row["draw"]], row, q["p"]
                            )
                            cell["pairs"][pair["outcome"]] += 1
                            pair_stream.write(
                                json.dumps(
                                    {
                                        key: row[key]
                                        for key in (
                                            "fit_id",
                                            "shape_c",
                                            "n",
                                            "draw",
                                            "p",
                                            "ratio",
                                        )
                                    }
                                    | PLAIN(pair),
                                    separators=(",", ":"),
                                    allow_nan=False,
                                )
                                + "\n"
                            )
    assert (
        totals["fits"] == 132000
        and totals["quantiles"] == 144000
        and len(exact_replays) == 186
    )
    matrix = []
    for (c, n, p, rho), cell in cells.items():
        assert cell["attempted"] == 1000
        scale = HELP["error_summary"](cell["accepted_errors"])
        relative = HELP["error_summary"](cell["relative_accepted"])
        rate_pass = cell["accepted"] / 1000 >= CRITERIA["valid_rate_min"]
        scale_pass = (
            rate_pass
            and scale["median_signed"] is not None
            and abs(scale["median_signed"]) <= CRITERIA["median_scale_abs_max"]
            and scale["p90_absolute"] <= CRITERIA["p90_abs_scale_max"][str(p)]
        )
        relative_pass = (
            None
            if rho in (None, 0)
            else rate_pass
            and relative["median_signed"] is not None
            and abs(relative["median_signed"]) <= CRITERIA["median_relative_abs_max"]
            and relative["p90_absolute"] <= CRITERIA["p90_abs_relative_max"][str(p)]
        )
        translation_pass = (
            None
            if rho is None
            else translation_gate(cell, cells[(c, n, p, None)]["accepted"])
        )
        matrix.append(
            {
                "shape_c": c,
                "n": n,
                "p": p,
                "ratio": rho,
                "attempted": 1000,
                "accepted": cell["accepted"],
                "refused": 1000 - cell["accepted"],
                "accepted_rate": cell["accepted"] / 1000,
                "raw_scale": HELP["error_summary"](cell["raw"]),
                "accepted_scale": scale,
                "raw_relative": HELP["error_summary"](cell["relative_raw"]),
                "accepted_relative": relative,
                "valid_rate_pass": rate_pass,
                "scale_pass": scale_pass,
                "relative_pass": relative_pass,
                "relative_qualification_applicable": rho
                in CRITERIA["relative_qualified_ratios"],
                "pair_outcomes": cell["pairs"],
                "translation_gate_pass": translation_pass,
            }
        )
    baseline_rows = [r for r in matrix if r["ratio"] is None]
    eligible = [r for r in matrix if r["relative_qualification_applicable"]]
    translated = [r for r in matrix if r["ratio"] is not None]
    passed = (
        all(r["scale_pass"] for r in baseline_rows)
        and all(r["scale_pass"] and r["relative_pass"] for r in eligible)
        and all(r["translation_gate_pass"] for r in translated)
    )
    write_json(output / "matrix-results.json", {"cells": matrix})
    write_json(
        output / "qualification-summary.json",
        {
            "qualification_passed": passed,
            "totals": totals,
            "optimizer_status_counts": status_counts,
            "refusal_reasons": reasons,
            "baseline_scale_passed": sum(r["scale_pass"] for r in baseline_rows),
            "baseline_cells": len(baseline_rows),
            "eligible_scale_and_relative_passed": sum(
                r["scale_pass"] and r["relative_pass"] for r in eligible
            ),
            "eligible_cells": len(eligible),
            "translation_cells_passed": sum(
                r["translation_gate_pass"] for r in translated
            ),
            "translation_cells": len(translated),
            "exact_embedded_candidate_B_replays": exact_replays,
        },
    )


def main() -> None:
    """Prepare, execute/reuse fixed chunks, or summarize retained outcomes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "summarize"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if args.action == "prepare":
        prepare(output)
        return
    binding = frozen_binding(output)
    if args.action == "summarize":
        summarize(output)
        return
    started = time.perf_counter()
    results = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        jobs = [
            pool.submit(chunk, str(output), ci, n, start, binding)
            for ci in range(3)
            for n in CRITERIA["usable_counts"]
            for start in range(0, 1000, 50)
        ]
        for job in as_completed(jobs):
            result = job.result()
            results.append(result)
            print(
                json.dumps(
                    {
                        "completed_chunks": len(results),
                        "total_chunks": 240,
                        "elapsed_seconds": time.perf_counter() - started,
                        **result,
                    }
                ),
                flush=True,
            )
    assert frozen_binding(output) == binding
    summarize(output)
    write_json(
        output / "execution-completion.json",
        {
            "seconds": time.perf_counter() - started,
            "workers": 4,
            "chunks": len(results),
            "fits": sum(r["fits"] for r in results),
            "quantiles": sum(r["quantiles"] for r in results),
            "frozen_sources_and_inputs_unchanged": True,
            "binding": binding,
        },
    )
    print("Completed all 240 chunks and qualification summaries", flush=True)


if __name__ == "__main__":
    main()
