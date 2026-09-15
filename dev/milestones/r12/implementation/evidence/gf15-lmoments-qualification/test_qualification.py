"""Focused falsifiers for the isolated Stage 2 evaluator, not the estimator."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "qualification", Path(__file__).with_name("qualify-lmoments.py")
)
qualification = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qualification
SPEC.loader.exec_module(qualification)


def test_errors_denominators_margins_and_zero() -> None:
    """Refusals cannot disappear and tiny rounded zero truth stays undefined."""
    row = qualification.error_row(
        {
            "shape_c": 0.0,
            "n": 10,
            "draw": 0,
            "p": 0.5,
            "ratio": 0.0,
            "true_quantile": 1e-16,
            "sigma": 1.0,
            "mu": -0.3,
        },
        True,
        0.125 + 1e-16,
    )
    assert row["scale_error"] == pytest.approx(0.125)
    assert row["relative_error"] is None
    records = [dict(row, draw=i, accepted=i < 949) for i in range(1000)]
    summary = qualification.cell_summary(records)
    assert summary["accepted_count"] == 949
    assert summary["valid_rate"] == 0.949
    assert summary["margins"]["valid_rate"] == pytest.approx(-0.001)
    assert summary["scale_pass"] is False
    assert summary["relative_pass"] is None
    assert summary["scale"]["median_absolute"] == pytest.approx(0.125)
    assert (
        qualification.cell_summary([dict(r, accepted=False) for r in records])["scale"]
        is None
    )
    with pytest.raises(ValueError, match="1000"):
        qualification.cell_summary(records[:-1])
    passing = [dict(r, accepted=True, scale_error=0.05) for r in records]
    assert qualification.cell_summary(passing)["scale_pass"] is True
    assert (
        qualification.cell_summary([dict(r, scale_error=0.125) for r in passing])[
            "scale_pass"
        ]
        is False
    )


def test_translation_categories_and_numeric_boundary() -> None:
    """Both refusals never pass; acceptance changes cannot hide behind nulls."""
    for first, second, expected in (
        (True, True, "both_accepted"),
        (True, False, "first_only"),
        (False, True, "second_only"),
        (False, False, "both_refused"),
    ):
        baseline = {"accepted": first, "scale_error": 0.0}
        translated = {"accepted": second, "scale_error": 1e-6}
        result = qualification.translation_result(baseline, translated)
        assert result["category"] == expected
        assert result["numerical_pass"] is (True if first and second else None)
        assert result["acceptance_unchanged"] is (first == second)
    result = qualification.translation_result(
        {"accepted": True, "scale_error": 0.0},
        {"accepted": True, "scale_error": 1.0001e-6},
    )
    assert result["numerical_pass"] is False
    passed = {
        "category": "both_accepted",
        "acceptance_unchanged": True,
        "numerical_pass": True,
    }
    refused = {
        "category": "both_refused",
        "acceptance_unchanged": True,
        "numerical_pass": None,
    }
    assert qualification.translation_cell_gate([passed] * 950 + [refused] * 50)
    assert not qualification.translation_cell_gate([passed] * 949 + [refused] * 51)
    assert not qualification.translation_cell_gate([refused] * 1000)
    assert not qualification.translation_cell_gate(
        [passed] * 999 + [dict(passed, numerical_pass=False)]
    )
    assert not qualification.translation_cell_gate(
        [passed] * 999 + [dict(refused, acceptance_unchanged=False)]
    )


def test_atomic_chunk_fault_resume_and_corruption(tmp_path) -> None:
    """Only exact receipts are reusable; unexpected compute faults publish none."""
    calls = []

    def compute():
        calls.append(1)
        return [{"accepted": False, "quantiles": [{"p": 0.5}]}]

    root = tmp_path / "chunk"
    first = qualification.atomic_chunk(root, "a" * 64, compute, (1, 1))
    assert first["reused"] is False
    assert qualification.atomic_chunk(root, "a" * 64, compute, (1, 1))["reused"] is True
    assert calls == [1]
    with pytest.raises(ValueError, match="binding"):
        qualification.atomic_chunk(root, "b" * 64, compute, (1, 1))
    receipt = root / "receipt.json"
    record = json.loads(receipt.read_text())
    record["fits"] = 2
    receipt.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="receipt"):
        qualification.atomic_chunk(root, "a" * 64, compute, (1, 1))

    def fault():
        raise RuntimeError("unexpected adapter fault")

    failed = tmp_path / "failed"
    with pytest.raises(RuntimeError, match="unexpected"):
        qualification.atomic_chunk(failed, "a" * 64, fault, (1, 1))
    assert not (failed / "receipt.json").exists()
    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / "binding.json").write_text(json.dumps({"binding": "a" * 64}))
    (partial / "fits.partial").write_text("interrupted bytes")
    assert (
        qualification.atomic_chunk(partial, "a" * 64, compute, (1, 1))["reused"]
        is False
    )
    (partial / "writer.claim").touch()
    with pytest.raises(FileExistsError):
        qualification.atomic_chunk(partial, "a" * 64, compute, (1, 1))
