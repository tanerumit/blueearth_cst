"""Execute fixed GF15 Stage 1 checks; never execute the candidate matrix."""

import argparse
import gzip
import hashlib
import importlib.metadata
import json
import math
import os
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path

import candidate_adapter as adapter
import numpy as np
from lmoments3 import distr
from reference_oracle import (
    CONSTANT_SOURCES,
    EULER,
    PI,
    Interval,
    cdf_enclosure,
    log_cdf_standard,
    parameter_reference,
    population_moments,
    tau,
)
from scipy.stats import genextreme

ROOT = Path(__file__).resolve().parent
ANCHORS = {
    "gf15/artifact-inventory.json": "3f13145d29c377a1c92042b3845695ce293edd58e565e17a67851767026719e1",
    "gf15-normalized-qualification/artifact-inventory.json": "07148bb3b165ef2d1785fb49fc57908d260009cd7885c7b39712e1148aefdf4a",
    "gf15/results/criteria.json": "988611b6d239b95f7542f8d67470395e4997ac61dd97198fd075fdcba552d643",
    "gf15/results/provenance.json": "0d85d2a63c6be70683e2a1485de7bfc6266a265fd383cf96b124b6facdc67db2",
    "gf15-normalized-qualification/results/provenance.json": "a1ea18808890a1c270e75a35441b1bb4eecdb901551c6fafce0565be822686ae",
}


def sha(path: Path) -> str:
    """Hash exact file bytes without modifying the source."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    """Read UTF-8 JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path):
    """Stream all retained rows, including refusals."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def canonical_key(row: dict) -> tuple:
    """Keep null baseline and translated zero distinct in the canonical key."""
    return tuple(row[name] for name in ("shape_c", "n", "draw", "p", "ratio"))


def insert_unique(table: dict, row: dict) -> None:
    """Fail closed on malformed or duplicate retained keys."""
    key = canonical_key(row)
    if type(row["draw"]) is not int or not 0 <= row["draw"] <= 999:
        raise ValueError("illegal draw ID")
    if key in table:
        raise ValueError(f"duplicate key: {key}")
    table[key] = row


def validate_key_coverage(actual: set, expected: set) -> None:
    """Refuse dropped, added or altered keys."""
    if actual != expected:
        raise ValueError("incomplete canonical key coverage")


def validate_receipt(
    receipt: dict, filename: str, digest: str, binding: str, counts: tuple
) -> None:
    """Validate exact predecessor receipt bindings and executed row counts."""
    if (
        receipt["file"] != filename
        or receipt["sha256"] != digest
        or receipt["binding"] != binding
    ):
        raise ValueError("receipt binding/hash mismatch")
    if counts != tuple(
        receipt[k] for k in ("fits", "quantiles", "accepted", "evaluations")
    ) or counts[:2] != (550, 600):
        raise ValueError("receipt count mismatch")


def validate_paired_truth(a: dict, b: dict) -> None:
    """Preserve independently loaded A truth/offsets and original status semantics."""
    if (
        a["mu"] != b["mu"]
        or a["true_quantile"] != b["true_quantile"]
        or a["sigma"] != 1
    ):
        raise ValueError("inconsistent truth/offset")


def audit_inputs() -> dict:
    """Audit every selected file, receipt and both full predecessor key sets."""
    evidence = ROOT.parent
    for name, expected in ANCHORS.items():
        if sha(evidence / name) != expected:
            raise ValueError(f"anchor mismatch: {name}")
    inventories = {
        label: {
            row["path"]: row
            for row in read_json(evidence / label / "artifact-inventory.json")["files"]
        }
        for label in ("gf15", "gf15-normalized-qualification")
    }

    checked = []

    def verify(label: str, name: str) -> Path:
        record = inventories[label][name]
        path = evidence / label / name
        actual = sha(path)
        if actual != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"inventory mismatch: {path}")
        checked.append({**record, "path": f"{label}/{name}"})
        return path

    a_rows, b_rows = {}, {}
    expected_keys = set()
    b_binding = sha(verify("gf15-normalized-qualification", "results/preflight.json"))
    for index, shape in enumerate((-0.2, 0.0, 0.2)):
        for count in (10, 18, 30, 60):
            sample_path = verify("gf15", f"results/samples-c{index}-n{count}.npy")
            samples = np.load(sample_path, allow_pickle=False)
            if samples.shape != (1000, count) or samples.dtype != np.float64:
                raise ValueError("invalid retained sample array")
            for draw in range(1000):
                for probability in (0.5, 0.9):
                    for ratio in (None, 0.0, 0.05, 0.5, 2.0, 10.0):
                        expected_keys.add((shape, count, draw, probability, ratio))
            for start in range(0, 1000, 50):
                suffix = f"c{index}-n{count}-{start:04d}"
                for row in rows(verify("gf15", f"results/draws-{suffix}.jsonl.gz")):
                    insert_unique(a_rows, row)
                chunk = verify(
                    "gf15-normalized-qualification", f"results/fits-{suffix}.jsonl.gz"
                )
                receipt = read_json(
                    verify(
                        "gf15-normalized-qualification", f"results/fits-{suffix}.json"
                    )
                )
                fits = quantiles = accepted = evaluations = 0
                for fit in rows(chunk):
                    fits += 1
                    accepted += fit["accepted"]
                    evaluations += fit["evaluation_count_verified"]
                    expected_probabilities = (
                        {0.5, 0.9} if fit["ratio"] is None else {fit["p"]}
                    )
                    if {
                        q["p"] for q in fit["quantiles"]
                    } != expected_probabilities or len(fit["quantiles"]) != len(
                        expected_probabilities
                    ):
                        raise ValueError("wrong B quantile membership")
                    for quantile in fit["quantiles"]:
                        quantiles += 1
                        row = {
                            name: fit[name]
                            for name in (
                                "shape_c",
                                "n",
                                "draw",
                                "ratio",
                                "mu",
                                "accepted",
                            )
                        }
                        row.update(
                            {
                                name: quantile[name]
                                for name in (
                                    "p",
                                    "true_quantile",
                                    "estimate",
                                    "scale_error",
                                    "relative_error",
                                )
                            }
                        )
                        insert_unique(b_rows, row)
                validate_receipt(
                    receipt,
                    chunk.name,
                    sha(chunk),
                    b_binding,
                    (fits, quantiles, accepted, evaluations),
                )
    validate_key_coverage(set(a_rows), expected_keys)
    validate_key_coverage(set(b_rows), expected_keys)
    if len(expected_keys) != 144000:
        raise ValueError("wrong full key population size")
    for key, a in a_rows.items():
        b = b_rows[key]
        validate_paired_truth(a, b)
        if a["ratio"] is None:
            other = (*key[:3], 0.9 if key[3] == 0.5 else 0.5, None)
            if a["mu"] != a_rows[other]["mu"]:
                raise ValueError("inconsistent baseline offsets")
        else:
            baseline = a_rows[(*key[:4], None)]
            if a["mu"] != a["ratio"] - baseline["true_quantile"]:
                raise ValueError("translated offset mismatch")
    return {
        "anchors": ANCHORS,
        "files": checked,
        "A_keys": len(a_rows),
        "B_keys": len(b_rows),
        "canonical_key_set_sha256": hashlib.sha256(
            "\n".join(
                sorted(json.dumps(key, separators=(",", ":")) for key in expected_keys)
            ).encode()
        ).hexdigest(),
        "selected_file_count": len(checked) - 1,
        "additional_preflight_files": 1,
        "A_valid": sum(row["valid"] for row in a_rows.values()),
        "B_accepted_quantiles": sum(row["accepted"] for row in b_rows.values()),
        "candidate_fits": 0,
        "mapping": {
            "key": ["shape_c", "n", "draw", "p", "ratio"],
            "A_acceptance": "valid",
            "B_acceptance": "accepted",
            "B_flattening": "exactly once per nested quantile",
            "sample": "retained A.samples[draw] + A.mu",
            "baseline": "ratio=null; distinct from 0",
        },
    }


def bits(value: float) -> str:
    """Freeze IEEE 754 binary64 in portable big-endian hexadecimal."""
    return struct.pack(">d", float(value)).hex()


def quantile_gate(
    parameters: dict,
    p: float,
    output: float,
    normalization_scale: float,
    normalized_output: float,
) -> dict:
    """Compare exact output to two forward-CDF enclosures without extra allowance."""
    with localcontext() as context:
        context.prec = 120
        returned = Decimal.from_float(output)
        s = Decimal.from_float(normalization_scale)
        magnitude = max(Decimal(1), abs(Decimal.from_float(normalized_output)))
        tolerance = Decimal("1e-10") * magnitude
        passes = [
            cdf_enclosure(parameters, p, Decimal("1e-30") * magnitude * s, precision)
            for precision in (80, 120)
        ]
        intervals = [tuple(map(Decimal, item["enclosure"])) for item in passes]
        if max(a for a, _ in intervals) > min(b for _, b in intervals):
            raise ArithmeticError("nonoverlapping CDF precision enclosures")
        lower = min(a for a, _ in intervals)
        upper = max(b for _, b in intervals)
        if (upper - lower) / s > Decimal("2e-30") * magnitude:
            raise ArithmeticError("CDF hull width exceeds budget")
        maximum = max(abs(returned - lower), abs(returned - upper)) / s
        minimum = max(lower - returned, returned - upper, Decimal(0)) / s
        outcome = (
            "pass"
            if maximum <= tolerance
            else "fail"
            if minimum > tolerance
            else "unresolved"
        )
        before, after = (
            Decimal.from_float(math.nextafter(output, direction))
            for direction in (-math.inf, math.inf)
        )
        cell = [(before + returned) / 2, (returned + after) / 2]
        c, loc, scale = (
            Decimal.from_float(parameters[k]) for k in ("c", "loc", "scale")
        )
        endpoint = None if c == 0 else loc + scale / c
        inside = endpoint is None or (
            returned <= endpoint if c > 0 else returned >= endpoint
        )
        intersects = endpoint is None or (
            cell[0] < endpoint if c > 0 else cell[1] > endpoint
        )
        if not intersects:
            outcome = "unsupported"
        if outcome != "pass":
            raise ArithmeticError(
                f"quantile gate {outcome}: c={c}, p={p}, error={minimum}:{maximum}, T={tolerance}"
            )
        standardized = (Interval.point(output) - loc) / scale
        probability_residual = log_cdf_standard(standardized, c).exp() - Interval.point(
            p
        )
        display = float((lower + upper) / 2)
        return {
            "parameters": parameters,
            "parameter_bits": {k: bits(v) for k, v in parameters.items()},
            "p": p,
            "p_bits": bits(p),
            "output": output,
            "output_bits": bits(output),
            "precision_passes": passes,
            "hull": [str(lower), str(upper)],
            "normalized_width": str((upper - lower) / s),
            "T_normalized": str(tolerance),
            "normalized_minimum_error": str(minimum),
            "normalized_maximum_error": str(maximum),
            "normalization_scale": normalization_scale,
            "endpoint": None if endpoint is None else str(endpoint),
            "inside_support": inside,
            "rounding_cell_intersects_support": intersects,
            "rounding_cell": list(map(str, cell)),
            "ties_to_even_includes_midpoints": int(bits(output), 16) % 2 == 0,
            "reference_display_float": display,
            "display_half_ulp_bound": str(Decimal.from_float(math.ulp(display)) / 2),
            "probability_residual_diagnostic_interval": probability_residual.record(),
            "display_rounding_not_added_to_T": True,
            "outcome": outcome,
        }


def branch_identity(t3: float) -> dict:
    """Repeat pinned branch predicates and pre-snap G solely for characterization."""
    if t3 <= 0:
        g = (
            0.28377530
            + t3
            * (-1.21096399 + t3 * (-2.50728214 + t3 * (-1.13455566 + t3 * -0.07138022)))
        ) / (1 + t3 * (2.06189696 + t3 * (1.31912239 + t3 * 0.25077104)))
        branch = (
            "nonpositive_rational"
            if t3 >= -0.8
            else "newton_alternate"
            if t3 <= -0.97
            else "newton_rational"
        )
    else:
        z = 1 - t3
        g = (-1 + z * (1.59921491 + z * (-0.48832213 + z * 0.01573152))) / (
            1 + z * (-0.64363929 + z * 0.08985247)
        )
        branch = "positive_snap" if abs(g) < 1e-5 else "positive_rational"
    return {
        "branch": branch,
        "pre_snap_or_rational_G": g,
        "predicates": {
            "t3_le_zero": t3 <= 0,
            "t3_ge_minus_point8": t3 >= -0.8,
            "t3_le_minus_point97": t3 <= -0.97,
            "abs_G_lt_1e5": abs(g) < 1e-5,
        },
    }


def traced_source_fit(moments: list[float], identity: dict) -> tuple[dict, dict]:
    """Observe executed pinned-library lines without modifying estimator locals."""
    events = []

    def trace(frame, event, arg):
        if frame.f_code is distr.GenextremeGen._lmom_fit.__code__ and event == "line":
            events.append({"line": frame.f_lineno, "G": frame.f_locals.get("G")})
        return trace

    previous = sys.gettrace()
    sys.settrace(trace)
    try:
        fitted = dict(distr.gev.lmom_fit(lmom_ratios=moments))
    finally:
        sys.settrace(previous)
    reached = {row["line"] for row in events}
    expected = {
        "positive_snap": 1347,
        "positive_rational": 1351,
        "nonpositive_rational": 1315,
        "newton_alternate": 1322,
        "newton_rational": 1324,
    }[identity["branch"]]
    if expected not in reached or (
        identity["branch"] == "newton_rational" and 1322 in reached
    ):
        raise ArithmeticError("actual library branch differs from recorded predicate")
    if moments[2] > 0:
        actual_g = next(row["G"] for row in events if row["line"] == 1346)
        if actual_g != identity["pre_snap_or_rational_G"]:
            raise ArithmeticError("actual pre-snap G differs from source coefficients")
    return fitted, {
        "events": events,
        "required_line": expected,
        "installed_file_sha256": adapter.DISTR_SHA256,
    }


def numerical_controls() -> dict:
    """Execute population gates before freezing branch and same-float CDF controls."""
    population = []
    cases = []
    for shape_text in ("-.2", ".2", "0"):
        references = []
        for precision in (80, 120):
            with localcontext() as context:
                context.prec = precision
                moments, evidence = population_moments(Decimal(shape_text))
                references.append(
                    {
                        "precision": precision,
                        "moments": list(map(str, moments)),
                        "gamma_evidence": evidence,
                    }
                )
        if any(
            abs(Decimal(a) - Decimal(b)) > Decimal("1e-30")
            for a, b in zip(references[0]["moments"], references[1]["moments"])
        ):
            raise ArithmeticError("population reference precision mismatch")
        rounded = list(map(float, references[0]["moments"]))
        fitted = adapter._parameters(rounded)
        errors = {
            "c": abs(fitted["c"] - float(shape_text)),
            "loc": abs(fitted["loc"]),
            "scale": abs(fitted["scale"] - 1),
        }
        population.append(
            {
                "shape": shape_text,
                "precision_passes": references,
                "rounded_moments": rounded,
                "moment_bits": list(map(bits, rounded)),
                "fitted": fitted,
                "errors": errors,
                "passed": all(value <= 1e-5 for value in errors.values()),
            }
        )
        cases.append((f"population_{shape_text}", rounded, fitted))
    if not all(row["passed"] for row in population):
        raise ArithmeticError(f"original population gate failed: {population}")
    with localcontext() as context:
        context.prec = 120
        fixed = [
            ("positive_.50", Decimal(".50")),
            ("positive_tau_.2", tau(Decimal(".2"))),
        ]
        fixed += [
            (f"snap_tau_{c}", tau(Decimal(c)))
            for c in ("0", "-.000005", ".000005", "-.00002", ".00002")
        ]
        fixed += [
            (f"literal_{t}", Decimal(t))
            for t in (
                "-.000001",
                "0",
                ".000001",
                "-.30",
                "-.799999",
                "-.8",
                "-.800001",
                "-.85",
                "-.969999",
                "-.97",
                "-.970001",
                "-.98",
            )
        ]
    branches = []
    for label, exact in fixed:
        moments = [0.0, 1.0, float(exact)]
        fitted = adapter._parameters(moments)
        identity = branch_identity(moments[2])
        direct, source_trace = traced_source_fit(moments, identity)
        if fitted != direct or (
            (fitted["c"] == 0) != (identity["branch"] == "positive_snap")
        ):
            raise ArithmeticError("branch/source fidelity mismatch")
        references = [
            parameter_reference(moments, precision) for precision in (80, 120)
        ]
        if abs(
            Decimal(references[0]["parameters"]["c"])
            - Decimal(references[1]["parameters"]["c"])
        ) > Decimal("1e-35"):
            raise ArithmeticError("shape roots disagree beyond 1e-35")
        for name in ("c", "loc", "scale"):
            if abs(
                Decimal(references[0]["parameters"][name])
                - Decimal(references[1]["parameters"][name])
            ) > Decimal("1e-30"):
                raise ArithmeticError("branch parameter reference precision mismatch")
        with localcontext() as context:
            context.prec = 120
            reference = {k: Decimal(v) for k, v in references[1]["parameters"].items()}
            errors = {
                k: str(
                    abs(Decimal.from_float(fitted[k]) - reference[k])
                    / (1 if k == "c" else reference["scale"])
                )
                for k in reference
            }
        branches.append(
            {
                "label": label,
                "exact_t3_input": str(exact),
                "rounded_moments": moments,
                "moment_bits": list(map(bits, moments)),
                "fitted": fitted,
                "identity": identity,
                "references": references,
                "discrepancies": errors,
                "reference_line": 1e-5,
                "disposition": "population_gated_shape_overlap"
                if label == "positive_tau_.2"
                else "characterization_only",
                "source_exact": True,
                "source_trace": source_trace,
            }
        )
        cases.append((label, moments, fitted))
    quantiles = []
    for label, moments, parameters in cases:
        for probability in (0.5, 0.9):
            normalized = adapter._quantile(parameters, probability)
            scipy_quantile = float(genextreme.ppf(probability, **parameters))
            if abs(normalized - scipy_quantile) > 1e-10 * max(1, abs(normalized)):
                raise ArithmeticError("SciPy mapping/sign control failed")
            normalized_record = quantile_gate(
                parameters, probability, normalized, 1.0, normalized
            )
            # Fixed positive affine map; physical parameters and output round separately.
            a, s = np.float64(7.25), np.float64(3.5)
            physical = {
                "c": parameters["c"],
                "loc": float(a + s * parameters["loc"]),
                "scale": float(s * parameters["scale"]),
            }
            output = float(a + s * normalized)
            physical_record = quantile_gate(
                physical, probability, output, float(s), normalized
            )
            quantiles.append(
                {
                    "label": label,
                    "normalized": normalized_record,
                    "physical": physical_record,
                    "scipy_quantile": scipy_quantile,
                }
            )
    return {
        "population": population,
        "branches": branches,
        "quantiles": quantiles,
        "constants": {"pi": str(PI), "euler": str(EULER), "sources": CONSTANT_SOURCES},
        "matrix_fits": 0,
    }


def summarize_synthetic(
    rows_to_reduce: list[dict], probability: float, ratio: float | None
) -> dict:
    """Exercise unchanged D3 semantics on synthetic rows, never qualify a matrix."""
    criteria = read_json(ROOT.parent / "gf15/results/criteria.json")
    accepted = [row["error"] for row in rows_to_reduce if row["accepted"]]
    if len(rows_to_reduce) != 1000:
        raise ValueError("D3 all-draw denominator must be 1000")
    values = np.asarray(accepted, dtype=np.float64)
    median = float(np.quantile(values, 0.5, method="linear")) if accepted else None
    absolute_median = (
        float(np.quantile(abs(values), 0.5, method="linear")) if accepted else None
    )
    p90 = float(np.quantile(abs(values), 0.9, method="linear")) if accepted else None
    relative = (
        None
        if ratio in (None, 0) or not accepted
        else {"median": median / abs(ratio), "p90_absolute": p90 / abs(ratio)}
    )
    valid_rate = len(accepted) / 1000
    scale_pass = bool(
        accepted
        and valid_rate >= criteria["valid_rate_min"]
        and abs(median) <= criteria["median_scale_abs_max"]
        and p90 <= criteria["p90_abs_scale_max"][str(probability)]
    )
    relative_pass = (
        None
        if ratio not in criteria["relative_qualified_ratios"]
        else bool(
            relative
            and abs(relative["median"]) <= criteria["median_relative_abs_max"]
            and relative["p90_absolute"]
            <= criteria["p90_abs_relative_max"][str(probability)]
        )
    )
    return {
        "valid_rate": valid_rate,
        "accepted_count": len(accepted),
        "all_draws": 1000,
        "median": median,
        "median_absolute": absolute_median,
        "p90_absolute": p90,
        "relative": relative,
        "scale_pass": scale_pass,
        "relative_pass": relative_pass,
        "synthetic_only": True,
    }


def comparison_category(first: bool, second: bool) -> str:
    """Keep four acceptance categories; both-refused is never a numeric pass."""
    return {
        (True, True): "both_accepted",
        (True, False): "first_only",
        (False, True): "second_only",
        (False, False): "both_refused",
    }[(first, second)]


def write_json_exclusive(path: Path, value: dict) -> None:
    """Publish immutable UTF-8 JSON without overwriting an existing file."""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def write_atomic_completion(path: Path, value: dict) -> None:
    """Expose completion only after its exact payload has been flushed."""
    pending = path.with_suffix(".pending")
    write_json_exclusive(pending, value)
    pending.rename(path)


def fixed_binding(inputs: dict) -> str:
    """Hash actual fixed inputs together with current authored/environment identities."""
    bound = {
        "inputs": inputs,
        "sources": {path.name: sha(path) for path in ROOT.glob("*.py")},
        "environment": sha(ROOT / "environment/artifact-inventory.json"),
        "predecessor_anchors": ANCHORS,
    }
    return hashlib.sha256(
        json.dumps(bound, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def fixed_chunk(namespace: Path, binding: str, compute) -> dict:
    """Exercise local single-writer atomic fixed chunks, not managed run-control."""
    if len(binding) != 64 or any(c not in "0123456789abcdef" for c in binding):
        raise ValueError("chunk binding must be a SHA-256 digest")
    namespace.mkdir(exist_ok=True)
    owner = namespace / "writer.claim"
    descriptor = os.open(owner, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    try:
        intent = namespace / "binding.json"
        if intent.exists():
            if read_json(intent) != {"binding": binding}:
                raise ValueError("conflicting chunk binding")
        else:
            write_json_exclusive(intent, {"binding": binding})
        payload, receipt = namespace / "payload.json", namespace / "receipt.json"
        if receipt.exists():
            record = read_json(receipt)
            if not payload.exists() or record != {
                "binding": binding,
                "sha256": sha(payload),
            }:
                raise ValueError("inconsistent completion receipt")
            return {"action": "reused", "payload": read_json(payload)}
        if payload.exists():
            raise ValueError("unreceipted completed payload requires review")
        if (namespace / "receipt.partial").exists():
            raise ValueError("inconsistent partial receipt")
        result = compute()
        pending = namespace / "payload.partial"
        if pending.exists():
            pending.unlink()
        write_json_exclusive(pending, result)
        pending.rename(payload)
        receipt_partial = namespace / "receipt.partial"
        write_json_exclusive(
            receipt_partial, {"binding": binding, "sha256": sha(payload)}
        )
        receipt_partial.rename(receipt)
        return {"action": "computed", "payload": result}
    finally:
        owner.unlink()


def verify_environment_and_protected() -> dict:
    """Verify frozen effective runtime, installed source and protected repo bytes."""
    environment = ROOT / "environment"
    for row in read_json(environment / "artifact-inventory.json"):
        path = environment / row["path"]
        if sha(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError("environment metadata changed")
    effective = read_json(environment / "effective-environment.json")
    if sys.version.split()[0] != effective["python_version"]:
        raise ValueError("Python version changed")
    for package, version in effective["packages"].items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"effective package changed: {package}")
    import lmoments3

    package_root = Path(lmoments3.__file__).parent
    for name, expected in effective["lmoments3_python_files"].items():
        if sha(package_root / name) != expected:
            raise ValueError("installed lmoments3 source changed")
    protected = read_json(environment / "protected-files.json")
    for name, expected in protected.items():
        if sha(ROOT.parents[5] / name) != expected:
            raise ValueError(f"protected path changed: {name}")
    return {
        "protected_files": len(protected),
        "installed_lmoments3_sources": len(effective["lmoments3_python_files"]),
        "runtime_versions": effective["packages"],
    }


def freeze_attempt(output: Path) -> dict:
    """Claim absent output and freeze source/environment before final controls."""
    output.mkdir(parents=False, exist_ok=False)
    verified = verify_environment_and_protected()
    source = {
        path.name: sha(path)
        for path in ROOT.iterdir()
        if path.suffix == ".py" or path.name == "README.md"
    }
    manifest = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "source": source,
        "environment_inventory_sha256": sha(
            ROOT / "environment/artifact-inventory.json"
        ),
        "input_anchors": ANCHORS,
        "expected_outputs": [
            "input-audit.json",
            "numerical-controls.json",
            "test-controls.log",
            "criteria.json",
            "completion.json",
        ],
        "matrix_authorized": False,
        "stage": "Stage 1 implementation readiness only",
        "verified_before": verified,
    }
    write_json_exclusive(output / "attempt.json", manifest)
    return manifest


def main() -> int:
    """Run an explicitly selected bounded readiness operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["audit-inputs", "numerical-controls", "run-fixed"]
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scratch", type=Path)
    args = parser.parse_args()
    if args.command == "run-fixed":
        if args.scratch is None:
            parser.error(
                "run-fixed requires an explicit disposable --scratch directory"
            )
        args.scratch.mkdir(parents=False, exist_ok=False)
        manifest = freeze_attempt(args.output)
        start = time.monotonic()
        try:
            write_json_exclusive(args.output / "input-audit.json", audit_inputs())
            (args.output / "criteria.json").write_bytes(
                (ROOT.parent / "gf15/results/criteria.json").read_bytes()
            )
            with (args.output / "test-controls.log").open(
                "x", encoding="utf-8"
            ) as stream:
                subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-m",
                        "pytest",
                        str(ROOT / "test_readiness.py"),
                        "-v",
                        "-s",
                        "-o",
                        f"cache_dir={args.scratch / 'test-cache'}",
                        "--basetemp",
                        str(args.scratch / "test-work"),
                    ],
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
            numerical = numerical_controls()
            replay = numerical_controls()
            if numerical != replay:
                raise ArithmeticError("fixed numerical replay differs")
            write_json_exclusive(args.output / "numerical-controls.json", numerical)
            write_json_exclusive(
                args.output / "replay.json",
                {
                    "exact_numerical_replay": True,
                    "recomputed_numerical_passes": 2,
                    "numerical_sha256": sha(args.output / "numerical-controls.json"),
                    "chunk_reuse_and_fault_controls": "test-controls.log; test_namespace_replay_and_interruption",
                    "no_network_claim": "not asserted",
                },
            )
            verified_after = verify_environment_and_protected()
            if manifest["source"] != {
                name: sha(ROOT / name) for name in manifest["source"]
            } or manifest["environment_inventory_sha256"] != sha(
                ROOT / "environment/artifact-inventory.json"
            ):
                raise ValueError("source/environment changed during controls")
            write_atomic_completion(
                args.output / "completion.json",
                {
                    "status": "implementation_controls_passed_pending_independent_review",
                    "seconds": time.monotonic() - start,
                    "attempt_sha256": sha(args.output / "attempt.json"),
                    "files": {
                        path.name: sha(path)
                        for path in args.output.iterdir()
                        if path.is_file()
                    },
                    "qualification": "not executed",
                    "verified_after": verified_after,
                },
            )
        except BaseException as error:
            write_json_exclusive(
                args.output / "failure.json",
                {
                    "type": type(error).__name__,
                    "message": str(error),
                    "seconds": time.monotonic() - start,
                },
            )
            raise
        print(
            "Fixed controls complete; independent scientific readiness verdict outstanding"
        )
        return 0
    result = audit_inputs() if args.command == "audit-inputs" else numerical_controls()
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(f"Completed {args.command}; zero candidate matrix fits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
