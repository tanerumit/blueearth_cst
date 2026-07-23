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
