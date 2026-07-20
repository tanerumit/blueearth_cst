"""Unit tests for prepare_weagen_config helpers (R5 §8).

Targets the year math (compute_nr_years, generate-branch) and the stress-test
branch dict assembly (build_weagen_config). Both are import-clean after the R5
function extraction (commit 3) — no snakemake global, no heavy deps.
"""

import math
import os
import sys

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.prepare_weagen_config import build_weagen_config, compute_nr_years


@pytest.mark.parametrize(
    "middle_year, run_length, expected",
    [
        (2080, 20, math.ceil((2080 + 20 / 2) - 2010 + 2)),  # 82 (seed config)
        (2050, 30, math.ceil((2050 + 30 / 2) - 2010 + 2)),  # 57
        (2010, 0, math.ceil((2010 + 0) - 2010 + 2)),        # 2 (degenerate)
    ],
)
def test_compute_nr_years(middle_year, run_length, expected):
    """Year math spans 2010 -> horizon +/- run_length/2, +2 pad."""
    assert compute_nr_years(middle_year, run_length) == expected


def test_seed_year_math_value():
    """Pin the seed-config value explicitly (horizon 2080, run_length 20)."""
    assert compute_nr_years(2080, 20) == 82


def test_stress_test_branch_dict_shape(tmp_path):
    """The stress_test branch assembles the imposeClimateChanges block + copies
    the temp/precip sections verbatim from the snake config — no arithmetic."""
    snake_cfg = {
        "workflows": {
            "climate_experiment": {
                "stress_test": {
                    "temp": {"step_num": 1, "transient_change": True},
                    "precip": {"step_num": 2, "transient_change": False},
                }
            }
        }
    }
    snake_path = tmp_path / "snake.yml"
    snake_path.write_text(yaml.safe_dump(snake_cfg), encoding="utf-8")

    out = build_weagen_config(
        cftype="stress_test",
        snake_config_path=str(snake_path),
        output_path="out/",
        nc_file_prefix="rlz_1_cst",
        nc_file_suffix="3",
    )

    assert out["imposeClimateChanges"] == {
        "output.path": "out/",
        "nc.file.prefix": "rlz_1_cst",
        "nc.file.suffix": "3",
    }
    assert out["temp"] == {"step_num": 1, "transient_change": True}
    assert out["precip"] == {"step_num": 2, "transient_change": False}
