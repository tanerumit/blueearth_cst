"""The v2 project config shape parses, composes and builds a DAG.

P1's acceptance surface (R14 `config-shape-p1-loader.task.md`). The fixture is
`tests/data/v2/project_config_v2_probe.yml`, hand-written rather than migrated:
P4 owns `tests/snake_config_fixture.yml` and migrates it WITH the rewriter, so
a P1 test that edited it would be doing P4's job with a worse tool.

**This module also records where P1's scope line falls, as an executable
statement rather than a note.** P1 moved the T1 reads — the `project:`,
`basin:`, `climate:` and `model:` sections, which is what `shared:` dissolved
into. It did NOT move the T2 reads: the per-workflow key renames (`C-22`,
`C-25`, `C-29`, `C-31`, `C-32`, `C-33`, `C-56`, `C-59`, `C-60`, `C-66`,
`C-67`, `C-68`, `C-69`) are ~280 sites across `blueearth_cst/experiment/`,
`projections/` and `model/` — three package directories no R14 phase claims,
and none of them a Snakefile.

So two entry points dry-run clean on v2 today and two stop at their first
T2-renamed key. ``test_wf2_and_wf3_stop_at_the_first_t2_renamed_key`` asserts
that, WITH the key it stops on, so the phase that moves those reads has a
failing test that turns green rather than a paragraph it has to find.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from blueearth_cst.shared.config_composition import load_composed_config

REPO_ROOT = Path(__file__).resolve().parent.parent
V2_CONFIG = REPO_ROOT / "tests" / "data" / "v2" / "project_config_v2_probe.yml"

#: The entry points whose config reads P1 moved in full.
V2_CLEAN = ("analyze_climate", "build_model")

#: The two that do not, and the key each stops on. Naming the key is the point:
#: it turns "P1 left this" into "here is the next thing to move".
V2_BLOCKED = {
    "analyze_projections": "clim_project",  # C-25 -> `ensemble:`
    "run_stress_test": "stress_test",  # C-68 -> `climate_perturbations:`
}


def _dry_run(snakefile: str) -> str:
    """Dry-run one entry point on the v2 config; return the combined output."""
    result = subprocess.run(
        f"snakemake all -c 1 -s {snakefile}.smk --configfile {V2_CONFIG} --dry-run",
        shell=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return (result.stdout or "") + (result.stderr or "")


def test_the_v2_fixture_composes():
    """The shape parses and composes before any DAG is asked for.

    Cheapest of the three claims, and the one whose failure is least ambiguous:
    a composition failure is the loader, a DAG failure is a rule.
    """
    composed = load_composed_config(V2_CONFIG)
    assert composed["schema_version"] == 2
    assert set(composed) == {
        "schema_version",
        "project",
        "basin",
        "climate",
        "model",
        "workflows",
    }
    assert "shared" not in composed
    assert composed["climate"]["selected"] == "era5"
    assert composed["climate"]["window"] == {"start": 2000, "end": 2020}


@pytest.mark.workflow_contract
@pytest.mark.parametrize("snakefile", V2_CLEAN)
def test_an_entry_point_dry_runs_clean_on_v2(snakefile):
    """P1's acceptance criterion, for the entry points it reaches."""
    combined = _dry_run(snakefile)
    assert "Building DAG of jobs" in combined, combined[-3000:]
    assert "Error in file" not in combined, combined[-3000:]


@pytest.mark.workflow_contract
@pytest.mark.parametrize(("snakefile", "key"), sorted(V2_BLOCKED.items()))
def test_wf2_and_wf3_stop_at_the_first_t2_renamed_key(snakefile, key):
    """The scope line, asserted so the next phase inherits a test, not a note.

    This is a RATCHET in the unusual direction: it passes because the work is
    not done. When the phase that moves the T2 reads lands, this test fails —
    and that failure is the signal to move the entry point into ``V2_CLEAN``
    above, where the real assertion lives. Deleting it silently would lose the
    only executable record that P1 stopped here on purpose.
    """
    combined = _dry_run(snakefile)
    assert key in combined, (
        f"{snakefile} no longer stops on {key!r}. If the T2 reads have been "
        f"moved, move {snakefile!r} into V2_CLEAN and delete this case — it "
        "exists only to mark the boundary."
    )
    assert "Building DAG of jobs" not in combined or "Error" in combined


def test_every_declared_t2_file_exists():
    """D-7.9: the file and its ``config_path`` stanza travel together.

    An empty T2 file is legal and a MISSING one with ``config_path`` still
    declared is a hard parse error, so a fixture that lost a sibling would fail
    with a refusal about the fixture rather than about the shape under test.
    """
    directory = V2_CONFIG.parent
    import yaml

    t1 = yaml.safe_load(V2_CONFIG.read_text(encoding="utf-8"))
    for name, stanza in t1["workflows"].items():
        declared = stanza.get("config_path")
        assert declared, f"workflows.{name} declares no config_path"
        assert (directory / declared).is_file(), (
            f"workflows.{name}.config_path names {declared!r}, which is not "
            f"beside {V2_CONFIG.name} — a relative config_path anchors at the "
            "project file's own directory, not the working directory"
        )
        assert os.path.basename(declared) == declared, (
            "the fixture's config_path values are bare sibling filenames, so "
            "the set stays relocatable"
        )
