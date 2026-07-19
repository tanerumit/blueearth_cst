"""Tests for src/setup_gauges_and_outputs.py (R3 sections 7.1, 8)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.setup_gauges_and_outputs import update_wflow_gauges_outputs  # noqa: E402


def test_raises_on_unknown_outvar():
    # Validation runs before any model is opened, so a dummy root is fine: an
    # unknown wflow_outvars name must raise loudly, not be silently dropped.
    with pytest.raises(ValueError, match="Unknown wflow_outvars"):
        update_wflow_gauges_outputs(wflow_root="unused", outputs=["bogus var"])
