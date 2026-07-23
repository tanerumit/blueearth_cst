"""Unit tests for dev/scripts/semantic_tree_diff.py (R06 milestone tooling).

Each comparator: equal inputs pass; a seeded perturbation fails. The NetCDF
comparator gets a dedicated coordinate-PERMUTATION test -- the discriminator
that proves it is element-wise (no realignment), not aggregate-stat based
(design §9 ext2-02).
"""

import os
import sys

import numpy as np
import pytest
import xarray as xr
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dev", "scripts"))
import semantic_tree_diff as std  # noqa: E402


# ---------------------------------------------------------------------------
# .nc element-wise comparator
# ---------------------------------------------------------------------------

def _write_nc(path, data, x=(0, 1, 2), attrs=None):
    ds = xr.Dataset(
        {"var": (("x",), np.asarray(data, dtype=float))},
        coords={"x": list(x)},
        attrs=attrs or {},
    )
    ds.to_netcdf(path)


def test_nc_equal_passes(tmp_path):
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    _write_nc(a, [1.0, 2.0, 3.0])
    _write_nc(b, [1.0, 2.0, 3.0])
    assert std.compare_nc(str(a), str(b), tol=0.0) == []


def test_nc_value_perturbation_fails(tmp_path):
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    _write_nc(a, [1.0, 2.0, 3.0])
    _write_nc(b, [1.0, 2.0, 3.5])  # one element perturbed
    diffs = std.compare_nc(str(a), str(b), tol=1e-9)
    assert diffs and any("out of tolerance" in d for d in diffs)


def test_nc_coordinate_permutation_fails(tmp_path):
    """The acid test: same data + coords but permuted coord ORDER must FAIL.

    A permutation preserves every aggregate stat (min/max/mean/std/count) --
    only an element-wise, no-realign comparator catches it."""
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    # same {x: value} pairs, different stored order
    _write_nc(a, [10.0, 20.0, 30.0], x=(0, 1, 2))
    _write_nc(b, [30.0, 10.0, 20.0], x=(2, 0, 1))
    diffs = std.compare_nc(str(a), str(b), tol=0.0)
    assert diffs, "permuted coordinate order must FAIL (no realignment)"


def test_nc_nan_mask_mismatch_fails(tmp_path):
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    _write_nc(a, [1.0, np.nan, 3.0])
    _write_nc(b, [1.0, 2.0, 3.0])
    diffs = std.compare_nc(str(a), str(b), tol=1e-9)
    assert any("NaN mask" in d for d in diffs)


def test_nc_nonvolatile_attr_change_fails(tmp_path):
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    _write_nc(a, [1.0, 2.0, 3.0], attrs={"units": "m3/s"})
    _write_nc(b, [1.0, 2.0, 3.0], attrs={"units": "cfs"})
    diffs = std.compare_nc(str(a), str(b), tol=0.0)
    assert any("attrs" in d for d in diffs)


def test_nc_volatile_attr_change_passes(tmp_path):
    a = tmp_path / "a.nc"
    b = tmp_path / "b.nc"
    _write_nc(a, [1.0, 2.0, 3.0], attrs={"history": "created monday"})
    _write_nc(b, [1.0, 2.0, 3.0], attrs={"history": "created tuesday"})
    assert std.compare_nc(str(a), str(b), tol=0.0) == []


# ---------------------------------------------------------------------------
# .toml normalized comparator
# ---------------------------------------------------------------------------

def test_toml_key_order_and_comments_pass(tmp_path):
    a = tmp_path / "a.toml"
    b = tmp_path / "b.toml"
    a.write_text('# comment A\n[s]\nx = 1\ny = 2\n')
    b.write_text('[s]\ny = 2\nx = 1\n# comment B\n')  # reordered + diff comment
    assert std.compare_toml(str(a), str(b)) == []


def test_toml_value_change_fails(tmp_path):
    a = tmp_path / "a.toml"
    b = tmp_path / "b.toml"
    a.write_text('[s]\nx = 1\n')
    b.write_text('[s]\nx = 2\n')
    diffs = std.compare_toml(str(a), str(b))
    assert diffs and "s.x" in diffs[0]


# ---------------------------------------------------------------------------
# copied-config YAML normalize-then-compare
# ---------------------------------------------------------------------------

def _write_yaml(path, doc):
    path.write_text(yaml.safe_dump(doc))


def test_copied_config_mapped_path_normalizes(tmp_path):
    """The documented old->new path rewrite is the ONLY allowed difference."""
    ref = tmp_path / "config" / "ref.yml"
    cur = tmp_path / "config" / "cur.yml"
    ref.parent.mkdir(parents=True)
    _write_yaml(ref, {"project": {"data_sources": "config/deltares_data.yml"}})
    _write_yaml(cur, {"project": {"data_sources": "config/catalogs/deltares_data.yml"}})
    assert std.compare_copied_config(str(ref), str(cur)) == []


def test_copied_config_all_four_keys_normalize(tmp_path):
    """data_sources_climate is in the map (commit-2 as-built inventory)."""
    ref = tmp_path / "ref.yml"
    cur = tmp_path / "cur.yml"
    _write_yaml(ref, {
        "project": {
            "data_sources": "config/deltares_data.yml",
            "data_sources_climate": "config/cmip6_data.yml",
        },
        "workflows": {"model_creation": {
            "model_build_config": "config/wflow_build_model.yml",
            "waterbodies_config": "config/wflow_update_waterbodies.yml",
        }},
    })
    _write_yaml(cur, {
        "project": {
            "data_sources": "config/catalogs/deltares_data.yml",
            "data_sources_climate": "config/catalogs/cmip6_data.yml",
        },
        "workflows": {"model_creation": {
            "model_build_config": "config/templates/wflow_build_model.yml",
            "waterbodies_config": "config/templates/wflow_update_waterbodies.yml",
        }},
    })
    assert std.compare_copied_config(str(ref), str(cur)) == []


def test_copied_config_reflexive_self_compare_clean(tmp_path):
    """Reflexivity: comparing a pre-R6 (OLD-path) snapshot against itself is
    clean. Pins the bug the self-smoke caught -- the directional normalize must
    not false-fail on identical inputs."""
    x = tmp_path / "x.yml"
    _write_yaml(x, {
        "project": {
            "data_sources": "config/deltares_data.yml",
            "data_sources_climate": "config/cmip6_data.yml",
        },
    })
    assert std.compare_copied_config(str(x), str(x)) == []


def test_copied_config_nonpath_value_change_fails(tmp_path):
    """A non-path value change is a real FAIL even with a valid path rewrite."""
    ref = tmp_path / "ref.yml"
    cur = tmp_path / "cur.yml"
    _write_yaml(ref, {"project": {"data_sources": "config/deltares_data.yml"},
                      "shared": {"clim_historical": "era5"}})
    _write_yaml(cur, {"project": {"data_sources": "config/catalogs/deltares_data.yml"},
                      "shared": {"clim_historical": "chirps"}})  # drift
    diffs = std.compare_copied_config(str(ref), str(cur))
    assert diffs and any("clim_historical" in d for d in diffs)


def test_copied_config_unmapped_path_value_fails(tmp_path):
    """A path value not in the map is left untouched and must fail equality."""
    ref = tmp_path / "ref.yml"
    cur = tmp_path / "cur.yml"
    _write_yaml(ref, {"project": {"data_sources": "config/some_other.yml"}})
    _write_yaml(cur, {"project": {"data_sources": "config/catalogs/some_other.yml"}})
    diffs = std.compare_copied_config(str(ref), str(cur))
    assert diffs


# ---------------------------------------------------------------------------
# walker: self-compare clean; a perturbed file fails; exclusions honored
# ---------------------------------------------------------------------------

def test_diff_trees_self_compare_clean(tmp_path):
    root = tmp_path / "tree"
    (root / "config").mkdir(parents=True)
    _write_yaml(root / "config" / "snake.yml", {"project": {"data_sources": "config/x.yml"}})
    (root / "a.toml").write_text("[s]\nx = 1\n")
    _write_nc(root / "d.nc", [1.0, 2.0, 3.0])
    report = std.diff_trees(str(root), str(root), tol=0.0)
    assert report["passed"], std.format_report(report)
    assert report["n_compared"] == 3


def test_diff_trees_detects_perturbation(tmp_path):
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    (ref).mkdir()
    (cur).mkdir()
    _write_nc(ref / "d.nc", [1.0, 2.0, 3.0])
    _write_nc(cur / "d.nc", [1.0, 2.0, 9.0])  # perturbed
    report = std.diff_trees(str(ref), str(cur), tol=1e-9)
    assert not report["passed"]
    assert report["failures"]


def test_diff_trees_excludes_logs_and_benchmarks(tmp_path):
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    for root in (ref, cur):
        (root / "logs").mkdir(parents=True)
        (root / "benchmarks").mkdir(parents=True)
        (root / ".snakemake").mkdir(parents=True)
    (ref / "logs" / "a.log").write_text("ref timestamp 1")
    (cur / "logs" / "a.log").write_text("cur timestamp 2")  # differs, but excluded
    (ref / "benchmarks" / "b.txt").write_text("10s")
    (cur / "benchmarks" / "b.txt").write_text("99s")
    report = std.diff_trees(str(ref), str(cur), tol=0.0)
    assert report["passed"], std.format_report(report)
    assert report["n_compared"] == 0


def test_diff_trees_reports_missing_and_extra(tmp_path):
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    ref.mkdir()
    cur.mkdir()
    (ref / "only_ref.csv").write_text("a,b\n1,2\n")
    (cur / "only_cur.csv").write_text("a,b\n1,2\n")
    report = std.diff_trees(str(ref), str(cur), tol=0.0)
    assert not report["passed"]
    assert report["missing"] and report["extra"]


# ---------------------------------------------------------------------------
# P3-1: path map + allowlist + path-aware toml comparator (design §6a, commit 5)
# ---------------------------------------------------------------------------

P31_MAP = std.build_p31_path_map("experiment", "era5_20000101_20201231")


def _write_run_toml(path, path_static, path_forcing="../realization_1/x.nc",
                    path_input="../../../hydrology_model/instate/instates.nc"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[input]\n"
        f'path_static = "{path_static}"\n'
        f'path_forcing = "{path_forcing}"\n'
        "[state]\n"
        f'path_input = "{path_input}"\n'
        'path_output = "outstates.nc"\n'
        "[csv]\n"
        'path = "output.csv"\n'
    )


def test_toml_path_static_relocation_passes(tmp_path):
    """§6a positive: old-depth vs new-depth path_static both resolve to
    project-relative hydrology_model/staticmaps.nc (no map entry needed)."""
    ref_root = tmp_path / "ref"
    cur_root = tmp_path / "cur"
    ref_toml = ref_root / "hydrology_model" / "run_climate_experiment" / "a.toml"
    cur_toml = cur_root / "experiments" / "experiment" / "model_runs" / "a.toml"
    _write_run_toml(ref_toml, "../staticmaps.nc",
                    path_forcing="../../climate_experiment/realization_1/x.nc",
                    path_input="../instate/instates.nc")
    _write_run_toml(cur_toml, "../../../hydrology_model/staticmaps.nc")
    diffs = std.compare_toml(str(ref_toml), str(cur_toml),
                             ref_root=str(ref_root), cur_root=str(cur_root),
                             path_map=P31_MAP)
    assert diffs == [], diffs


def test_toml_path_forcing_prefix_map_passes(tmp_path):
    """§6a positive: path_forcing target moved with exp_dir; the DIRECTORY-PREFIX
    rule climate_experiment/ -> experiments/experiment/ translates the ref
    target onto the cur one. The target is a temp() file existing in NEITHER
    tree -- asserts the prefix-rewrite form of the map, not a per-file table."""
    ref_root = tmp_path / "ref"
    cur_root = tmp_path / "cur"
    ref_toml = ref_root / "hydrology_model" / "run_climate_experiment" / "a.toml"
    cur_toml = cur_root / "experiments" / "experiment" / "model_runs" / "a.toml"
    _write_run_toml(ref_toml, "../staticmaps.nc",
                    path_forcing="../../climate_experiment/realization_1/inmaps_rlz_1_cst_1.nc",
                    path_input="../instate/instates.nc")
    _write_run_toml(cur_toml, "../../../hydrology_model/staticmaps.nc",
                    path_forcing="../realization_1/inmaps_rlz_1_cst_1.nc")
    # the forcing target exists in neither tree (temp()-deleted)
    assert not (ref_root / "climate_experiment").exists()
    assert not (cur_root / "experiments" / "experiment" / "realization_1").exists()
    diffs = std.compare_toml(str(ref_toml), str(cur_toml),
                             ref_root=str(ref_root), cur_root=str(cur_root),
                             path_map=P31_MAP)
    assert diffs == [], diffs


def test_toml_path_static_mis_repoint_fails(tmp_path):
    """§6a negative: cur path_static resolving to a DIFFERENT project-relative
    target fails, naming the field (mis-repoint caught, not hidden)."""
    ref_root = tmp_path / "ref"
    cur_root = tmp_path / "cur"
    ref_toml = ref_root / "hydrology_model" / "run_climate_experiment" / "a.toml"
    cur_toml = cur_root / "experiments" / "experiment" / "model_runs" / "a.toml"
    _write_run_toml(ref_toml, "../staticmaps.nc",
                    path_forcing="../../climate_experiment/realization_1/x.nc",
                    path_input="../instate/instates.nc")
    _write_run_toml(cur_toml, "../../../hydrology_model/staticmaps_WRONG.nc")
    diffs = std.compare_toml(str(ref_toml), str(cur_toml),
                             ref_root=str(ref_root), cur_root=str(cur_root),
                             path_map=P31_MAP)
    assert diffs and any("path_static" in d and "mis-repoint" in d for d in diffs)


def test_diff_trees_path_map_pairs_moved_files(tmp_path):
    """A pure move (same bytes, mapped path) is content-diffed and CLEAN --
    not MISSING+EXTRA."""
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    (ref / "climate_experiment" / "model_results").mkdir(parents=True)
    (cur / "experiments" / "experiment" / "model_results").mkdir(parents=True)
    (ref / "climate_experiment" / "model_results" / "Qstats.csv").write_text("a,b\n1,2\n")
    (cur / "experiments" / "experiment" / "model_results" / "Qstats.csv").write_text("a,b\n1,2\n")
    (ref / "climate_historical" / "raw_data").mkdir(parents=True)
    (cur / "climate_historical" / "era5_20000101_20201231").mkdir(parents=True)
    _write_nc(ref / "climate_historical" / "raw_data" / "extract_historical.nc",
              [1.0, 2.0, 3.0])
    _write_nc(cur / "climate_historical" / "era5_20000101_20201231" / "extract_historical.nc",
              [1.0, 2.0, 3.0])
    report = std.diff_trees(str(ref), str(cur), tol=0.0, path_map=P31_MAP)
    assert report["passed"], std.format_report(report)
    assert report["n_compared"] == 2


def test_diff_trees_path_map_value_diff_still_fails(tmp_path):
    """The map pairs moved files but does NOT mask a value change (risk-4)."""
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    (ref / "climate_experiment" / "model_results").mkdir(parents=True)
    (cur / "experiments" / "experiment" / "model_results").mkdir(parents=True)
    (ref / "climate_experiment" / "model_results" / "Qstats.csv").write_text("a,b\n1,2\n")
    (cur / "experiments" / "experiment" / "model_results" / "Qstats.csv").write_text("a,b\n1,999\n")
    report = std.diff_trees(str(ref), str(cur), tol=0.0, path_map=P31_MAP)
    assert not report["passed"]
    assert report["failures"] and not report["missing"] and not report["extra"]


def test_diff_trees_allowlist_gate_contract(tmp_path):
    """Allowlisted EXTRA entries pass (reported as allowed); an unexplained
    EXTRA fails the gate."""
    allow = std.build_p31_allowlist("experiment", "era5_20000101_20201231")
    ref = tmp_path / "ref"
    cur = tmp_path / "cur"
    ref.mkdir()
    (cur / "experiments" / "experiment").mkdir(parents=True)
    (cur / "climate_historical" / "era5_20000101_20201231").mkdir(parents=True)
    (cur / "experiments" / "experiment" / ".project_consistency_ok").write_text("ok")
    (cur / "climate_historical" / "era5_20000101_20201231" / ".guard_ok").write_text("ok")
    report = std.diff_trees(str(ref), str(cur), tol=0.0,
                            path_map=P31_MAP, allowlist=allow)
    assert report["passed"], std.format_report(report)
    assert len(report["allowed"]) == 2
    # now an unexplained extra appears -> gate FAILURE
    (cur / "experiments" / "experiment" / "unexplained.csv").write_text("a\n1\n")
    report = std.diff_trees(str(ref), str(cur), tol=0.0,
                            path_map=P31_MAP, allowlist=allow)
    assert not report["passed"]
    assert report["extra"] == ["experiments/experiment/unexplained.csv"]


def test_diff_trees_self_compare_clean_with_p31_map(tmp_path):
    """Self-diff smoke: a NEW-layout tree diffed against itself with the map
    active is clean (old-layout prefixes match nothing; map is a no-op)."""
    root = tmp_path / "tree"
    (root / "experiments" / "experiment" / "model_results").mkdir(parents=True)
    (root / "experiments" / "experiment" / "model_results" / "Qstats.csv").write_text("a,b\n1,2\n")
    _write_run_toml(root / "experiments" / "experiment" / "model_runs" / "a.toml",
                    "../../../hydrology_model/staticmaps.nc")
    report = std.diff_trees(str(root), str(root), tol=0.0, path_map=P31_MAP,
                            allowlist=std.build_p31_allowlist(
                                "experiment", "era5_20000101_20201231"))
    assert report["passed"], std.format_report(report)
