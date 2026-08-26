"""The v2 project config shape parses, composes and builds a DAG.

P1's acceptance surface (R14 `config-shape-p1-loader.task.md`). The fixture is
`tests/data/v2/project_config_v2_probe.yml`, hand-written rather than migrated:
P4 owns `tests/snake_config_fixture.yml` and migrates it WITH the rewriter, so
a P1 test that edited it would be doing P4's job with a worse tool.

**This module records how far the T2 migration has got, as an executable
statement rather than a note.** P1 moved the T1 reads — the `project:`,
`basin:`, `climate:` and `model:` sections, which is what `shared:` dissolved
into — and stopped. P1b is moving the T2 reads, the per-workflow key renames,
one workflow at a time; each slice moves its entry point from ``V2_BLOCKED``
to ``V2_CLEAN`` in the same commit as the readers, so no intermediate commit
is red.

Done so far: WF1 (`C-22`, `C-56`) and WF2 (`C-25`, `C-59`, `C-60`, `C-63`).
Still owed by WF3: `C-68`, `C-31`, `C-32`, `C-33`, `C-67`, `C-69`, `C-29`,
`C-34`. ``test_wf3_stops_at_the_first_t2_renamed_key`` asserts the remaining
boundary WITH the key it stops on, so the slice that moves those reads has a
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

#: The entry points that dry-run clean on v2. P1 delivered the first two by
#: moving the T1 reads; P1b added `analyze_projections` by moving WF2's T2 key
#: readers (`C-25`, `C-59`, `C-60`, `C-63`).
V2_CLEAN = ("analyze_climate", "build_model", "analyze_projections")

#: The two that do not, and the key each stops on. Naming the key is the point:
#: it turns "P1 left this" into "here is the next thing to move".
V2_BLOCKED = {
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
def test_wf3_stops_at_the_first_t2_renamed_key(snakefile, key):
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


def test_reference_window_takes_no_water_year_offset(tmp_path):
    """`C-74` / D-7.4: WF2's reference window is CALENDAR years.

    `hydrological_year_bounds()` trims to complete water years one layer down,
    so a `reference_window` routed through the water-year path would have the
    offset applied twice and every change factor would move. Nothing else
    catches that: `check_baseline` is out of scope for the phase that wrote
    this reader, and the probe fixture declares `water_year_start: Jan`, under
    which a double offset is exactly zero and therefore invisible.

    So the assertion is a COMPARISON against a non-Jan water year, not a value.
    """
    import shutil

    import yaml

    from blueearth_cst.projections import reference_window as _rw
    from blueearth_cst.shared.snake_utils import window_year_pair

    def _effective(water_year_start):
        for source in V2_CONFIG.parent.glob("project_config_v2_probe*.yml"):
            shutil.copy(source, tmp_path / source.name)
        target = tmp_path / V2_CONFIG.name
        doc = yaml.safe_load(target.read_text(encoding="utf-8"))
        doc["climate"]["water_year_start"] = water_year_start
        target.write_text(yaml.safe_dump(doc), encoding="utf-8")
        composed = load_composed_config(target)
        window = composed["workflows"]["analyze_projections"]["reference_window"]
        pair = window_year_pair(window, "reference_window")
        return _rw.clip_reference_window(pair).effective

    assert _effective("Jan") == _effective("Oct")
