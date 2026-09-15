"""Independently audit frozen GF15 A/B/C records without fitting or evaluator imports."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np


def read(path: Path) -> Any:
    """Read UTF-8 JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    """Hash complete file bytes."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition: bool, context: Any) -> None:
    """Stop with an actionable counterexample."""
    if not condition:
        raise AssertionError(context)


def equal(actual: Any, expected: Any, context: Any) -> None:
    """Compare decoded JSON exactly, preserving boolean versus number types."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), context)
        for name, value in expected.items():
            equal(actual[name], value, (context, name))
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), context)
        for index, value in enumerate(expected):
            equal(actual[index], value, (context, index))
    else:
        require(isinstance(actual, bool) == isinstance(expected, bool), context)
        require(actual == expected, (context, actual, expected))


def records(path: Path) -> Any:
    """Stream all compressed JSON lines."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def inventory(root: Path, entries: Any) -> int:
    """Verify unique manifest paths, sizes and SHA-256."""
    if isinstance(entries, dict):
        entries = entries["files"]
    seen = set()
    for item in entries:
        path = (root / item["path"]).resolve()
        require(path.is_relative_to(root.resolve()), ("escape", path))
        require(path not in seen, ("duplicate inventory", path))
        seen.add(path)
        require(path.stat().st_size == item["bytes"], ("size", path))
        require(digest(path) == item["sha256"], ("hash", path))
    return len(seen)


def hash_map(root: Path, mapping: dict) -> None:
    """Verify every explicit path-to-digest binding."""
    for name, expected in mapping.items():
        equal(digest(root / name), expected, ("binding", name))


def key(row: dict) -> tuple:
    """Preserve null baseline as a distinct fifth key component."""
    return tuple(row[name] for name in ("shape_c", "n", "draw", "p", "ratio"))


def add(target: dict, identity: tuple, row: dict) -> None:
    """Reject duplicate canonical keys."""
    require(identity not in target, ("duplicate key", identity))
    target[identity] = row


def errors(estimate: float | None, truth: float, accepted: bool, ratio: Any) -> dict:
    """Compute errors in generating sigma=1, with baseline/zero convention."""
    scale = float(estimate - truth) if accepted else None
    if accepted:
        require(math.isfinite(scale), ("nonfinite accepted error", estimate, truth))
    relative = scale / abs(truth) if accepted and ratio not in (None, 0) else None
    return {"accepted": accepted, "scale_error": scale, "relative_error": relative}


def describe(values: list) -> dict | None:
    """Compute conditional linear quantiles on an explicit cohort."""
    if not values:
        return None
    array = np.asarray(values, dtype=np.float64)
    require(bool(np.isfinite(array).all()), "nonfinite summary cohort")
    return {
        "median": float(np.quantile(array, 0.5, method="linear")),
        "median_absolute": float(np.quantile(abs(array), 0.5, method="linear")),
        "p90_absolute": float(np.quantile(abs(array), 0.9, method="linear")),
    }


def cell_header(cell: tuple) -> dict:
    """Name cell coordinates."""
    return dict(zip(("shape_c", "n", "p", "ratio"), cell, strict=True))


def summarize(cell: tuple, rows: list) -> dict:
    """Recompute full individual gates and signed point margins."""
    selected = [row for row in rows if row["accepted"]]
    scale = describe([row["scale_error"] for row in selected])
    relative = (
        describe([row["relative_error"] for row in selected])
        if cell[3] not in (None, 0)
        else None
    )
    rate = len(selected) / 949
    limit = 0.5 if cell[2] == 0.9 else 0.25
    eligible = cell[3] in (0.5, 2, 10)
    scale_pass = bool(
        rate >= 0.95
        and scale is not None
        and abs(scale["median"]) <= 0.1
        and scale["p90_absolute"] <= limit
    )
    relative_pass = (
        bool(
            rate >= 0.95
            and relative is not None
            and abs(relative["median"]) <= 0.1
            and relative["p90_absolute"] <= limit
        )
        if eligible
        else None
    )
    return {
        **cell_header(cell),
        "all_draws": 1000,
        "accepted_count": len(selected),
        "valid_rate": rate,
        "scale": scale,
        "relative": relative,
        "relative_eligible": eligible,
        "scale_pass": scale_pass,
        "relative_pass": relative_pass,
        "margins": {
            "valid_rate": rate - 0.95,
            "scale_median": 0.1 - abs(scale["median"]) if scale else None,
            "scale_p90": limit - scale["p90_absolute"] if scale else None,
            "relative_median": 0.1 - abs(relative["median"]) if relative else None,
            "relative_p90": limit - relative["p90_absolute"] if relative else None,
        },
        "individual_gate_pass": scale_pass and (relative_pass if eligible else True),
    }


def category(first: bool, second: bool) -> str:
    """Classify all four acceptance combinations."""
    return {
        (True, True): "both_accepted",
        (True, False): "first_only",
        (False, True): "second_only",
        (False, False): "both_refused",
    }[first, second]


def translated(identity: tuple, baseline: dict, shifted: dict) -> dict:
    """Keep unchanged acceptance separate from the accepted-pair numerical gate."""
    both = baseline["accepted"] and shifted["accepted"]
    delta = shifted["scale_error"] - baseline["scale_error"] if both else None
    return {
        "key": list(identity),
        "baseline_error": baseline["scale_error"],
        "translated_error": shifted["scale_error"],
        "category": category(baseline["accepted"], shifted["accepted"]),
        "acceptance_unchanged": baseline["accepted"] == shifted["accepted"],
        "delta_scale_error": delta,
        "numerical_pass": abs(delta) <= 1e-6 if both else None,
        "margin": 1e-6 - abs(delta) if both else None,
    }


def branch(t3: float) -> dict:
    """Reconstruct source-defined predicates; no estimator or inversion is called."""
    if t3 > 0:
        z = 1 - t3
        g = (-1 + z * (1.59921491 + z * (-0.48832213 + z * 0.01573152))) / (
            1 + z * (-0.64363929 + z * 0.08985247)
        )
        name = "positive_snap" if abs(g) < 1e-5 else "positive_rational"
    else:
        g = (
            0.28377530
            + t3
            * (-1.21096399 + t3 * (-2.50728214 + t3 * (-1.13455566 - t3 * 0.07138022)))
        ) / (1 + t3 * (2.06189696 + t3 * (1.31912239 + t3 * 0.25077104)))
        name = "nonpositive_rational"
        if t3 < -0.8:
            name = "newton_alternate" if t3 <= -0.97 else "newton_rational"
    return {
        "branch": name,
        "pre_snap_or_rational_G": g,
        "predicates": {
            "t3_le_zero": t3 <= 0,
            "t3_ge_minus_point8": t3 >= -0.8,
            "t3_le_minus_point97": t3 <= -0.97,
            "abs_G_lt_1e5": abs(g) < 1e-5,
        },
    }


def discrimination() -> list:
    """Require deliberate errors to be rejected by the actual checker/reducer."""
    caught = []
    good = errors(0.4, 0.5, True, 0.5)
    fixtures = [
        ("wrong range denominator", {**good, "scale_error": -0.01}, good),
        ("zero confused with baseline", [0.0], [None]),
        ("boolean disguised as number", {"accepted": 1}, {"accepted": True}),
        ("wrong all-draw denominator", 949 / 949, 949 / 1000),
    ]
    for label, wrong, expected in fixtures:
        try:
            equal(wrong, expected, label)
        except AssertionError:
            caught.append(label)
        else:
            raise AssertionError(("mutation escaped", label))
    try:
        add({(0,): good}, (0,), good)
    except AssertionError:
        caught.append("duplicate canonical row")
    rows = [errors(0.1, 0, True, None)] * 949 + [errors(None, 0, False, None)] * 51
    result = summarize((0, 18, 0.9, None), rows)
    equal(result["valid_rate"], 0.949, "949 valid denominator")
    require(not result["scale_pass"], "949 must fail")
    refused = errors(None, 0, False, None)
    require(
        translated((0,), refused, refused)["numerical_pass"] is None, "both refused"
    )
    equal(
        {category(a, b) for a, b in product((False, True), repeat=2)},
        {"both_accepted", "first_only", "second_only", "both_refused"},
        "categories",
    )
    require(len(caught) == 5, "discrimination count")
    return caught


def audit(root: Path, output: Path) -> None:
    """Run the complete retained-data audit into an absent output directory."""
    started = time.perf_counter()
    require(not output.exists(), ("immutable output already exists", output))
    output.mkdir(parents=True)
    evidence = root / "dev/milestones/r12/implementation/evidence"
    stage1 = evidence / "gf15-lmoments-readiness"
    stage2 = evidence / "gf15-lmoments-qualification"
    result = stage2 / "results"
    source_sha = digest(Path(__file__))
    freeze = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_sha,
        "command": sys.argv,
        "python": sys.version,
        "executable": sys.executable,
        "executable_sha256": digest(Path(sys.executable)),
        "packages": {
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        },
        "stage2_inventory_sha256": digest(stage2 / "artifact-inventory.json"),
    }
    write(output / "audit-freeze.json", freeze)
    anchors = {
        "artifact-inventory.json": "404ed2d38185b81692cab8dc144acda4e854ae106a5768f7075d0b31f0556781",
        "results/provenance.json": "3ef0f96b4b8865350d7e657a7303189d5c1b96ed8c1830b5ca4438ebfceaec3c",
        "results/completion.json": "e0586b299381114a9ff20e22bdf1dd9c1a8d670ed90fe210a4e4ae004ee34845",
        "results/mechanical-audit.json": "25bfff7aee0ee4026265ca728d751349d188967e5c1a3b4773aa08168322d600",
        "results/qualification-summary.json": "1f5084379d16e7f17aa732795c8ad81bed62437823d2d8d9efe525d8c3842b00",
    }
    hash_map(stage2, anchors)
    equal(
        inventory(stage2, read(stage2 / "artifact-inventory.json")),
        748,
        "Stage2 inventory",
    )
    provenance = read(result / "provenance.json")
    hash_map(stage1, provenance["readiness"]["anchors"])
    inventory(stage1, read(stage1 / "artifact-inventory.json"))
    signed = read(stage1 / "results/independent/signed-verdict.json")
    equal(signed, provenance["readiness"]["signed_verdict"], "embedded Stage1 verdict")
    hash_map(stage1, signed["source"])
    hash_map(stage1 / "results/attempt-2", signed["control_files"])
    hash_map(stage1 / "results/independent", signed["independent_evidence"])
    hash_map(evidence, signed["input_anchors"])
    equal(
        digest(root / "dev/milestones/r12/gf15-alternative-estimator-design.md"),
        signed["design_sha256"],
        "accepted design",
    )
    equal(
        digest(stage1 / "environment/artifact-inventory.json"),
        signed["environment_inventory_sha256"],
        "environment inventory",
    )
    inventory(
        stage1 / "environment", read(stage1 / "environment/artifact-inventory.json")
    )
    protected = read(stage1 / "environment/protected-files.json")
    equal(len(protected), 177, "protected file count")
    hash_map(root, protected)
    environment = read(result / "environment.json")
    equal(platform.python_version(), environment["python_version"], "Python version")
    equal(freeze["packages"], environment["packages"], "installed versions")
    hash_map(
        Path(environment["module_paths"]["lmoments3"]).parent,
        environment["lmoments3_python_files"],
    )
    equal(
        digest(Path(environment["base_executable"])),
        environment["base_executable_sha256"],
        "base executable",
    )
    for field, name in (
        ("environment_sha256", "environment.json"),
        ("criteria_sha256", "criteria.json"),
        ("input_audit_sha256", "input-audit.json"),
    ):
        equal(digest(result / name), provenance[field], field)
    equal(
        (result / "criteria.json").read_bytes(),
        (evidence / "gf15/results/criteria.json").read_bytes(),
        "A criteria bytes",
    )
    mechanical = read(result / "mechanical-audit.json")
    hash_map(result, mechanical["files"])
    inputs = read(result / "input-audit.json")
    equal(inventory(evidence, inputs["files"]), 733, "selected and preflight inventory")
    predecessor_maps = {}
    for name in ("gf15", "gf15-normalized-qualification"):
        inv = read(evidence / name / "artifact-inventory.json")
        predecessor_maps[name] = {item["path"]: item for item in inv["files"]}
    for item in inputs["files"]:
        name, relative = item["path"].split("/", 1)
        original = predecessor_maps[name][relative]
        equal(item["sha256"], original["sha256"], item["path"])
        equal(item["bytes"], original["bytes"], item["path"])
    mutations = discrimination()
    print(
        "Integrity, signed controls, environment, and discrimination passed", flush=True
    )
    cells = list(
        product(
            (-0.2, 0.0, 0.2),
            (10, 18, 30, 60),
            (0.9, 0.5),
            (None, 0.0, 0.05, 0.5, 2.0, 10.0),
        )
    )
    expected = {
        (c, n, draw, p, ratio) for c, n, p, ratio in cells for draw in range(1000)
    }
    streams = {name: {} for name in "ABC"}
    original_rows = {}
    arrays = {}
    chosen = {"gf15-normalized-qualification/results/preflight.json"}
    for index, c in enumerate((-0.2, 0.0, 0.2)):
        for n in (10, 18, 30, 60):
            relative = f"gf15/results/samples-c{index}-n{n}.npy"
            chosen.add(relative)
            array = np.load(evidence / relative, allow_pickle=False)
            require(array.shape == (1000, n) and array.dtype == np.float64, relative)
            require(bool(np.isfinite(array).all()), relative)
            arrays[c, n] = array
            for start in range(0, 1000, 50):
                a_path = f"gf15/results/draws-c{index}-n{n}-{start:04d}.jsonl.gz"
                b_path = f"gf15-normalized-qualification/results/fits-c{index}-n{n}-{start:04d}.jsonl.gz"
                receipt_path = b_path.removesuffix("l.gz")
                chosen.update((a_path, b_path, receipt_path))
                a_count = 0
                for row in records(evidence / a_path):
                    identity = key(row)
                    require(
                        identity in expected
                        and c == row["shape_c"]
                        and n == row["n"]
                        and start <= row["draw"] < start + 50,
                        (a_path, identity),
                    )
                    equal(row["sigma"], 1.0, identity)
                    evaluated = errors(
                        row["estimate"],
                        row["true_quantile"],
                        row["valid"],
                        row["ratio"],
                    )
                    equal(
                        row["scale_error"],
                        evaluated["scale_error"],
                        ("A scale", identity),
                    )
                    equal(
                        row["relative_error"],
                        evaluated["relative_error"],
                        ("A relative", identity),
                    )
                    add(streams["A"], identity, evaluated)
                    add(original_rows, identity, row)
                    a_count += 1
                equal(a_count, 600, a_path)
                receipt = read(evidence / receipt_path)
                equal(receipt["sha256"], digest(evidence / b_path), b_path)
                equal(
                    receipt["binding"],
                    digest(
                        evidence
                        / "gf15-normalized-qualification/results/preflight.json"
                    ),
                    receipt_path,
                )
                counts = Counter()
                for fit in records(evidence / b_path):
                    counts["fits"] += 1
                    counts["accepted"] += fit["accepted"]
                    counts["evaluations"] += fit["evaluation_count_verified"]
                    probabilities = [0.9, 0.5] if fit["ratio"] is None else [fit["p"]]
                    equal(
                        [q["p"] for q in fit["quantiles"]],
                        probabilities,
                        (b_path, "probabilities"),
                    )
                    for q in fit["quantiles"]:
                        identity = (
                            fit["shape_c"],
                            fit["n"],
                            fit["draw"],
                            q["p"],
                            fit["ratio"],
                        )
                        a = original_rows[identity]
                        equal(fit["mu"], a["mu"], ("B mu", identity))
                        equal(
                            q["true_quantile"],
                            a["true_quantile"],
                            ("B truth", identity),
                        )
                        evaluated = errors(
                            q["estimate"],
                            a["true_quantile"],
                            fit["accepted"],
                            fit["ratio"],
                        )
                        # B retains diagnostic numeric errors even for refused fits.
                        # They never enter accepted cohorts or paired row errors.
                        raw_errors = errors(
                            q["estimate"],
                            a["true_quantile"],
                            q["estimate"] is not None and math.isfinite(q["estimate"]),
                            fit["ratio"],
                        )
                        equal(
                            q["scale_error"],
                            raw_errors["scale_error"],
                            ("B scale", identity),
                        )
                        equal(
                            q["relative_error"],
                            raw_errors["relative_error"],
                            ("B relative", identity),
                        )
                        add(streams["B"], identity, evaluated)
                        counts["quantiles"] += 1
                for name in ("fits", "quantiles", "accepted", "evaluations"):
                    equal(counts[name], receipt[name], (receipt_path, name))
                equal(counts["fits"], 550, b_path)
                equal(counts["quantiles"], 600, b_path)
    equal(
        chosen, {item["path"] for item in inputs["files"]}, "complete selected file set"
    )
    for method in "AB":
        equal(set(streams[method]), expected, (method, "complete canonical key set"))
    canonical_digest = hashlib.sha256(
        "\n".join(
            sorted(json.dumps(k, separators=(",", ":")) for k in expected)
        ).encode()
    ).hexdigest()
    equal(canonical_digest, inputs["canonical_key_set_sha256"], "canonical key digest")
    for method, count_field, valid_field in (
        ("A", "A_keys", "A_valid"),
        ("B", "B_keys", "B_accepted_quantiles"),
    ):
        equal(len(streams[method]), inputs[count_field], count_field)
        equal(
            sum(r["accepted"] for r in streams[method].values()),
            inputs[valid_field],
            valid_field,
        )
    for identity, row in original_rows.items():
        c, n, draw, p, ratio = identity
        base = original_rows[c, n, draw, p, None]
        equal(base["mu"], 0.0, ("baseline offset", identity))
        if ratio is not None:
            equal(
                row["mu"],
                ratio - base["true_quantile"],
                ("translated offset", identity),
            )
            equal(
                row["true_quantile"],
                ratio,
                ("translated truth", identity),
            )
    print(
        "All predecessor records, receipts, sample arrays and complete keys passed",
        flush=True,
    )
    diag = {
        "fits": 0,
        "accepted_fits": 0,
        "branches": dict.fromkeys(
            (
                "preinversion_refusal",
                "positive_snap",
                "positive_rational",
                "nonpositive_rational",
                "newton_rational",
                "newton_alternate",
            ),
            0,
        ),
        "refusals": {},
        "warnings": {},
        "exception_refusals": 0,
        "fit_seconds": 0.0,
        "sample_outside_support_fits": {"normalized": 0, "physical": 0},
        "nonfinite_log_density_fits": {"normalized": 0, "physical": 0},
    }
    diagnostic_cases = []
    chunk_seconds = 0.0
    for index, c in enumerate((-0.2, 0.0, 0.2)):
        for n in (10, 18, 30, 60):
            for start in range(0, 1000, 50):
                chunk = result / f"chunks/c{index}-n{n}-{start:04d}"
                receipt = read(chunk / "receipt.json")
                equal(
                    read(chunk / "binding.json"),
                    {"binding": anchors["results/provenance.json"]},
                    chunk,
                )
                equal(receipt["binding"], anchors["results/provenance.json"], chunk)
                equal(receipt["sha256"], digest(chunk / receipt["file"]), chunk)
                counts = Counter()
                chunk_seconds += receipt["seconds"]
                for fit in records(chunk / receipt["file"]):
                    counts["fits"] += 1
                    counts["accepted_fits"] += fit["accepted"]
                    diag["fits"] += 1
                    diag["accepted_fits"] += fit["accepted"]
                    diag["fit_seconds"] += fit["fit_seconds"]
                    ar = fit["adapter_record"]
                    probabilities = [0.9, 0.5] if fit["ratio"] is None else [fit["p"]]
                    identity = (c, n, fit["draw"], probabilities[0], fit["ratio"])
                    require(
                        c == fit["shape_c"]
                        and n == fit["n"]
                        and start <= fit["draw"] < start + 50,
                        (chunk, identity),
                    )
                    a = original_rows[identity]
                    sample = arrays[c, n][fit["draw"]] + a["mu"]
                    equal(fit["mu"], a["mu"], identity)
                    equal(
                        ar["input"],
                        {
                            "count": n,
                            "sample_sha256": hashlib.sha256(
                                sample.tobytes()
                            ).hexdigest(),
                            "probabilities": probabilities,
                        },
                        (identity, "supplied sample"),
                    )
                    equal(
                        ar["source_sha256"],
                        environment["lmoments3_python_files"]["distr.py"],
                        identity,
                    )
                    normal = ar["normalization"]
                    equal(normal["a"], float(min(sample)), identity)
                    equal(normal["s"], float(max(sample) - min(sample)), identity)
                    equal(
                        normal["y"],
                        ((sample - normal["a"]) / normal["s"]).tolist(),
                        identity,
                    )
                    equal([q["p"] for q in ar["quantiles"]], probabilities, identity)
                    equal([q["p"] for q in fit["quantiles"]], probabilities, identity)
                    accepted = not ar["refusal_reasons"] and all(
                        q["diagnostic_valid"] for q in ar["quantiles"]
                    )
                    equal(ar["accepted"], accepted, (identity, "adapter conjunction"))
                    equal(fit["accepted"], accepted, (identity, "fit conjunction"))
                    for q in ar["quantiles"]:
                        equal(q["accepted"], accepted, (identity, "shared baseline"))
                    equal(ar["warnings"], [], (identity, "warnings"))
                    equal(ar["refusal_reasons"], [], (identity, "refusals"))
                    require(not ar.get("exception"), (identity, "exception"))
                    classified = branch(ar["moments"]["t3"])
                    equal(fit["branch"], classified, (identity, "branch"))
                    diag["branches"][classified["branch"]] += 1
                    for coordinate in ("normalized", "physical"):
                        params = ar[f"{coordinate}_parameters"]
                        require(
                            all(math.isfinite(v) for v in params.values())
                            and params["c"] > -1
                            and params["scale"] > 0,
                            identity,
                        )
                        sample_values = (
                            np.asarray(normal["y"])
                            if coordinate == "normalized"
                            else sample
                        )
                        support = 1 - params["c"] * (
                            (sample_values - params["loc"]) / params["scale"]
                        )
                        d = ar[f"{coordinate}_diagnostics"]
                        # SciPy includes the finite endpoint in support membership.
                        outside = int(np.count_nonzero(support < 0))
                        equal(
                            d["sample_outside_support"],
                            outside,
                            (identity, coordinate, "support"),
                        )
                        equal(
                            len(d["log_density"]),
                            n,
                            (identity, coordinate, "log density length"),
                        )
                        nonfinite = sum(
                            not math.isfinite(float(v)) for v in d["log_density"]
                        )
                        equal(
                            d["nonfinite_log_density_count"],
                            nonfinite,
                            (identity, coordinate),
                        )
                        diag["sample_outside_support_fits"][coordinate] += outside > 0
                        diag["nonfinite_log_density_fits"][coordinate] += nonfinite > 0
                        if outside or nonfinite:
                            diagnostic_cases.append(
                                {
                                    "key": list(identity),
                                    "coordinate": coordinate,
                                    "outside": outside,
                                    "nonfinite": nonfinite,
                                }
                            )
                    for q, aq in zip(fit["quantiles"], ar["quantiles"], strict=True):
                        identity = key(q)
                        equal(
                            identity,
                            (c, n, fit["draw"], aq["p"], fit["ratio"]),
                            "candidate quantile-to-fit ownership",
                        )
                        a = original_rows[identity]
                        equal(q["mu"], a["mu"], identity)
                        equal(q["accepted"], accepted, identity)
                        equal(q["estimate"], aq["estimate"], identity)
                        equal(q["true_quantile"], a["true_quantile"], identity)
                        equal(q["sigma_generator"], 1.0, identity)
                        evaluated = errors(
                            aq["estimate"], a["true_quantile"], accepted, fit["ratio"]
                        )
                        equal(q["scale_error"], evaluated["scale_error"], identity)
                        equal(
                            q["relative_error"], evaluated["relative_error"], identity
                        )
                        add(streams["C"], identity, evaluated)
                        counts["quantiles"] += 1
                for name in ("fits", "quantiles", "accepted_fits"):
                    equal(counts[name], receipt[name], (chunk, name))
                equal(counts["fits"], 550, chunk)
                equal(counts["quantiles"], 600, chunk)
            print(f"Candidate raw records checked: c={c}, n={n}", flush=True)
    equal(set(streams["C"]), expected, "C complete canonical keys")
    equal(diag, read(result / "diagnostics.json"), "diagnostics")
    controls = read(stage1 / "results/attempt-2/numerical-controls.json")
    covered = {row["identity"]["branch"] for row in controls["branches"]}
    reached = {name for name, count in diag["branches"].items() if count}
    require(reached <= covered, ("uncovered reached branch", reached - covered))
    individual = {method: [] for method in "ABC"}
    paired = {pair: [] for pair in ("AB", "AC", "BC")}
    translation_cells = []
    for cell in cells:
        c, n, p, ratio = cell
        keys = [(c, n, draw, p, ratio) for draw in range(1000)]
        for method in "ABC":
            individual[method].append(
                summarize(cell, [streams[method][k] for k in keys])
            )
        for pair in paired:
            first, second = pair
            cats = dict.fromkeys(
                ("both_accepted", "first_only", "second_only", "both_refused"), 0
            )
            retained = []
            for k in keys:
                cat = category(
                    streams[first][k]["accepted"], streams[second][k]["accepted"]
                )
                cats[cat] += 1
                if cat == "both_accepted":
                    retained.append(k)
            paired[pair].append(
                {
                    **cell_header(cell),
                    "all_draws": 1000,
                    "categories": cats,
                    "intersection_count": len(retained),
                    "retained_draw_ids": [k[2] for k in retained],
                    "intersection_errors": {
                        method: {
                            "scale": describe(
                                [streams[method][k]["scale_error"] for k in retained]
                            ),
                            "relative": describe(
                                [streams[method][k]["relative_error"] for k in retained]
                            )
                            if ratio not in (None, 0)
                            else None,
                        }
                        for method in pair
                    },
                }
            )
        if ratio is not None:
            pairs = [
                translated(k, streams["C"][c, n, k[2], p, None], streams["C"][k])
                for k in keys
            ]
            cats = dict(Counter(row["category"] for row in pairs))
            unchanged = all(row["acceptance_unchanged"] for row in pairs)
            failures = sum(row["numerical_pass"] is False for row in pairs)
            translation_cells.append(
                {
                    **cell_header(cell),
                    "all_draws": 1000,
                    "categories": cats,
                    "acceptance_unchanged": unchanged,
                    "numerical_passes": sum(
                        row["numerical_pass"] is True for row in pairs
                    ),
                    "numerical_failures": failures,
                    "translation_pass": unchanged
                    and failures == 0
                    and cats.get("both_accepted", 0) >= 950,
                }
            )
    equal(individual, read(result / "individual-cells.json"), "all individual cells")
    equal(paired, read(result / "paired-cells.json"), "all paired cells")
    equal(
        {"cells": translation_cells},
        read(result / "translation-cells.json"),
        "translation cells",
    )
    pair_seen = set()
    for row in records(result / "paired-keys.jsonl.gz"):
        pair, identity = row["pair"], tuple(row["key"])
        require(pair in paired and identity in expected, ("paired illegal key", row))
        require((pair, identity) not in pair_seen, ("duplicate paired row", row))
        pair_seen.add((pair, identity))
        first, second = pair
        equal(
            row,
            {
                "pair": pair,
                "key": list(identity),
                "category": category(
                    streams[first][identity]["accepted"],
                    streams[second][identity]["accepted"],
                ),
                first: streams[first][identity],
                second: streams[second][identity],
            },
            ("paired row", pair, identity),
        )
    equal(len(pair_seen), 432000, "complete paired rows")
    trans_seen = set()
    max_delta = 0.0
    trans_cats = dict.fromkeys(
        ("both_accepted", "first_only", "second_only", "both_refused"), 0
    )
    trans_failures = 0
    for row in records(result / "translation-pairs.jsonl.gz"):
        identity = tuple(row["key"])
        c, n, draw, p, ratio = identity
        require(
            identity in expected and ratio is not None and identity not in trans_seen,
            identity,
        )
        trans_seen.add(identity)
        recalculated = translated(
            identity, streams["C"][c, n, draw, p, None], streams["C"][identity]
        )
        equal(row, recalculated, ("translation row", identity))
        trans_cats[row["category"]] += 1
        trans_failures += row["numerical_pass"] is False
        if row["delta_scale_error"] is not None:
            max_delta = max(max_delta, abs(row["delta_scale_error"]))
    equal(len(trans_seen), 120000, "complete translation pairs")
    outcomes = {}
    for method, rows in individual.items():
        outcomes[method] = {
            "accepted_quantiles": sum(row["accepted_count"] for row in rows),
            "baseline_scale_passed": sum(
                row["scale_pass"] for row in rows if row["ratio"] is None
            ),
            "baseline_cells": 24,
            "all_scale_passed": sum(row["scale_pass"] for row in rows),
            "eligible_scale_and_relative_passed": sum(
                row["individual_gate_pass"] for row in rows if row["relative_eligible"]
            ),
            "eligible_cells": 72,
            "all_individual_gates_passed": all(
                row["individual_gate_pass"] for row in rows
            ),
        }
    summary = read(result / "qualification-summary.json")
    equal(summary["individual_outcomes"], outcomes, "overall outcomes")
    translations = {
        "categories": trans_cats,
        "numeric_failures": trans_failures,
        "max_absolute_delta_scale_error": max_delta,
        "passed_cells": sum(row["translation_pass"] for row in translation_cells),
        "cells": 120,
    }
    equal(summary["translation"], translations, "overall translation")
    counts = {
        "fits": diag["fits"],
        "quantiles": len(streams["C"]),
        "individual_cells_per_estimator": 144,
        "translation_pairs": len(trans_seen),
        "pairwise_rows": len(pair_seen),
    }
    equal(summary["counts"], counts, "summary counts")
    conjunction = outcomes["C"]["all_individual_gates_passed"] and all(
        row["translation_pass"] for row in translation_cells
    )
    equal(summary["mechanical_gate_conjunction"], conjunction, "conjunction")
    completion = read(result / "completion.json")
    equal(completion["counts"], counts, "completion counts")
    equal(
        completion["mechanical_gate_conjunction"], conjunction, "completion conjunction"
    )
    equal(completion["chunk_seconds"], chunk_seconds, "chunk timing")
    hash_map(stage2, anchors)
    hash_map(root, protected)
    require(digest(Path(__file__)) == source_sha, "auditor changed during audit")
    write(output / "individual-cells.json", individual)
    write(output / "paired-cells.json", paired)
    write(output / "translation-cells.json", {"cells": translation_cells})
    write(output / "diagnostic-cases.json", diagnostic_cases)
    write(
        output / "audit-results.json",
        {
            "status": "complete_independent_audit_passed",
            "scientific_gate_conjunction": conjunction,
            "comparison_policy": "Exact decoded values, including all floats; no numerical tolerance or gate waiver.",
            "counts": counts,
            "stage2_files_rehashed": 749,
            "protected_files": 177,
            "selected_predecessor_files": 732,
            "additional_preflight": 1,
            "chunk_receipts": 240,
            "installed_lmoments3_sources": 6,
            "individual_outcomes": outcomes,
            "translation": translations,
            "diagnostics": diag,
            "reached_branches": sorted(reached),
            "signed_control_branches": sorted(covered),
            "discrimination_detected": mutations,
            "all_432_individual_and_432_paired_cells_exact": True,
            "all_432000_pair_and_120000_translation_rows_exact": True,
            "new_fits": 0,
            "seconds": time.perf_counter() - started,
            "source_sha256": source_sha,
            "input_anchors": anchors,
        },
    )
    write(
        output / "artifact-inventory.json",
        [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
            for path in sorted(output.iterdir())
            if path.is_file()
        ],
    )
    print(
        "COMPLETE: exact independent audit passed; candidate qualification="
        + str(conjunction),
        flush=True,
    )


def write(path: Path, value: Any) -> None:
    """Create a result exclusively; never overwrite an existing artifact."""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(Path.cwd(), args.output)
