"""Linux production-versus-frozen GF15 parity matrix; scratch evidence runner."""

import importlib.util
import json
import struct
import sys
from pathlib import Path

import numpy as np

from blueearth_cst.experiment import gev_lmoments as production

root = Path(__file__).resolve().parents[7]
candidate_path = (
    root
    / "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/candidate_adapter.py"
)
spec = importlib.util.spec_from_file_location("gf15_frozen_candidate", candidate_path)
candidate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = candidate
spec.loader.exec_module(candidate)

base = np.array([0.0, 0.2, 0.2, 0.5, 0.75, 1.0, 1.4, 2.0])
shapes = [
    base,
    np.array([1.0, 2.0, 3.0, 4.0]),
    np.array([0.5, 0.5, 0.5, 0.5, 1.0, 2.0]),
    np.array([-5.0, -1.0, 0.0, 0.0, 3.0, 9.0, 12.0]),
    np.linspace(0.0, 1.0, 30),
    np.array([2.0, 2.0, 2.0, 2.0]),
    np.array([0.0, 0.0, 0.0, 1.0, 100.0]),
]
samples = [
    transform(shape)
    for shape in shapes
    for transform in (
        lambda x: x,
        lambda x: x + 100.0,
        lambda x: x * 1000.0,
        lambda x: -x,
    )
]
probability_sets = [
    (0.9,),
    (0.5,),
    (0.9, 0.5),
    (0.5, 0.9),
    (0.01,),
    (0.99,),
    (0.01, 0.5, 0.99),
]


def equal_number(left, right):
    if isinstance(left, (float, int)) and isinstance(right, (float, int)):
        return struct.pack(">d", float(left)) == struct.pack(">d", float(right))
    return left == right


def compare(produced, expected):
    failures = []
    for field in ("accepted", "refusal_reasons", "warnings"):
        actual = (
            produced["status"] == "accepted" if field == "accepted" else produced[field]
        )
        if actual != expected[field]:
            failures.append(field)
    if produced.get("exception_refusal") != expected.get("exception_refusal"):
        failures.append("exception_refusal")
    for field, names in (
        ("input", ("count", "sample_sha256", "probabilities")),
        ("normalization", ("a", "s")),
        ("moments", ("normalized", "physical", "t3")),
        ("normalized_parameters", ("c", "loc", "scale")),
        ("physical_parameters", ("c", "loc", "scale")),
        (
            "normalized_diagnostics",
            ("sample_outside_support", "nonfinite_log_density_count"),
        ),
        (
            "physical_diagnostics",
            ("sample_outside_support", "nonfinite_log_density_count"),
        ),
    ):
        actual = produced.get(field)
        reference = expected.get(field)
        if (actual is None) != (reference is None):
            failures.append(field)
        elif actual is not None:
            for name in names:
                left = actual.get(name)
                right = reference.get(name)
                if isinstance(left, list) and isinstance(right, list):
                    same = len(left) == len(right) and all(
                        equal_number(a, b) for a, b in zip(left, right)
                    )
                else:
                    same = equal_number(left, right)
                if not same:
                    failures.append(f"{field}.{name}")
    if len(produced["quantiles"]) != len(expected["quantiles"]):
        failures.append("quantile_count")
    else:
        for index, (row, ref) in enumerate(
            zip(produced["quantiles"], expected["quantiles"])
        ):
            for name in (
                "p",
                "normalized",
                "estimate",
                "diagnostic_valid",
                "accepted",
                "refusal_reason",
            ):
                if not equal_number(row.get(name), ref.get(name)):
                    failures.append(f"quantiles.{index}.{name}")
    return failures


failures = []
accepted = refused = 0
first_accepted = None
for sample_index, sample in enumerate(samples):
    for probability_index, probabilities in enumerate(probability_sets):
        produced = production.fit_case(sample, probabilities).record()
        expected = candidate.fit_case(sample, probabilities)
        differences = compare(produced, expected)
        if differences:
            failures.append(
                {
                    "sample": sample_index,
                    "probabilities": probability_index,
                    "fields": differences,
                }
            )
        if produced["status"] == "accepted":
            accepted += 1
            if first_accepted is None:
                first_accepted = (produced, expected)
        else:
            refused += 1

mutated = json.loads(json.dumps(first_accepted[0]))
mutated["quantiles"][0]["estimate"] *= 1.0 + 1e-9
mutant_failures = compare(mutated, first_accepted[1])
assert "quantiles.0.estimate" in mutant_failures

refusal_failures = []
refusal_cases = 0
for sample_index, sample in enumerate(samples):
    for probability_index, probabilities in enumerate(
        ((0.9, 1.0), (0.9, float("nan")), (0.0,))
    ):
        produced = production.fit_case(sample, probabilities).record()
        expected = candidate.fit_case(sample, probabilities)
        differences = compare(produced, expected)
        refusal_cases += 1
        if differences:
            refusal_failures.append(
                {
                    "sample": sample_index,
                    "probabilities": probability_index,
                    "fields": differences,
                }
            )

result = {
    "sample_shapes": len(samples),
    "probability_sets": len(probability_sets),
    "pairs": len(samples) * len(probability_sets),
    "accepted": accepted,
    "refused": refused,
    "mismatches": failures,
    "refusal_cases": refusal_cases,
    "refusal_mismatches": refusal_failures,
    "wrong_result_mutant_failures": mutant_failures,
}
print(json.dumps(result, indent=2, sort_keys=True))
if failures or refusal_failures:
    raise SystemExit(1)
