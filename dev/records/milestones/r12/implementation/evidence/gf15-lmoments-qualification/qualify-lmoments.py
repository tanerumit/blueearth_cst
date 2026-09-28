"""Run the fixed GF15 Stage 2 matrix with the signed, unchanged Stage 1 adapter.

Local evidence namespace only. Statistical failures do not stop the matrix;
input, software and receipt failures stop without a successful completion.
"""

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
import shutil
import sys
import time
import traceback
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
READINESS = ROOT.parent / "gf15-lmoments-readiness"
ORIGINAL = ROOT.parent / "gf15/results"
NORMALIZED = ROOT.parent / "gf15-normalized-qualification/results"
sys.path.insert(0, str(READINESS))
SPEC = importlib.util.spec_from_file_location(
    "stage1_readiness", READINESS / "check-readiness.py"
)
READY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = READY
SPEC.loader.exec_module(READY)
ADAPTER = READY.adapter
CRITERIA = READY.read_json(ORIGINAL / "criteria.json")
KEY = ("shape_c", "n", "draw", "p", "ratio")
ANCHORS = {
    "results/independent/signed-verdict.json": "837968aff560f67d67a21bd292476c2f75fa051987da025ddc2065c703195d39",
    "results/attempt-2/completion.json": "7cba09d4bf7af14a93b08e9deedff7b48dd5fe019cd1baf9e992a11bf651338c",
    "artifact-inventory.json": "e5c45124f30949cec124ebb41c12ef9b6b609ffe63fc8d3e42128a370254b2ca",
}
BRANCHES = (
    "preinversion_refusal",
    "positive_snap",
    "positive_rational",
    "nonpositive_rational",
    "newton_rational",
    "newton_alternate",
)


def digest_object(value: object) -> str:
    """Hash canonical JSON, rejecting unmarked nonfinite values."""
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def finite_json(value: object) -> object:
    """Retain exceptional numeric diagnostics as explicit strings, never drop them."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: finite_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [finite_json(v) for v in value]
    return value


@contextmanager
def gzip_writer(path: Path):
    """Write reproducible compressed JSONL bytes to an exclusively claimed path."""
    with path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as text:
                yield text
        raw.flush()
        os.fsync(raw.fileno())


def emit(stream, row: dict) -> None:
    """Write one losslessly retained record with strict JSON numeric handling."""
    stream.write(
        json.dumps(finite_json(row), separators=(",", ":"), allow_nan=False) + "\n"
    )


def atomic_chunk(
    namespace: Path, binding: str, compute, expected: tuple[int, int] = (550, 600)
) -> dict:
    """Publish a complete fit payload and atomic receipt; exact receipts alone resume."""
    namespace.mkdir(exist_ok=True)
    owner = namespace / "writer.claim"
    fd = os.open(owner, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        intent = namespace / "binding.json"
        if intent.exists():
            if READY.read_json(intent) != {"binding": binding}:
                raise ValueError("conflicting chunk binding")
        else:
            READY.write_json_exclusive(intent, {"binding": binding})
        payload, receipt = namespace / "fits.jsonl.gz", namespace / "receipt.json"
        if receipt.exists():
            record = READY.read_json(receipt)
            if (
                record["binding"] != binding
                or not payload.exists()
                or record["sha256"] != READY.sha(payload)
                or (record["fits"], record["quantiles"]) != expected
            ):
                raise ValueError("inconsistent chunk receipt")
            records = list(READY.rows(payload))
            counts = (len(records), sum(len(r["quantiles"]) for r in records))
            if (
                counts != expected
                or sum(r["accepted"] for r in records) != record["accepted_fits"]
            ):
                raise ValueError("inconsistent receipt payload counts")
            return record | {"reused": True}
        if payload.exists() or (namespace / "receipt.pending").exists():
            raise ValueError("unreceipted completed payload requires review")
        started = time.perf_counter()
        records = compute()
        counts = (len(records), sum(len(r["quantiles"]) for r in records))
        if counts != expected:
            raise ValueError("incomplete computed chunk")
        partial = namespace / "fits.partial"
        if partial.exists():
            partial.unlink()  # Exact binding above permits disposable partial recovery.
        with gzip_writer(partial) as stream:
            for row in records:
                emit(stream, row)
        partial.rename(payload)
        result = {
            "binding": binding,
            "sha256": READY.sha(payload),
            "file": payload.name,
            "fits": counts[0],
            "quantiles": counts[1],
            "accepted_fits": sum(r["accepted"] for r in records),
            "seconds": time.perf_counter() - started,
        }
        READY.write_atomic_completion(receipt, result)
        return result | {"reused": False}
    finally:
        owner.unlink()


def verify_stage1() -> dict:
    """Bind accepted readiness, controls and runtime without repeating fixed fits."""
    for name, expected in ANCHORS.items():
        if READY.sha(READINESS / name) != expected:
            raise ValueError(f"Stage 1 anchor changed: {name}")
    signed = READY.read_json(READINESS / "results/independent/signed-verdict.json")
    for section, prefix in (
        ("source", READINESS),
        ("control_files", READINESS / "results/attempt-2"),
        ("independent_evidence", READINESS / "results/independent"),
    ):
        for name, expected in signed[section].items():
            if READY.sha(prefix / name) != expected:
                raise ValueError(f"signed readiness binding changed: {name}")
    if (
        READY.sha(READINESS / "environment/artifact-inventory.json")
        != signed["environment_inventory_sha256"]
    ):
        raise ValueError("signed environment inventory changed")
    design = ROOT.parents[2] / "gf15-alternative-estimator-design.md"
    if READY.sha(design) != signed["design_sha256"]:
        raise ValueError("accepted design changed")
    verified = READY.verify_environment_and_protected()
    return {
        "anchors": ANCHORS,
        "signed_verdict": signed,
        "runtime_verification": verified,
    }


def error_row(truth: dict, accepted: bool, estimate: float | None) -> dict:
    """Attach A-owned truth and errors using generator scale, preserving statuses."""
    row = {name: truth[name] for name in (*KEY, "mu", "true_quantile")}
    row.update(accepted=accepted, estimate=estimate, sigma_generator=truth["sigma"])
    if accepted and (estimate is None or not math.isfinite(estimate)):
        raise ValueError("accepted quantile has nonfinite estimate")
    error = (
        None if not accepted else (estimate - truth["true_quantile"]) / truth["sigma"]
    )
    relative = None
    if accepted and truth["ratio"] not in (None, 0):
        relative = (estimate - truth["true_quantile"]) / abs(truth["true_quantile"])
    row.update(scale_error=error, relative_error=relative)
    return row


def compute_chunk(index: int, count: int, start: int) -> list[dict]:
    """Execute exactly eleven independent fits per retained draw, truth-blind."""
    shape = CRITERIA["shapes_scipy_c"][index]
    suffix = f"c{index}-n{count}-{start:04d}"
    originals = {
        READY.canonical_key(row): row
        for row in READY.rows(ORIGINAL / f"draws-{suffix}.jsonl.gz")
    }
    samples = np.load(ORIGINAL / f"samples-c{index}-n{count}.npy", allow_pickle=False)
    slots = [(None, None)] + [
        (p, rho)
        for p in CRITERIA["probabilities"]
        for rho in CRITERIA["ratios_true_quantile_over_generating_scale"]
    ]
    results = []
    for draw in range(start, start + 50):
        for p, ratio in slots:
            probabilities = CRITERIA["probabilities"] if ratio is None else [p]
            truth = originals[(shape, count, draw, probabilities[0], ratio)]
            supplied = samples[draw] + truth["mu"]
            begun = time.perf_counter()
            raw = ADAPTER.fit_case(supplied, probabilities)
            elapsed = time.perf_counter() - begun
            branch = {"branch": "preinversion_refusal"}
            if "moments" in raw and "invalid_moments" not in raw["refusal_reasons"]:
                branch = READY.branch_identity(raw["moments"]["t3"])
            diagnostics = {q["p"]: q for q in raw["quantiles"]}
            quantiles = []
            for probability in probabilities:
                original = originals[(shape, count, draw, probability, ratio)]
                diagnostic = diagnostics.get(probability, {})
                quantiles.append(
                    error_row(original, raw["accepted"], diagnostic.get("estimate"))
                )
            results.append(
                {
                    "shape_c": shape,
                    "n": count,
                    "draw": draw,
                    "p": p,
                    "ratio": ratio,
                    "mu": truth["mu"],
                    "accepted": raw["accepted"],
                    "fit_seconds": elapsed,
                    "branch": branch,
                    "adapter_record": raw,
                    "quantiles": quantiles,
                }
            )
    return results


def error_summary(values: list[float]) -> dict | None:
    """Compute conditional linear-quantile summaries; empty populations stay null."""
    if not values:
        return None
    array = np.asarray(values, dtype=np.float64)
    if not np.isfinite(array).all():
        raise ValueError("nonfinite accepted error")
    return {
        "median": float(np.quantile(array, 0.5, method="linear")),
        "median_absolute": float(np.quantile(abs(array), 0.5, method="linear")),
        "p90_absolute": float(np.quantile(abs(array), 0.9, method="linear")),
    }


def cell_summary(records: list[dict]) -> dict:
    """Apply every individual unchanged gate with explicit denominators/margins."""
    if len(records) != 1000:
        raise ValueError("all-draw denominator must be 1000")
    first = records[0]
    selected = [row for row in records if row["accepted"]]
    scale = error_summary([row["scale_error"] for row in selected])
    relative = (
        error_summary([row["relative_error"] for row in selected])
        if first["ratio"] not in (None, 0)
        else None
    )
    p = str(first["p"])
    margins = {
        "valid_rate": len(selected) / 1000 - CRITERIA["valid_rate_min"],
        "scale_median": None
        if scale is None
        else CRITERIA["median_scale_abs_max"] - abs(scale["median"]),
        "scale_p90": None
        if scale is None
        else CRITERIA["p90_abs_scale_max"][p] - scale["p90_absolute"],
        "relative_median": None
        if relative is None
        else CRITERIA["median_relative_abs_max"] - abs(relative["median"]),
        "relative_p90": None
        if relative is None
        else CRITERIA["p90_abs_relative_max"][p] - relative["p90_absolute"],
    }
    scale_pass = scale is not None and all(
        margins[k] >= 0 for k in ("valid_rate", "scale_median", "scale_p90")
    )
    eligible = first["ratio"] in CRITERIA["relative_qualified_ratios"]
    relative_pass = (
        (
            relative is not None
            and all(
                margins[k] >= 0
                for k in ("valid_rate", "relative_median", "relative_p90")
            )
        )
        if eligible
        else None
    )
    return {
        **{k: first[k] for k in ("shape_c", "n", "p", "ratio")},
        "all_draws": 1000,
        "accepted_count": len(selected),
        "valid_rate": len(selected) / 1000,
        "scale": scale,
        "relative": relative,
        "relative_eligible": eligible,
        "scale_pass": scale_pass,
        "relative_pass": relative_pass,
        "margins": margins,
        "individual_gate_pass": scale_pass and (relative_pass if eligible else True),
    }


def translation_result(baseline: dict, translated: dict) -> dict:
    """Distinguish all four acceptance states and the accepted-pair error gate."""
    category = READY.comparison_category(baseline["accepted"], translated["accepted"])
    delta = (
        translated["scale_error"] - baseline["scale_error"]
        if category == "both_accepted"
        else None
    )
    return {
        "category": category,
        "acceptance_unchanged": baseline["accepted"] == translated["accepted"],
        "delta_scale_error": delta,
        "numerical_pass": None
        if delta is None
        else abs(delta) <= CRITERIA["translation_paired_abs_max"],
        "margin": None
        if delta is None
        else CRITERIA["translation_paired_abs_max"] - abs(delta),
    }


def translation_cell_gate(outcomes: list[dict]) -> bool:
    """Preserve predecessor rates and all-pair acceptance/numerical requirements."""
    if len(outcomes) != 1000:
        raise ValueError("translation denominator must be 1000")
    return (
        sum(r["category"] == "both_accepted" for r in outcomes) >= 950
        and all(r["acceptance_unchanged"] for r in outcomes)
        and not any(r["numerical_pass"] is False for r in outcomes)
    )


def load_tables(output: Path, binding: str) -> tuple[dict, dict]:
    """Rehash/recount every chunk and reconstruct full distinct canonical keys."""
    tables = {label: {} for label in "ABC"}
    diagnostic = {
        "fits": 0,
        "accepted_fits": 0,
        "branches": Counter({b: 0 for b in BRANCHES}),
        "refusals": Counter(),
        "warnings": Counter(),
        "exception_refusals": 0,
        "fit_seconds": 0.0,
        "sample_outside_support_fits": Counter(),
        "nonfinite_log_density_fits": Counter(),
    }
    for index, shape in enumerate(CRITERIA["shapes_scipy_c"]):
        for count in CRITERIA["usable_counts"]:
            samples = np.load(
                ORIGINAL / f"samples-c{index}-n{count}.npy", allow_pickle=False
            )
            for start in range(0, 1000, 50):
                suffix = f"c{index}-n{count}-{start:04d}"
                originals = {}
                for a in READY.rows(ORIGINAL / f"draws-{suffix}.jsonl.gz"):
                    key = READY.canonical_key(a)
                    originals[key] = a
                    READY.insert_unique(
                        tables["A"], error_row(a, a["valid"], a["estimate"])
                    )
                for b in READY.rows(NORMALIZED / f"fits-{suffix}.jsonl.gz"):
                    for q in b["quantiles"]:
                        key = (shape, count, b["draw"], q["p"], b["ratio"])
                        READY.insert_unique(
                            tables["B"],
                            error_row(originals[key], b["accepted"], q["estimate"]),
                        )
                namespace = output / "chunks" / suffix
                atomic_chunk(
                    namespace,
                    binding,
                    lambda: (_ for _ in ()).throw(
                        ValueError("missing completed chunk")
                    ),
                )
                for fit in READY.rows(namespace / "fits.jsonl.gz"):
                    diagnostic["fits"] += 1
                    diagnostic["accepted_fits"] += fit["accepted"]
                    diagnostic["fit_seconds"] += fit["fit_seconds"]
                    raw = fit["adapter_record"]
                    expected_probabilities = (
                        CRITERIA["probabilities"]
                        if fit["ratio"] is None
                        else [fit["p"]]
                    )
                    supplied = samples[fit["draw"]] + fit["mu"]
                    if (
                        raw["input"]["sample_sha256"]
                        != hashlib.sha256(supplied.tobytes()).hexdigest()
                        or raw["input"]["probabilities"] != expected_probabilities
                        or raw["accepted"] != fit["accepted"]
                        or [q["p"] for q in fit["quantiles"]] != expected_probabilities
                    ):
                        raise ValueError(
                            "candidate sample/probability/shared acceptance mismatch"
                        )
                    branch = {"branch": "preinversion_refusal"}
                    if (
                        "moments" in raw
                        and "invalid_moments" not in raw["refusal_reasons"]
                    ):
                        branch = READY.branch_identity(raw["moments"]["t3"])
                    if branch != fit["branch"]:
                        raise ValueError("candidate branch mismatch")
                    estimates = {q["p"]: q.get("estimate") for q in raw["quantiles"]}
                    diagnostic["branches"][fit["branch"]["branch"]] += 1
                    diagnostic["refusals"].update(raw["refusal_reasons"])
                    diagnostic["warnings"].update(
                        json.dumps(w, sort_keys=True) for w in raw["warnings"]
                    )
                    diagnostic["exception_refusals"] += "exception_refusal" in raw
                    for coordinate in ("normalized", "physical"):
                        values = raw.get(f"{coordinate}_diagnostics", {})
                        diagnostic["sample_outside_support_fits"][coordinate] += (
                            values.get("sample_outside_support", 0) > 0
                        )
                        diagnostic["nonfinite_log_density_fits"][coordinate] += (
                            values.get("nonfinite_log_density_count", 0) > 0
                        )
                    for q in fit["quantiles"]:
                        key = READY.canonical_key(q)
                        truth = originals[key]
                        if q["estimate"] != estimates.get(q["p"]):
                            raise ValueError("adapter estimate changed")
                        if (
                            fit["mu"] != truth["mu"]
                            or q["true_quantile"] != truth["true_quantile"]
                            or q["accepted"] != fit["accepted"]
                        ):
                            raise ValueError("candidate truth/acceptance drift")
                        expected = error_row(truth, fit["accepted"], q["estimate"])
                        if expected != q:
                            raise ValueError("candidate error recomputation mismatch")
                        READY.insert_unique(tables["C"], q)
    expected_keys = {
        (c, n, draw, p, rho)
        for c in CRITERIA["shapes_scipy_c"]
        for n in CRITERIA["usable_counts"]
        for draw in range(1000)
        for p in CRITERIA["probabilities"]
        for rho in (None, *CRITERIA["ratios_true_quantile_over_generating_scale"])
    }
    for table in tables.values():
        READY.validate_key_coverage(set(table), expected_keys)
    if diagnostic["fits"] != 132000 or sum(diagnostic["branches"].values()) != 132000:
        raise ValueError("incomplete fit/branch coverage")
    return tables, diagnostic


def summarize(output: Path, binding: str) -> dict:
    """Emit all individual cells, exhaustive translations and pair intersections."""
    tables, diagnostic = load_tables(output, binding)
    cells = [
        (c, n, p, rho)
        for c in CRITERIA["shapes_scipy_c"]
        for n in CRITERIA["usable_counts"]
        for p in CRITERIA["probabilities"]
        for rho in (None, *CRITERIA["ratios_true_quantile_over_generating_scale"])
    ]
    summaries = {}
    for label, table in tables.items():
        summaries[label] = [
            cell_summary([table[(c, n, d, p, rho)] for d in range(1000)])
            for c, n, p, rho in cells
        ]
    READY.write_json_exclusive(output / "individual-cells.json", summaries)
    pair_summaries = {}
    with gzip_writer(output / "paired-keys.jsonl.gz") as stream:
        for first, second in (("A", "B"), ("A", "C"), ("B", "C")):
            pair = first + second
            pair_summaries[pair] = []
            for c, n, p, rho in cells:
                categories = Counter(
                    {
                        k: 0
                        for k in (
                            "both_accepted",
                            "first_only",
                            "second_only",
                            "both_refused",
                        )
                    }
                )
                selected = {first: [], second: []}
                retained = []
                for draw in range(1000):
                    key = (c, n, draw, p, rho)
                    a, b = tables[first][key], tables[second][key]
                    category = READY.comparison_category(a["accepted"], b["accepted"])
                    categories[category] += 1
                    emit(
                        stream,
                        {
                            "pair": pair,
                            "key": list(key),
                            "category": category,
                            first: {
                                k: a[k]
                                for k in ("accepted", "scale_error", "relative_error")
                            },
                            second: {
                                k: b[k]
                                for k in ("accepted", "scale_error", "relative_error")
                            },
                        },
                    )
                    if category == "both_accepted":
                        retained.append(draw)
                        selected[first].append(a)
                        selected[second].append(b)
                pair_summaries[pair].append(
                    {
                        "shape_c": c,
                        "n": n,
                        "p": p,
                        "ratio": rho,
                        "all_draws": 1000,
                        "categories": dict(categories),
                        "intersection_count": len(retained),
                        "retained_draw_ids": retained,
                        "intersection_errors": {
                            label: {
                                "scale": error_summary(
                                    [r["scale_error"] for r in selected[label]]
                                ),
                                "relative": None
                                if rho in (None, 0)
                                else error_summary(
                                    [r["relative_error"] for r in selected[label]]
                                ),
                            }
                            for label in (first, second)
                        },
                    }
                )
    READY.write_json_exclusive(output / "paired-cells.json", pair_summaries)
    translated_cells = []
    categories = Counter(
        {k: 0 for k in ("both_accepted", "first_only", "second_only", "both_refused")}
    )
    numeric_failures = 0
    max_delta = 0.0
    with gzip_writer(output / "translation-pairs.jsonl.gz") as stream:
        for c, n, p, rho in cells:
            if rho is None:
                continue
            outcomes = []
            for draw in range(1000):
                baseline = tables["C"][(c, n, draw, p, None)]
                translated = tables["C"][(c, n, draw, p, rho)]
                result = translation_result(baseline, translated)
                emit(
                    stream,
                    {
                        "key": [c, n, draw, p, rho],
                        "baseline_error": baseline["scale_error"],
                        "translated_error": translated["scale_error"],
                        **result,
                    },
                )
                categories[result["category"]] += 1
                numeric_failures += result["numerical_pass"] is False
                if result["delta_scale_error"] is not None:
                    max_delta = max(max_delta, abs(result["delta_scale_error"]))
                outcomes.append(result)
            cell_categories = Counter(r["category"] for r in outcomes)
            # Preserve B's cell gate: refusals never count as numeric passes.
            translated_cells.append(
                {
                    "shape_c": c,
                    "n": n,
                    "p": p,
                    "ratio": rho,
                    "all_draws": 1000,
                    "categories": dict(cell_categories),
                    "acceptance_unchanged": all(
                        r["acceptance_unchanged"] for r in outcomes
                    ),
                    "numerical_passes": sum(
                        r["numerical_pass"] is True for r in outcomes
                    ),
                    "numerical_failures": sum(
                        r["numerical_pass"] is False for r in outcomes
                    ),
                    "translation_pass": translation_cell_gate(outcomes),
                }
            )
    READY.write_json_exclusive(
        output / "translation-cells.json", {"cells": translated_cells}
    )
    READY.write_json_exclusive(output / "diagnostics.json", diagnostic)
    result = {
        "stage": "Stage 2 observed mechanical outcomes; Stage 3 scientific verdict pending",
        "counts": {
            "fits": diagnostic["fits"],
            "quantiles": len(tables["C"]),
            "individual_cells_per_estimator": len(cells),
            "translation_pairs": sum(categories.values()),
            "pairwise_rows": 3 * len(tables["C"]),
        },
        "individual_outcomes": {
            label: {
                "accepted_quantiles": sum(
                    r["accepted"] for r in tables[label].values()
                ),
                "baseline_scale_passed": sum(
                    r["scale_pass"] for r in rows if r["ratio"] is None
                ),
                "baseline_cells": 24,
                "all_scale_passed": sum(r["scale_pass"] for r in rows),
                "eligible_scale_and_relative_passed": sum(
                    r["individual_gate_pass"] for r in rows if r["relative_eligible"]
                ),
                "eligible_cells": 72,
                "all_individual_gates_passed": all(
                    r["individual_gate_pass"] for r in rows
                ),
            }
            for label, rows in summaries.items()
        },
        "translation": {
            "categories": dict(categories),
            "numeric_failures": numeric_failures,
            "max_absolute_delta_scale_error": max_delta,
            "passed_cells": sum(r["translation_pass"] for r in translated_cells),
            "cells": 120,
        },
        "mechanical_gate_conjunction": all(
            r["individual_gate_pass"] for r in summaries["C"]
        )
        and all(r["translation_pass"] for r in translated_cells),
        "independent_qualification_acceptance": None,
    }
    READY.write_json_exclusive(output / "qualification-summary.json", result)
    return result


def source_identity() -> dict:
    """Bind all authored evaluator sources and usage contract before matrix fits."""
    return {
        p.name: READY.sha(p)
        for p in ROOT.iterdir()
        if p.suffix == ".py" or p.name == "README.md"
    }


def prepare(output: Path) -> None:
    """Exclusively claim an absent attempt and freeze complete input/source identity."""
    output.mkdir(parents=False, exist_ok=False)
    verified = verify_stage1()
    audit = READY.audit_inputs()
    if audit != READY.read_json(READINESS / "results/attempt-2/input-audit.json"):
        raise ValueError("complete D4 audit differs from accepted readiness")
    READY.write_json_exclusive(output / "input-audit.json", audit)
    shutil.copyfile(ORIGINAL / "criteria.json", output / "criteria.json")
    READY.write_json_exclusive(
        output / "environment.json",
        READY.read_json(READINESS / "environment/effective-environment.json"),
    )
    manifest = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "source": source_identity(),
        "readiness": verified,
        "input_audit_sha256": READY.sha(output / "input-audit.json"),
        "criteria_sha256": READY.sha(output / "criteria.json"),
        "environment_sha256": READY.sha(output / "environment.json"),
        "estimator": "exact signed candidate_adapter.fit_case(sample, probabilities); no fallback",
        "scope": "Stage 2 only; complete original development matrix; no resampling or production",
        "expected_counts": {
            "chunks": 240,
            "fits": 132000,
            "quantiles": 144000,
            "cells": 144,
            "translation_pairs": 120000,
        },
        "comparison_status": {
            "A": "original per-p valid",
            "B": "shared accepted",
            "C": "shared baseline accepted; scalar translated accepted",
        },
        "sample_and_truth": "A samples[draw]+A.mu; A true_quantile; A sigma=1; no RNG",
        "branch_source": "signed check-readiness.branch_identity using retained t3 and pinned coefficients; preinversion refusals counted",
    }
    READY.write_json_exclusive(output / "provenance.json", manifest)
    (output / "chunks").mkdir()
    print(
        json.dumps(
            {"prepared": str(output), "binding": READY.sha(output / "provenance.json")}
        ),
        flush=True,
    )


def check_binding(output: Path) -> str:
    """Refuse any changed readiness, evaluator, criteria, effective runtime or inputs."""
    manifest = READY.read_json(output / "provenance.json")
    if (
        source_identity() != manifest["source"]
        or verify_stage1() != manifest["readiness"]
    ):
        raise ValueError("frozen source/readiness binding changed")
    for name, field in (
        ("input-audit.json", "input_audit_sha256"),
        ("criteria.json", "criteria_sha256"),
        ("environment.json", "environment_sha256"),
    ):
        if READY.sha(output / name) != manifest[field]:
            raise ValueError(f"frozen {name} changed")
    if READY.audit_inputs() != READY.read_json(output / "input-audit.json"):
        raise ValueError("full D4 inputs changed")
    return READY.sha(output / "provenance.json")


def run(output: Path) -> None:
    """Finish every statistical cell, stopping only unexpected control/software faults."""
    if (output / "completion.json").exists() or (output / "failure.json").exists():
        raise ValueError("terminal attempt cannot be resumed or overwritten")
    owner = output / "writer.claim"
    fd = os.open(owner, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    started = time.perf_counter()
    try:
        binding = check_binding(output)
        receipts = []
        for index in range(3):
            for count in CRITERIA["usable_counts"]:
                for start in range(0, 1000, 50):
                    namespace = output / "chunks" / f"c{index}-n{count}-{start:04d}"
                    receipt = atomic_chunk(
                        namespace,
                        binding,
                        lambda i=index, n=count, s=start: compute_chunk(i, n, s),
                    )
                    receipts.append(receipt)
                    print(
                        json.dumps(
                            {
                                "completed_chunks": len(receipts),
                                "total_chunks": 240,
                                "elapsed_seconds": time.perf_counter() - started,
                                **receipt,
                            }
                        ),
                        flush=True,
                    )
        fitting_done = time.perf_counter()
        result = summarize(output, binding)
        if check_binding(output) != binding:
            raise ValueError("binding changed during execution")
        files = {
            p.relative_to(output).as_posix(): READY.sha(p)
            for p in output.rglob("*")
            if p.is_file() and p.name != "writer.claim"
        }
        audit = {
            "status": "mechanically_complete",
            "binding": binding,
            "counts": result["counts"],
            "all_chunk_receipts_verified": 240,
            "all_predecessor_files_verified": 732,
            "canonical_key_sets_equal": True,
            "input_audit_sha256": READY.sha(output / "input-audit.json"),
            "files": files,
        }
        READY.write_json_exclusive(output / "mechanical-audit.json", audit)
        READY.write_atomic_completion(
            output / "completion.json",
            {
                "status": "stage_2_complete_pending_independent_stage_3",
                "binding": binding,
                "mechanical_audit_sha256": READY.sha(output / "mechanical-audit.json"),
                "qualification_summary_sha256": READY.sha(
                    output / "qualification-summary.json"
                ),
                "counts": result["counts"],
                "mechanical_gate_conjunction": result["mechanical_gate_conjunction"],
                "seconds": time.perf_counter() - started,
                "fit_chunk_phase_seconds": fitting_done - started,
                "chunk_seconds": sum(r["seconds"] for r in receipts),
                "reused_chunks": sum(r["reused"] for r in receipts),
                "command": [sys.executable, *sys.argv],
            },
        )
        print(json.dumps(result), flush=True)
    except BaseException as error:
        READY.write_json_exclusive(
            output / "failure.json",
            {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
                "seconds": time.perf_counter() - started,
                "status": "attempt_failed_no_success_receipt",
            },
        )
        raise
    finally:
        owner.unlink()


def main() -> None:
    """Prepare one immutable attempt, then run or resume its exact matrix chunks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if args.action == "prepare":
        prepare(output)
    else:
        run(output)


if __name__ == "__main__":
    main()
