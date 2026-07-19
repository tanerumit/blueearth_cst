"""Exact-equivalence tests for the shared get_config helper (R3 §3, §8).

Pins the semantics the four inline get_config copies (three Snakefiles +
conftest) had before they were collapsed into src/snake_utils.py, so the move
is provably identity-preserving rather than merely green on a smoke test.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.snake_utils import get_config  # noqa: E402


def test_missing_required_raises():
    with pytest.raises(ValueError):
        get_config({}, "absent", optional=False)


def test_missing_optional_returns_none_by_default():
    assert get_config({}, "absent") is None


def test_missing_optional_returns_explicit_default():
    assert get_config({}, "absent", default="fallback") == "fallback"


def test_present_key_returned():
    assert get_config({"k": 42}, "k") == 42


def test_present_required_key_returned():
    assert get_config({"k": "v"}, "k", optional=False) == "v"


def test_none_value_returned_not_treated_as_missing():
    # A key explicitly set to None returns None, not the default — the key IS
    # present. This is the subtle semantic the inline copies all shared.
    assert get_config({"k": None}, "k", default="fallback") is None


@pytest.mark.parametrize("falsey", [0, "", False, []])
def test_falsey_values_returned_as_is(falsey):
    result = get_config({"k": falsey}, "k", default="fallback")
    assert result == falsey and type(result) is type(falsey)
