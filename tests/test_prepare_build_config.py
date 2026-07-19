"""Tests for src/prepare_build_config.py (R3 section 8). Hermetic (yaml only)."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.prepare_build_config import merge_build_config  # noqa: E402


def _template(path):
    path.write_text(
        yaml.safe_dump(
            {
                "modeltype": "wflow_sbm",
                "steps": [
                    {"setup_basemaps": {"hydrography_fn": "merit_hydro_ihu"}},
                    {"setup_rivers": {"river_upa": 32}},
                ],
            }
        )
    )


def test_merge_injects_region_and_res_preserving_other_keys(tmp_path):
    template = tmp_path / "build.yml"
    _template(template)
    out = tmp_path / "out" / "run.yml"  # parent does not exist yet
    merge_build_config(
        template, out, 0.00833333, "{'subbasin': [9.66, 0.44], 'uparea': 100}"
    )
    cfg = yaml.safe_load(out.read_text())
    basemaps = next(s["setup_basemaps"] for s in cfg["steps"] if "setup_basemaps" in s)
    assert basemaps["region"] == {"subbasin": [9.66, 0.44], "uparea": 100}
    assert basemaps["res"] == 0.00833333
    assert basemaps["hydrography_fn"] == "merit_hydro_ihu"  # preserved
    assert any("setup_rivers" in s for s in cfg["steps"])  # other steps untouched


def test_merge_accepts_dict_region(tmp_path):
    template = tmp_path / "build.yml"
    _template(template)
    out = tmp_path / "run.yml"
    merge_build_config(template, out, "0.05", {"subbasin": [1.0, 2.0]})
    cfg = yaml.safe_load(out.read_text())
    basemaps = next(s["setup_basemaps"] for s in cfg["steps"] if "setup_basemaps" in s)
    assert basemaps["region"] == {"subbasin": [1.0, 2.0]}
    assert basemaps["res"] == 0.05


def test_merge_raises_without_setup_basemaps(tmp_path):
    template = tmp_path / "build.yml"
    template.write_text(yaml.safe_dump({"steps": [{"setup_rivers": {}}]}))
    with pytest.raises(RuntimeError, match="setup_basemaps"):
        merge_build_config(template, tmp_path / "run.yml", 0.01, {"subbasin": [1, 2]})
