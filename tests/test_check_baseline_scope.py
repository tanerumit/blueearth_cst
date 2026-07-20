"""Unit tests for the `--workflow` scope filter on check_baseline.py's `check`.

The filter (design ext1-1/ext2-1) tags each `TARGETS` entry with its owning
workflow and, when `--workflow` is given, builds ONE selected path universe and
applies it symmetrically to both the recorded manifest and the current on-disk
targets before the missing/diff/orphan/count logic. `record` stays unscoped by
construction (no `--workflow` flag), so a scoped run cannot truncate the
canonical manifest.

The fixture builds a synthetic project dir under `tmp_path` with valid files for
every real `TARGETS` template, then records a manifest against it via the same
`compute_manifest` code path used by the tool (so path keys match `resolve()`
byte-for-byte, including Windows separator quirks). No real Snakemake run.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev" / "scripts"))
import check_baseline as cb  # noqa: E402


def _write_target(path: str, kind: str) -> None:
    """Write a minimal but valid file for the given fingerprinter kind."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if kind == "nc":
        import xarray as xr

        xr.Dataset({"v": (("t",), np.array([1.0, 2.0, 3.0]))}).to_netcdf(p)
    elif kind == "csv":
        p.write_text("a,b\n1,2\n")
    elif kind == "yaml":
        p.write_text("project:\n  project_dir: synthetic\n")
    elif kind == "png":
        p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
    else:  # pragma: no cover - guard against a new untested kind
        raise ValueError(f"unhandled kind: {kind}")


@pytest.fixture
def project(tmp_path):
    """A synthetic project dir with all 14 targets present + a recorded manifest.

    Returns (project_dir, manifest_path). Both point under tmp_path.
    """
    project_dir = str(tmp_path)
    for _workflow, kind, template in cb.TARGETS:
        _write_target(cb.resolve(template, project_dir), kind)

    current, missing = cb.compute_manifest(project_dir)
    assert not missing, missing  # fixture sanity: all synthetic files exist
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {"version": cb.MANIFEST_VERSION, "project_dir": project_dir, "targets": current}
        )
    )
    return project_dir, manifest_path


def _check_ns(project_dir, manifest_path, workflow=None, tolerance=0.0):
    return argparse.Namespace(
        cmd="check",
        project_dir=project_dir,
        manifest=manifest_path,
        tolerance=tolerance,
        workflow=workflow,
    )


def _record_ns(project_dir, manifest_path):
    return argparse.Namespace(cmd="record", project_dir=project_dir, manifest=manifest_path)


def test_targets_tagged_with_expected_cardinality():
    """The shipping TARGETS carry the 4/7/3 workflow tags the count math relies on."""
    counts = Counter(workflow for workflow, _kind, _template in cb.TARGETS)
    assert counts == {
        "model_creation": 4,
        "climate_projections": 7,
        "climate_experiment": 3,
    }


def test_scoped_count_is_selected_not_full(project, capsys):
    """Assertion 1: `--workflow model_creation --workflow climate_projections`
    reports 11 targets, not the full 14."""
    project_dir, manifest_path = project
    rc = cb.cmd_check(
        _check_ns(project_dir, manifest_path,
                  workflow=["model_creation", "climate_projections"])
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK - 11 target(s)" in out


def test_selected_missing_target_fails(project, capsys):
    """Assertion 2: a selected target missing on disk -> non-zero, and named."""
    project_dir, manifest_path = project
    # Remove one climate_projections target (a selected workflow).
    victim = cb.resolve(
        "{clim_project_dir}/annual_change_scalar_stats_summary.csv", project_dir
    )
    Path(victim).unlink()

    rc = cb.cmd_check(
        _check_ns(project_dir, manifest_path,
                  workflow=["model_creation", "climate_projections"])
    )
    out = capsys.readouterr().out
    assert rc == 1
    assert victim in out


def test_unselected_missing_target_ignored(project, capsys):
    """Assertion 3: an unselected (workflow-3) target missing on disk is ignored
    by a scoped check -> returns 0, count stays 11."""
    project_dir, manifest_path = project
    # Remove a climate_experiment target; it is NOT in the selected universe.
    victim = cb.resolve("{exp_dir}/model_results/Qstats.csv", project_dir)
    Path(victim).unlink()

    rc = cb.cmd_check(
        _check_ns(project_dir, manifest_path,
                  workflow=["model_creation", "climate_projections"])
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK - 11 target(s)" in out


def test_record_rejects_workflow_flag_and_records_all(project, capsys):
    """Assertion 4: `record` has no `--workflow` (argparse SystemExit), and an
    unscoped record writes all 14 targets -> no scoped/truncating record path."""
    project_dir, manifest_path = project

    # (a) The record subparser rejects --workflow (no such flag on record).
    old_argv = sys.argv
    sys.argv = [
        "check_baseline.py", "record",
        "--project-dir", project_dir,
        "--manifest", str(manifest_path),
        "--workflow", "model_creation",
    ]
    try:
        with pytest.raises(SystemExit):
            cb.main()
    finally:
        sys.argv = old_argv

    # (b) An unscoped record writes all 14 targets.
    out_manifest = Path(manifest_path).parent / "recorded.json"
    rc = cb.cmd_record(_record_ns(project_dir, out_manifest))
    assert rc == 0
    written = json.loads(out_manifest.read_text())
    assert len(written["targets"]) == 14


def test_unscoped_check_spans_all_targets(project, capsys):
    """Assertion 5: `check` with no `--workflow` operates over all 14 targets,
    unchanged from before this commit."""
    project_dir, manifest_path = project
    rc = cb.cmd_check(_check_ns(project_dir, manifest_path, workflow=None))
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK - 14 target(s)" in out
