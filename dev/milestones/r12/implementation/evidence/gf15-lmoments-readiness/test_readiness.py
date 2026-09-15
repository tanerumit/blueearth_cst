"""Focused falsifiers for the authorized, isolated Stage 1 controls."""

import copy
import importlib.util
import inspect
import json
import random
import sys
import types
import warnings
from contextlib import contextmanager
from decimal import Decimal, localcontext
from pathlib import Path

import candidate_adapter as adapter
import numpy as np
import pytest
from lmoments3 import distr
from reference_oracle import gamma_decimal, population_moments

SPEC = importlib.util.spec_from_file_location(
    "readiness_checks", Path(__file__).with_name("check-readiness.py")
)
checks = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checks
SPEC.loader.exec_module(checks)
SAMPLE = np.array([0.0, 0.2, 0.2, 0.5, 0.75, 1.0, 1.4, 2.0])


def fail_rng(*args, **kwargs):
    """Tripwire for forbidden stochastic or fallback operations."""
    raise RuntimeError("forbidden stochastic/fallback operation")


def test_independent_population_reference() -> None:
    """Check Gamma at exact integer values and independent Gumbel limits."""
    for precision in (80, 120):
        with localcontext() as context:
            context.prec = precision
            for argument, expected in ((1, 1), (2, 1), (5, 24)):
                value, evidence = gamma_decimal(Decimal(argument))
                assert abs(value - expected) < Decimal("1e-38")
                assert Decimal(evidence["omitted_term_bound"]) <= Decimal("1e-40")
            moments, _ = population_moments(Decimal(0))
            assert moments[1] == Decimal(2).ln()
            assert abs(
                moments[2] - Decimal("0.169925001442312362907477887895633")
            ) < Decimal("1e-32")
            with pytest.raises(ValueError, match="positive"):
                gamma_decimal(Decimal(0))


def test_truth_blind_no_rng_fallback_and_replay(monkeypatch) -> None:
    """Instrument random calls/state and both named estimator calls."""
    assert list(inspect.signature(adapter.fit_case).parameters) == [
        "sample",
        "probabilities",
    ]
    state = random.getstate()
    numpy_state = np.random.get_state()
    for module, names in (
        (random, ("random", "uniform", "gauss", "seed")),
        (np.random, ("default_rng", "random", "uniform", "normal", "seed")),
        (adapter.genextreme, ("fit",)),
        (distr.gev, ("fit",)),
    ):
        for name in names:
            monkeypatch.setattr(module, name, fail_rng)
    counts = {"moments": 0, "inversion": 0}
    original_moments = adapter.lmoments3.lmom_ratios
    original_fit = distr.gev.lmom_fit

    def moments(*args, **kwargs):
        counts["moments"] += 1
        return original_moments(*args, **kwargs)

    def inversion(*args, **kwargs):
        counts["inversion"] += 1
        return original_fit(*args, **kwargs)

    monkeypatch.setattr(adapter.lmoments3, "lmom_ratios", moments)
    monkeypatch.setattr(distr.gev, "lmom_fit", inversion)
    first = adapter.fit_case(SAMPLE, [0.5, 0.9])
    evaluator_labels = {"shape": -0.2, "truth": 100}
    evaluator_labels.update(shape=0.2, truth=-100)
    second = adapter.fit_case(SAMPLE, [0.5, 0.9])
    assert first == second and first["accepted"]
    assert counts == {"moments": 2, "inversion": 2}
    assert random.getstate() == state
    after = np.random.get_state()
    assert (
        numpy_state[0] == after[0]
        and np.array_equal(numpy_state[1], after[1])
        and numpy_state[2:] == after[2:]
    )
    y = (SAMPLE - SAMPLE.min()) / np.ptp(SAMPLE)
    expected = dict(original_fit(lmom_ratios=original_moments(y, nmom=3)))
    assert first["normalized_parameters"] == expected
    # Unbiased order-statistic PWMs are an independent sample-moment check.
    from math import comb

    n = len(y)
    b = [
        sum(comb(i, r) / comb(n - 1, r) * value for i, value in enumerate(sorted(y)))
        / n
        for r in range(3)
    ]
    expected_moments = [b[0], 2 * b[1] - b[0], 6 * b[2] - 6 * b[1] + b[0]]
    assert np.allclose(
        first["moments"]["normalized"], expected_moments, atol=1e-15, rtol=0
    )


@pytest.mark.parametrize(
    "sample",
    [[], [1, 2, 3], [1] * 4, [[1, 2], [3, 4]], [1, 2, 3, np.nan], [1, 2, 3, np.inf]],
)
def test_invalid_samples_are_explicit_refusals(sample) -> None:
    result = adapter.fit_case(sample, [0.5, 0.9])
    assert not result["accepted"] and result["refusal_reasons"]
    assert "exception_refusal" not in result
    assert result == adapter.fit_case(sample, [0.5, 0.9])


def test_conjunction_ties_and_translation() -> None:
    first = adapter.fit_case(SAMPLE, [0.5, 0.9])
    assert first["accepted"]
    invalid = adapter.fit_case(SAMPLE, [0.5, 1.0])
    assert not invalid["accepted"]
    assert invalid["quantiles"][0]["diagnostic_valid"]
    assert invalid["quantiles"][0]["refusal_reason"] == "shared_baseline_revocation"
    assert not any(q["accepted"] for q in invalid["quantiles"])
    for shift in (-100.0, 0.05, 2.0, 10.0, 1000.0):
        for original in first["quantiles"]:
            translated = adapter.fit_case(SAMPLE + shift, [original["p"]])
            assert translated["accepted"] == first["accepted"]
            assert (
                abs(
                    translated["quantiles"][0]["estimate"]
                    - shift
                    - original["estimate"]
                )
                <= 1e-6
            )


def test_actual_source_allowlist_and_synthetic_nonconvergence() -> None:
    try:
        distr.gev._lmom_fit([0.0, 0.0, 0.0])
    except ValueError as error:
        positive = adapter.exception_refusal(error)
        assert positive and positive["line"] == 1307
        trace = error.__traceback__
        while trace.tb_next:
            trace = trace.tb_next
        # Synthetic classifier coverage only; no natural nonconvergence is asserted.
        synthetic = Exception("Iteration has not converged")
        synthetic.__traceback__ = types.TracebackType(
            None, trace.tb_frame, trace.tb_lasti, 1342
        )
        assert adapter.exception_refusal(synthetic)["line"] == 1342
    else:
        pytest.fail("actual pinned raising statement was not exercised")


@pytest.mark.parametrize("call", ["moments", "inversion", "adapter"])
@pytest.mark.parametrize(
    "error",
    [
        ValueError("L-Moments Invalid"),
        ValueError("conversion failed"),
        Exception("Iteration has not converged"),
        TypeError("L-Moments Invalid"),
        MemoryError("injected"),
        RuntimeError("adapter fault"),
    ],
)
def test_unknown_fault_stops_without_completion(
    call, error, monkeypatch, tmp_path
) -> None:
    def raise_fault(*args, **kwargs):
        raise error

    module, name = {
        "moments": (adapter.lmoments3, "lmom_ratios"),
        "inversion": (distr.gev, "lmom_fit"),
        "adapter": (adapter, "_quantile"),
    }[call]
    monkeypatch.setattr(module, name, raise_fault)
    assert adapter.exception_refusal(error) is None
    with pytest.raises(type(error), match=str(error)):
        checks.fixed_chunk(
            tmp_path / "chunk",
            checks.fixed_binding(
                {"sample": SAMPLE.tolist(), "probabilities": [0.5, 0.9]}
            ),
            lambda: adapter.fit_case(SAMPLE, [0.5, 0.9]),
        )
    assert not (tmp_path / "chunk/receipt.json").exists()
    assert not (tmp_path / "chunk/writer.claim").exists()


def test_inventory_key_and_receipt_mutations() -> None:
    row = next(
        checks.rows(checks.ROOT.parent / "gf15/results/draws-c0-n10-0000.jsonl.gz")
    )
    for name in ("mu", "true_quantile"):
        altered_truth = {"mu": row["mu"], "true_quantile": row["true_quantile"]}
        altered_truth[name] += 1
        with pytest.raises(ValueError, match="truth/offset"):
            checks.validate_paired_truth(row, altered_truth)
    table = {}
    checks.insert_unique(table, row)
    with pytest.raises(ValueError, match="duplicate"):
        checks.insert_unique(table, row)
    key = checks.canonical_key(row)
    with pytest.raises(ValueError, match="coverage"):
        checks.validate_key_coverage(set(), {key})
    altered = copy.deepcopy(row)
    altered["ratio"] = 0
    with pytest.raises(ValueError, match="coverage"):
        checks.validate_key_coverage({checks.canonical_key(altered)}, {key})
    altered["draw"] = 1000
    with pytest.raises(ValueError, match="illegal draw"):
        checks.insert_unique({}, altered)
    receipt = checks.read_json(
        checks.ROOT.parent
        / "gf15-normalized-qualification/results/fits-c0-n10-0000.json"
    )
    counts = tuple(receipt[k] for k in ("fits", "quantiles", "accepted", "evaluations"))
    checks.validate_receipt(
        receipt, receipt["file"], receipt["sha256"], receipt["binding"], counts
    )
    for field in ("file", "sha256", "binding", "fits", "quantiles"):
        altered = {**receipt, field: "corrupted"}
        with pytest.raises(ValueError, match="receipt"):
            checks.validate_receipt(
                altered, receipt["file"], receipt["sha256"], receipt["binding"], counts
            )


def test_d3_synthetic_denominators_and_empty_cohorts() -> None:
    sample = [{"accepted": True, "error": -0.2}, {"accepted": True, "error": 0.4}] + [
        {"accepted": False, "error": 999}
    ] * 998
    result = checks.summarize_synthetic(sample, 0.9, 0)
    assert result["valid_rate"] == 0.002 and result["accepted_count"] == 2
    assert result["median"] == pytest.approx(0.1)
    assert result["p90_absolute"] == pytest.approx(0.38)
    assert result["relative"] is None and not result["scale_pass"]
    assert checks.summarize_synthetic(sample, 0.9, 0.05)["relative_pass"] is None
    assert checks.summarize_synthetic(sample, 0.9, 0.5)["relative_pass"] is False
    empty = checks.summarize_synthetic([{"accepted": False}] * 1000, 0.5, 2)
    assert empty["median"] is None and empty["p90_absolute"] is None
    assert {
        checks.comparison_category(a, b) for a in (True, False) for b in (True, False)
    } == {"both_accepted", "first_only", "second_only", "both_refused"}


def test_namespace_replay_and_interruption(tmp_path) -> None:
    namespace = tmp_path / "fixed"
    binding = checks.fixed_binding(
        {"sample": SAMPLE.tolist(), "probabilities": [0.5, 0.9]}
    )
    first = checks.fixed_chunk(
        namespace,
        binding,
        lambda: adapter.fit_case(SAMPLE, [0.5, 0.9]),
    )
    second = checks.fixed_chunk(namespace, binding, fail_rng)
    assert (first["action"], second["action"]) == ("computed", "reused")
    assert first["payload"] == second["payload"]
    for changed in ("source", "environment", "inputs"):
        with pytest.raises(ValueError, match="conflicting"):
            checks.fixed_chunk(
                namespace, checks.fixed_binding({changed: "mutated"}), fail_rng
            )
    (namespace / "writer.claim").write_text("competing writer")
    with pytest.raises(FileExistsError):
        checks.fixed_chunk(namespace, binding, fail_rng)
    (namespace / "writer.claim").unlink()
    receipt = namespace / "receipt.json"
    value = json.loads(receipt.read_text())
    value["sha256"] = "corrupt"
    receipt.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="inconsistent"):
        checks.fixed_chunk(namespace, binding, fail_rng)
    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    checks.write_json_exclusive(incomplete / "binding.json", {"binding": binding})
    (incomplete / "payload.partial").write_text("interrupted")
    assert (
        checks.fixed_chunk(incomplete, binding, lambda: {"fixed": 1})["action"]
        == "computed"
    )
    partial_receipt = tmp_path / "partial-receipt"
    partial_receipt.mkdir()
    (partial_receipt / "receipt.partial").write_text("interrupted")
    with pytest.raises(ValueError, match="partial receipt"):
        checks.fixed_chunk(partial_receipt, binding, fail_rng)
    print(
        json.dumps(
            {
                "namespace_control": "passed",
                "binding": binding,
                "computed_chunks": 2,
                "reused_chunks": 1,
                "rejected_conflicts": 5,
                "partial_receipt_refused": True,
            }
        )
    )


@pytest.mark.parametrize("mutation", ["sign", "tuple", "probability", "output"])
def test_quantile_controls_discriminate(mutation) -> None:
    parameters = {"c": 0.2, "loc": 0.0, "scale": 1.0}
    output = adapter._quantile(parameters, 0.9)
    probability = 0.9
    if mutation == "sign":
        parameters["c"] *= -1
    elif mutation == "tuple":
        parameters["loc"] += 0.01
    elif mutation == "probability":
        probability = 0.5
    else:
        output += 0.01
    with pytest.raises(ArithmeticError, match="quantile gate"):
        checks.quantile_gate(parameters, probability, output, 1.0, output)


def test_overflow_warning_retention_discriminates(monkeypatch) -> None:
    """The earlier early-return omission is detected by this behavioral guard."""

    def check_warning():
        result = adapter.fit_case([-1e308, -1e307, 1e307, 1e308], [0.5])
        assert result["refusal_reasons"] == ["invalid_range"]
        assert any("overflow" in warning["message"] for warning in result["warnings"])

    check_warning()

    @contextmanager
    def broken_capture(record):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            yield

    monkeypatch.setattr(adapter, "_record_warnings", broken_capture)
    with pytest.raises(AssertionError):
        check_warning()


def test_population_gate_precedes_characterization(monkeypatch) -> None:
    original = adapter._parameters

    def incorrect(moments):
        result = original(moments)
        result["c"] += 0.001
        return result

    monkeypatch.setattr(adapter, "_parameters", incorrect)
    monkeypatch.setattr(checks, "parameter_reference", fail_rng)
    with pytest.raises(ArithmeticError, match="original population gate failed"):
        checks.numerical_controls()


@pytest.mark.parametrize(
    "bad_enclosure", [["0", "1"], ["100", "100.0000000000000000000000000000001"]]
)
def test_quantile_enclosure_mutations_stop(bad_enclosure, monkeypatch) -> None:
    def corrupted(parameters, p, width, precision):
        return {
            "enclosure": bad_enclosure
            if precision == 80
            else ["0.366512920581664327", "0.366512920581664328"]
        }

    monkeypatch.setattr(checks, "cdf_enclosure", corrupted)
    with pytest.raises(ArithmeticError, match="CDF"):
        checks.quantile_gate(
            {"c": 0.0, "loc": 0.0, "scale": 1.0},
            0.5,
            0.3665129205816643,
            1.0,
            0.3665129205816643,
        )


def test_forward_cdf_support_direction() -> None:
    from reference_oracle import log_cdf_standard

    with localcontext() as context:
        context.prec = 80
        assert log_cdf_standard(Decimal(6), Decimal(".2")).lo == 0
        assert log_cdf_standard(Decimal(-6), Decimal("-.2")).hi == Decimal("-Infinity")
        assert (
            log_cdf_standard(Decimal(0), Decimal(0)).lo
            < -1
            < log_cdf_standard(Decimal(0), Decimal(0)).hi
        )


@pytest.mark.parametrize(
    "parameters",
    [
        {"c": -1.0, "loc": 0.0, "scale": 1.0},
        {"c": 0.0, "loc": 0.0, "scale": 0.0},
        {"c": 0.0, "loc": float("nan"), "scale": 1.0},
    ],
)
def test_explicit_parameter_refusals(parameters, monkeypatch) -> None:
    monkeypatch.setattr(adapter, "_parameters", lambda moments: parameters)
    result = adapter.fit_case(SAMPLE, [0.5, 0.9])
    assert result["refusal_reasons"] == ["invalid_parameters"]
    assert "exception_refusal" not in result


def test_actual_conversion_error_and_subclass_are_faults(tmp_path) -> None:
    with pytest.raises(ValueError):
        checks.fixed_chunk(
            tmp_path / "conversion",
            checks.fixed_binding({"input": "bad conversion"}),
            lambda: adapter.fit_case(["bad", 1, 2, 3], [0.5]),
        )
    assert not (tmp_path / "conversion/receipt.json").exists()

    class OtherValueError(ValueError):
        pass

    try:
        raise OtherValueError("L-Moments Invalid")
    except OtherValueError as error:
        assert adapter.exception_refusal(error) is None


def test_endpoint_rounding_is_not_vetoed_by_probability_diagnostic() -> None:
    """A valid rounded endpoint must survive an unresolved diagnostic residual."""
    result = checks.quantile_gate(
        {"c": 60.0, "loc": 0.0, "scale": 60.0}, 0.9, 1.0, 1.0, 1.0
    )
    assert result["outcome"] == "pass"
    assert result["rounding_cell_intersects_support"]
    assert result["probability_residual_diagnostic_status"].startswith(
        "unresolved_support_interval"
    )
