"""Gate 2 (a-h): pure script-unit tests for the wf3 drift-guard comparator.

These call ``compare_project_consistency`` directly on staged config/snapshot
pairs — NO Snakemake, no rerun-triggers (that is gate 2b,
``test_guard_invalidation.py``). Design: dev/milestones/p31/experiment-structure-design.md
§7 gate 2, §3b.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from blueearth_cst.experiment.check_project_consistency import (  # noqa: E402
    compare_project_consistency,
)

# A minimal but structurally faithful full config (R01 sectioned schema),
# mirroring test_case/snake_config_baseline.yml at the guarded
# sections. The experiment sections that vary per experiment are present but
# deliberately NOT guarded.
_BASE_CFG = {
    "schema_version": 2,
    "project": {
        "project_dir": "test_case/test_local",
        # `C-07` deleted `static_dir`; `C-40` renamed `data_sources` to
        # `catalog`; `C-39` pushed the climate catalog DOWN to the WF2 file,
        # where it has its only reader.
        "catalog": "config/catalogs/deltares_data.yml",
    },
    "basin": {
        "region": "{'subbasin': [9.666, 0.4476], 'uparea': 100}",
        "resolution": 0.00833,
    },
    "climate": {
        "selected": "era5",
        "sources": ["era5"],
        # `C-70`: INCLUSIVE YEARS, not ISO timestamps.
        "window": {"start": 2000, "end": 2020},
    },
    # `C-19`: `wflow_outvars` is `model.outvars`. Still guarded as a LEAF, so a
    # post-build edit is refused at rule 3.01 — the mechanism is unchanged and
    # only the path moved.
    "model": {"outvars": ["river discharge"]},
    "workflows": {
        "build_model": {
            "enabled": True,
            # `C-22`: both paths sit under `engine:` now. The nesting matters to
            # this module specifically -- `_normalize_paths` recurses, so the
            # normalization map keys on the LEAF and has to find it at depth.
            "engine": {
                "build_config": "config/defaults/wflow_build_model.yml",
                "waterbodies_config": "config/defaults/wflow_update_waterbodies.yml",
            },
        },
        "analyze_projections": {
            "enabled": True,
            "clim_project": "cmip6",
            "models": ["NOAA-GFDL/GFDL-ESM4"],
            "scenarios": ["ssp245", "ssp585"],
        },
        "run_stress_test": {
            "experiment_name": "experiment",
            "realizations_num": 2,
        },
    },
}


def _write(path: Path, cfg: dict) -> Path:
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


@pytest.fixture()
def snapshots(tmp_path):
    """Write matching wf1 + wf2 snapshots from _BASE_CFG; return their paths."""
    wf1 = _write(tmp_path / "snake_config_build_model.yml", _BASE_CFG)
    wf2 = _write(tmp_path / "snake_config_analyze_projections.yml", _BASE_CFG)
    return wf1, wf2


def test_a_identical_sections_pass(snapshots):
    wf1, wf2 = snapshots
    diffs = compare_project_consistency(copy.deepcopy(_BASE_CFG), wf1, wf2)
    assert diffs == []


def test_b_mutated_basin_resolution_fails_naming_key(snapshots):
    wf1, wf2 = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["basin"]["resolution"] = 0.05
    diffs = compare_project_consistency(live, wf1, wf2)
    assert diffs
    assert any("basin" in d and "resolution" in d for d in diffs)


def test_c_mutated_build_model_fails(snapshots):
    wf1, wf2 = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["workflows"]["build_model"]["engine"]["waterbodies_config"] = "other.yml"
    diffs = compare_project_consistency(live, wf1, wf2)
    assert diffs
    assert any("workflows.build_model" in d for d in diffs)


def test_c2_mutated_shared_wflow_outvars_fails(snapshots):
    """The hoist must not WEAKEN this guard, and nothing else would catch it.

    ``wflow_outvars`` sat inside ``workflows.build_model`` until R13, so a
    post-build edit was refused here. Moved to ``shared:`` and left unguarded,
    the same edit would sail past rule 3.01 and first surface mid-experiment as
    ``export_wflow_results``' missing-column error -- a whole workflow away
    from its cause, and after the expensive part has run.

    Guarded as a LEAF rather than by widening the comparand to ``shared``
    whole: every guard param has to stay experiment-invariant, because the
    guard's second output is shared across experiments.
    """
    wf1, wf2 = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["model"]["outvars"] = ["actual evapotranspiration"]
    diffs = compare_project_consistency(live, wf1, wf2)
    assert diffs
    assert any("model.outvars" in d for d in diffs), diffs


def test_d_flat_vs_binned_paths_pass(tmp_path):
    """Symmetric normalization: a flat-path experiment config vs a binned
    snapshot converges (design §3b, gate 2d)."""
    # Snapshot uses NEW binned catalog paths; experiment config uses OLD flat
    # paths for the mapped keys. Symmetric normalization makes them equal.
    snapshot_cfg = copy.deepcopy(_BASE_CFG)
    wf1 = _write(tmp_path / "snake_config_build_model.yml", snapshot_cfg)

    live = copy.deepcopy(_BASE_CFG)
    live["project"]["catalog"] = "config\\deltares_data.yml"
    live["workflows"]["build_model"]["engine"]["build_config"] = (
        "config\\wflow_build_model.yml"
    )
    live["workflows"]["build_model"]["engine"]["waterbodies_config"] = (
        "config\\wflow_update_waterbodies.yml"
    )

    diffs = compare_project_consistency(live, wf1, wf2_snapshot_path=None)
    assert diffs == []


def test_e_missing_wf1_snapshot_fails_with_run_first_message(tmp_path):
    missing = tmp_path / "does_not_exist.yml"
    diffs = compare_project_consistency(copy.deepcopy(_BASE_CFG), missing)
    assert diffs
    assert any(
        "run build_model.smk first" in d.lower()
        or "run snakefile_build_model first" in d.lower()
        for d in diffs
    )


def test_f_mutated_historical_window_passes_not_guarded(snapshots):
    wf1, wf2 = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["climate"]["window"]["end"] = 2010
    diffs = compare_project_consistency(live, wf1, wf2)
    assert diffs == []


def test_g_mutated_analyze_projections_with_wf2_snapshot_fails(snapshots):
    wf1, wf2 = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["workflows"]["analyze_projections"]["scenarios"] = ["ssp126"]
    diffs = compare_project_consistency(live, wf1, wf2)
    assert diffs
    assert any("workflows.analyze_projections" in d for d in diffs)


def test_h_mutated_analyze_projections_without_wf2_snapshot_passes(snapshots):
    wf1, _ = snapshots
    live = copy.deepcopy(_BASE_CFG)
    live["workflows"]["analyze_projections"]["scenarios"] = ["ssp126"]
    # No wf2 snapshot -> projections section unchecked + logged, passes.
    diffs = compare_project_consistency(live, wf1, wf2_snapshot_path=None)
    assert diffs == []
