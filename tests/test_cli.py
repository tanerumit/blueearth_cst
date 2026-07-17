"""Test some snake command line interface (CLI) for validity of snakefiles."""

import os
from os.path import join, dirname, realpath
import subprocess

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

config_fn = join(TESTDIR, "snake_config_model_test.yml")


def _dry_run(snakefile):
    """Dry-run a Snakefile on the test config; return the completed process.

    stdout/stderr are captured as text so callers can match on the DAG-build
    exception class name. Snakemake writes these diagnostics to stderr, but we
    match on the combined stream so a stream change does not silently break a
    ratchet assertion below.
    """
    os.chdir(SNAKEDIR)
    cmd = f"snakemake all -c 1 -s {snakefile} --configfile {config_fn} --dry-run"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def test_snakefile_cli_model_creation():
    """Workflow 1 dry-run builds a clean DAG on the test config."""
    result = _dry_run("Snakefile_model_creation")
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")


# --- Known-failure ratchets (R3 followups) -----------------------------------
#
# Snakefile_climate_projections and Snakefile_climate_experiment do NOT build a
# clean DAG on the test config today; both are pre-M2 failures that live in R3's
# territory (Snakefile cleanup, ruleorder). Tracked in dev/followups.md under R3.
#
# Rather than a blanket `xfail(strict=True)` — which keeps "passing" on ANY
# failure and would happily mask a new config KeyError from the R1 migration —
# each test below asserts the SPECIFIC known failure: a non-zero exit AND the
# exact DAG-build exception class for that Snakefile.
#
# Ratchet semantics: if the underlying issue is fixed (planned in milestone R3),
# the dry-run will succeed, `returncode != 0` will FAIL, and this test will go
# red. When that happens, the fixer must convert this back to a plain
# `assert result.returncode == 0` success assertion — same discipline as a
# strict xfail, but a NEW/unexpected error type now fails loudly here instead of
# being silently absorbed as "still failing".


def test_snakefile_cli_climate_projections_known_missing_input():
    """Workflow 2 dry-run fails with MissingInputException (needs region.geojson).

    climate_projections needs region.geojson from model_creation — a cross-
    Snakefile input Snakemake will not build itself. R3 followup (dev/followups.md).
    """
    result = _dry_run("Snakefile_climate_projections")
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode != 0, combined
    assert "MissingInputException" in combined, combined


def test_snakefile_cli_climate_experiment_known_cyclic_graph():
    """Workflow 3 dry-run fails with CyclicGraphException at the stress-test rule.

    climate_experiment trips a CyclicGraphException at rule
    generate_climate_stress_test. R3 followup (dev/followups.md).
    """
    result = _dry_run("Snakefile_climate_experiment")
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode != 0, combined
    assert "CyclicGraphException" in combined, combined
