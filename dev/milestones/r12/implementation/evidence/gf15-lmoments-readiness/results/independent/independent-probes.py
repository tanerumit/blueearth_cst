"""Read-only scientific probes for the fixed GF15 readiness artifact."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import struct
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def arctan(value):
    total, term = value, value
    for k in range(1, 1000):
        term *= -value * value
        addition = term / (2 * k + 1)
        total += addition
        if abs(addition) < Decimal("1e-145"):
            return total
    raise AssertionError("Machin pi probe exhausted")


def forward_log_cdf(value, parameters):
    c, loc, scale = (Decimal.from_float(parameters[k]) for k in ("c", "loc", "scale"))
    z = (value - loc) / scale
    if c == 0:
        return -(-z).exp()
    support = 1 - c * z
    if support <= 0:
        return Decimal(0) if c > 0 else Decimal("-Infinity")
    return -(support.ln() / c).exp()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(
        "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness"
    ).resolve()
    sys.path.insert(0, str(root))
    import candidate_adapter as adapter
    import reference_oracle as oracle

    spec = importlib.util.spec_from_file_location("checks", root / "check-readiness.py")
    checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checks)
    controls = read(args.results / "numerical-controls.json")
    report = {
        "completion_sha256": sha(args.results / "completion.json"),
        "probe_source_sha256": sha(Path(__file__)),
    }
    with localcontext() as context:
        context.prec = 150
        pi = 16 * arctan(Decimal(1) / 5) - 4 * arctan(Decimal(1) / 239)
        assert abs(pi - oracle.PI) < Decimal("1e-137")
        gamma, evidence = oracle.gamma_decimal(Decimal(".5"))
        assert abs(gamma * gamma - pi) < Decimal("1e-55")
        first, _ = oracle.gamma_decimal(Decimal(".8"))
        next_value, _ = oracle.gamma_decimal(Decimal("1.8"))
        assert abs(next_value - Decimal(".8") * first) < Decimal("1e-55")
        report["gamma_pi"] = {
            "machin_pi_error": str(abs(pi - oracle.PI)),
            "gamma_half_squared_error": str(abs(gamma * gamma - pi)),
            "gamma_recurrence_error": str(abs(next_value - Decimal(".8") * first)),
            "omitted_log_gamma_term": evidence["omitted_term_bound"],
        }
        count = 0
        max_error = Decimal(0)
        for case in controls["quantiles"]:
            normalized = Decimal.from_float(case["normalized"]["output"])
            magnitude = max(Decimal(1), abs(normalized))
            for coordinate in ("normalized", "physical"):
                row = case[coordinate]
                scale = Decimal.from_float(row["normalization_scale"])
                target = Decimal.from_float(row["p"]).ln()
                for key, value in row["parameters"].items():
                    assert struct.pack(">d", value).hex() == row["parameter_bits"][key]
                assert struct.pack(">d", row["p"]).hex() == row["p_bits"]
                assert struct.pack(">d", row["output"]).hex() == row["output_bits"]
                assert Decimal(row["T_normalized"]) == Decimal("1e-10") * magnitude
                for precision in row["precision_passes"]:
                    lo, hi = map(Decimal, precision["enclosure"])
                    assert forward_log_cdf(lo, row["parameters"]) <= target
                    assert forward_log_cdf(hi, row["parameters"]) >= target
                    assert (hi - lo) / scale <= Decimal("1e-30") * magnitude
                lo, hi = map(Decimal, row["hull"])
                error = (
                    max(
                        abs(Decimal.from_float(row["output"]) - lo),
                        abs(Decimal.from_float(row["output"]) - hi),
                    )
                    / scale
                )
                assert error <= Decimal("1e-10") * magnitude
                max_error = max(max_error, error)
                count += 1
        report["cdf_endpoint_rechecks"] = {
            "comparisons": count,
            "scalar_decimal_precision": 150,
            "maximum_normalized_error_bound": str(max_error),
        }
    # Independent exact-rational PWM recovery on the existing tied fixed sample.
    sample = [0.0, 0.2, 0.2, 0.5, 0.75, 1.0, 1.4, 2.0]
    fitted = adapter.fit_case(sample, [0.5, 0.9])
    y = list(map(Fraction.from_float, fitted["normalization"]["y"]))
    n = len(y)
    pwm = [
        sum(
            Fraction(comb(i, r), comb(n - 1, r)) * value
            for i, value in enumerate(sorted(y))
        )
        / n
        for r in range(3)
    ]
    expected = [pwm[0], 2 * pwm[1] - pwm[0], 6 * pwm[2] - 6 * pwm[1] + pwm[0]]
    differences = [
        abs(float(exact) - actual)
        for exact, actual in zip(expected, fitted["moments"]["normalized"])
    ]
    assert max(differences) <= 1e-15
    report["exact_rational_pwm"] = {
        "absolute_differences": differences,
        "ties_retained": True,
    }
    # Independent full-key loading; no evaluator helpers and no fits on these rows.
    tables = [{}, {}]
    for index, shape in enumerate((-0.2, 0.0, 0.2)):
        for n in (10, 18, 30, 60):
            for start in range(0, 1000, 50):
                suffix = f"c{index}-n{n}-{start:04d}.jsonl.gz"
                for method, filename in enumerate(
                    (
                        root.parent / "gf15/results" / f"draws-{suffix}",
                        root.parent
                        / "gf15-normalized-qualification/results"
                        / f"fits-{suffix}",
                    )
                ):
                    with gzip.open(filename, "rt", encoding="utf-8") as stream:
                        for line in stream:
                            record = json.loads(line)
                            quantiles = [record] if method == 0 else record["quantiles"]
                            assert len(quantiles) == (
                                1 if method == 0 or record["ratio"] is not None else 2
                            )
                            for q in quantiles:
                                key = (
                                    record["shape_c"],
                                    record["n"],
                                    record["draw"],
                                    q["p"],
                                    record["ratio"],
                                )
                                assert key not in tables[method]
                                tables[method][key] = (
                                    record["mu"],
                                    q["true_quantile"],
                                    record["valid"]
                                    if method == 0
                                    else record["accepted"],
                                )
    expected_keys = {
        (c, n, draw, p, ratio)
        for c in (-0.2, 0.0, 0.2)
        for n in (10, 18, 30, 60)
        for draw in range(1000)
        for p in (0.5, 0.9)
        for ratio in (None, 0.0, 0.05, 0.5, 2.0, 10.0)
    }
    assert set(tables[0]) == set(tables[1]) == expected_keys
    assert all(tables[0][key][:2] == tables[1][key][:2] for key in expected_keys)
    report["independent_join"] = {
        "keys_each": len(expected_keys),
        "A_valid": sum(row[2] for row in tables[0].values()),
        "B_accepted_quantiles": sum(row[2] for row in tables[1].values()),
        "matrix_fits": 0,
    }
    endpoint = checks.quantile_gate(
        {"c": 60.0, "loc": 0.0, "scale": 60.0}, 0.9, 1.0, 1.0, 1.0
    )
    assert endpoint["outcome"] == "pass"
    report["endpoint_counterexample_after_repair"] = endpoint
    report["status"] = "passed"
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("Independent scientific probes passed")


if __name__ == "__main__":
    main()
