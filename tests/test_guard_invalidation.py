"""Gate 2b (i-l) + gate 2c: drift-guard invalidation and fresh-project checks.

Gate 2b is a DAG/rerun-trigger INTEGRATION check, NOT a comparator unit test
(that is ``test_check_project_consistency.py``). It runs the real
``check_project_consistency`` rule through Snakemake against a staged
``project_dir`` and reads Snakemake's scheduling reason from ``--dry-run``
after each comparand mutation, WITHOUT deleting the sentinel between
mutations. Design: dev/milestones/p31/experiment-structure-design.md §7 gates 2b/2c, §3c.

Mechanics: "Params have changed since last execution" is reported only when
the rule's outputs EXIST and the recorded params differ — from a cold dir a
dry-run reports "missing output files", which proves nothing about the
rerun-trigger. So the guard rule is executed ONCE for real (cheap: yaml
compare + two tiny text outputs; no data mirror, no Julia) to seed the
``.snakemake`` provenance metadata, then every mutation is checked
edit-then-``--dry-run``. The real execution is never repeated between
mutations — that would move the recorded-params baseline and invalidate the
(l) revert check.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared.snake_utils import (
    historical_window_bounds,
    slugify_window,
)

pytestmark = pytest.mark.workflow_contract

TESTDIR = Path(__file__).resolve().parent
SNAKEDIR = TESTDIR.parent
CONFIG_FN = TESTDIR / "project_config_fixture.yml"

sys.path.insert(0, str(SNAKEDIR / "dev" / "scripts"))
import cross_workflow_inputs as cwi  # noqa: E402

from blueearth_cst.shared.config_composition import load_composed_config  # noqa: E402
from tests.conftest import write_config  # noqa: E402


def _run(args, cfg_path):
    """Invoke snakemake on run_stress_test.smk; return the process.

    ``args`` (targets/flags) go BEFORE ``--configfile`` — a positional target
    after it would be swallowed by ``--configfile``'s greedy nargs. The repo's
    workflow profile (``profiles/default``) sets ``quiet: reason``, which
    suppresses exactly the per-job "Reason:" block gate 2b asserts on, so the
    profile is disabled here.
    """
    cmd = (
        f"snakemake {args} --workflow-profile none -c 1 "
        f'-s run_stress_test.smk --configfile "{cfg_path}"'
    )
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=str(SNAKEDIR)
    )


@pytest.fixture()
def staged_project(tmp_path):
    """A staged project_dir carrying EVERY wf3 leaf input.

    The snapshots are byte-serialized from the SAME parsed config the live
    ``--configfile`` uses, so the guard passes initially. Returns
    (cfg_path, project_dir, wf1_snapshot, wf2_snapshot, sentinel_path).

    "Every leaf" is load-bearing, not incidental: gate 2c(iii) below asserts
    that ``--unlock`` SUCCEEDS once the wf1 snapshot is restored, and on the
    pinned Snakemake ``--unlock`` builds the DAG first, so it fails on ANY
    missing leaf. A leaf the fixture forgets turns that assertion into a
    failure that looks like a guard defect and is not one.
    """
    base = load_composed_config(CONFIG_FN)
    pdir = tmp_path / "proj"
    base["project"]["project_dir"] = str(pdir).replace("\\", "/")
    experiment = base["workflows"]["run_stress_test"]["experiment_name"]

    # THE LEAF SET IS NOT MAINTAINED HERE any more. It lives in
    # `cross_workflow_inputs` with the other two stagers, and
    # `tests/test_cross_workflow_inputs.py` proves it complete and minimal
    # against the real DAG. This fixture is exactly why: R9 P4's rule 3.01c
    # `write_model_reference` is the first wf3 rule to declare model FILES as
    # inputs, so the model leaves joined the wf1 snapshot as things `--unlock`
    # needs on disk; test_cli.py's equivalent was updated and this one was not,
    # and 2c(iii) went red looking like a guard defect (R9 P5 F3). The phase
    # gate could not have caught it either -- this module is
    # `workflow_contract`, which `pixi run test-fast` excludes by definition.
    #
    # Two EXTRAS beyond the leaves, both deliberate non-leaves:
    #   * the wf2 snapshot, which the guard reads as a `params` path and
    #     existence-checks in its script (the projections overlay is optional
    #     and must not be force-required) -- this module's assertions are about
    #     that COMPARISON, not about the DAG;
    #   * the region, which since ADR 0003 wf3 reads not at all, staged only to
    #     keep the project looking like a completed wf1 run.
    config_text = yaml.safe_dump(base)
    cwi.stage(pdir, config_text, extras=(cwi.EXTRA_REGION, cwi.EXTRA_WF2_SNAPSHOT))
    snap_dir = pdir / "config" / "runs"
    wf1 = snap_dir / "project_config_build_model.yml"
    wf2 = snap_dir / "project_config_analyze_projections.yml"

    cfg_path = write_config(tmp_path, base, stem="project_config_staged")

    # exp_dir as defined in run_stress_test.smk (commit 2 moved it to
    # experiments/<name>/).
    sentinel = pdir / "experiments" / experiment / ".project_consistency_ok"
    # Key-level guard artifact lives under the dataset+window keyed store dir
    # (commit 4). Derive the key exactly as the Snakefile does.
    # `C-70` retyped the window to INCLUSIVE YEARS while the store key stayed
    # ISO at day resolution, so the conversion goes through the same helper
    # `climate_store_rule` uses. Formatting the years here would be a second
    # implementation of the key, free to drift from the one a run builds.
    _start, _end = historical_window_bounds(base["climate"]["window"])
    key = f"{base['climate']['selected']}_" + slugify_window(
        _start.isoformat(), _end.isoformat()
    )
    guard_ok = pdir / "data" / "climate" / "historical" / key / ".guard_ok"
    return cfg_path, pdir, wf1, wf2, sentinel, guard_ok


def _seed_guard(cfg_path, sentinel):
    """Execute the guard rule once for real (targets the sentinel)."""
    result = _run(f'"{sentinel.as_posix()}"', cfg_path)
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")
    assert sentinel.is_file(), "guard did not write the sentinel"


def _dry_run_output(cfg_path, sentinel):
    """--dry-run targeting the sentinel; return combined stdout+stderr."""
    result = _run(f'--dry-run "{sentinel.as_posix()}"', cfg_path)
    return (result.stdout or "") + (result.stderr or "")


@pytest.mark.slow
def test_guard_invalidation_i_to_l(staged_project):
    """Gate 2b: each comparand mutation schedules the guard; revert does not."""
    cfg_path, pdir, wf1, wf2, sentinel, guard_ok = staged_project
    _seed_guard(cfg_path, sentinel)

    # Guard artifact (second output, shared class) also written under the keyed
    # store dir (commit 4).
    assert guard_ok.is_file(), "guard did not write the key-level guard artifact"

    # Control: nothing changed -> "Nothing to be done".
    out = _dry_run_output(cfg_path, sentinel)
    assert "Nothing to be done" in out, out

    base_cfg_text = cfg_path.read_text(encoding="utf-8")

    # (i) mutate a guarded live-config section -> "Params have changed"
    #     (guarded-sections digest param flips).
    live = yaml.safe_load(base_cfg_text)
    live["basin"]["resolution"] = 0.05
    cfg_path.write_text(yaml.safe_dump(live), encoding="utf-8")
    out = _dry_run_output(cfg_path, sentinel)
    assert "Params have changed" in out, out

    # restore the live config; back to no-op before the next mutation
    cfg_path.write_text(base_cfg_text, encoding="utf-8")
    out = _dry_run_output(cfg_path, sentinel)
    assert "Nothing to be done" in out, out

    # (j) mutate the wf1 snapshot content -> scheduled (wf1 digest param).
    orig_wf1 = wf1.read_text(encoding="utf-8")
    wf1_doc = yaml.safe_load(orig_wf1)
    wf1_doc["basin"]["resolution"] = 0.05
    wf1.write_text(yaml.safe_dump(wf1_doc), encoding="utf-8")
    out = _dry_run_output(cfg_path, sentinel)
    assert "Params have changed" in out, out
    wf1.write_text(orig_wf1, encoding="utf-8")

    # (k) mutate the wf2 snapshot content -> scheduled (wf2 digest param).
    orig_wf2 = wf2.read_text(encoding="utf-8")
    wf2_doc = yaml.safe_load(orig_wf2)
    wf2_doc["workflows"]["analyze_projections"]["scenarios"] = ["ssp126"]
    wf2.write_text(yaml.safe_dump(wf2_doc), encoding="utf-8")
    out = _dry_run_output(cfg_path, sentinel)
    assert "Params have changed" in out, out
    wf2.write_text(orig_wf2, encoding="utf-8")

    # (l) every comparand reverted to original bytes -> "Nothing to be done"
    #     (content-addressed, mtime-immune; no false-fire).
    out = _dry_run_output(cfg_path, sentinel)
    assert "Nothing to be done" in out, out


def _unpack5(staged_project):
    # 2c ignores the guard_ok path.
    cfg_path, pdir, wf1, wf2, sentinel, _guard_ok = staged_project
    return cfg_path, pdir, wf1, wf2, sentinel


@pytest.mark.slow
def test_2c_fresh_project_missing_wf1_snapshot(staged_project):
    """Gate 2c: a fresh project (no wf1 snapshot) parses, dry-runs, unlocks."""
    cfg_path, pdir, wf1, wf2, sentinel = _unpack5(staged_project)
    wf1.unlink()
    wf2.unlink()

    # (i) --dry-run parses and builds the DAG — file_digest_or_absent returns
    #     "ABSENT", no parse-time traceback — and reports the guard's missing
    #     ancient() input via the rule-level MissingInputException naming the
    #     snapshot.
    result = _run(f'--dry-run "{sentinel.as_posix()}"', cfg_path)
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode != 0, combined
    assert "MissingInputException" in combined, combined
    assert "project_config_build_model.yml" in combined, combined
    assert "Traceback" not in combined, combined

    # (ii) --unlock with the snapshot absent. DEVIATION from design gate
    # 2c(ii), documented in dev/milestones/p31/phase-a-report.md: on the pinned Snakemake
    # 9.6.2, Workflow.unlock() calls _build_dag() before cleanup_locks()
    # (workflow.py:917), so --unlock fails on ANY missing leaf input — the
    # guard's wf1 snapshot behaves exactly like any other unbuilt leaf input
    # (pre-R07 this was demonstrated against extract_climate_grid's
    # ancient(region.geojson), which B1 retired; the guard's own snapshot is
    # now the leaf that shows it). The guard therefore does not degrade
    # --unlock beyond baseline behavior; what the digest helper buys is that the
    # failure is the clean rule-level MissingInputException, never a
    # parse-time digest traceback. Pin exactly that:
    unlock = _run("--unlock", cfg_path)
    combined = (unlock.stdout or "") + (unlock.stderr or "")
    assert unlock.returncode != 0, combined
    assert "MissingInputException" in combined, combined
    assert "Traceback" not in combined, combined

    # ...and with every leaf input present (snapshot restored), --unlock
    # SUCCEEDS — the recoverable-lock scenario (a crashed run implies the
    # snapshot existed at crash time) keeps working.
    # COMPOSED, not raw: the wf1 project snapshot records the whole config a
    # run used, and the guard compares it against the composed live config.
    # Staging the T1 file verbatim would seed a two-key stanza and the guard
    # would refuse for a difference the migration did not make.
    base = load_composed_config(cfg_path)
    wf1.write_text(yaml.safe_dump(base), encoding="utf-8")
    unlock = _run("--unlock", cfg_path)
    assert unlock.returncode == 0, (unlock.stdout or "") + (unlock.stderr or "")
    wf1.unlink()

    # (iii) with the snapshot present, a content change still flips the digest
    #       param — the absence-tolerant helper does not weaken the trigger.
    # COMPOSED, not raw: the wf1 project snapshot records the whole config a
    # run used, and the guard compares it against the composed live config.
    # Staging the T1 file verbatim would seed a two-key stanza and the guard
    # would refuse for a difference the migration did not make.
    base = load_composed_config(cfg_path)
    wf1.write_text(yaml.safe_dump(base), encoding="utf-8")
    _seed_guard(cfg_path, sentinel)
    out = _dry_run_output(cfg_path, sentinel)
    assert "Nothing to be done" in out, out
    wf1_doc = yaml.safe_load(wf1.read_text(encoding="utf-8"))
    wf1_doc["project"]["static_dir"] = "changed"
    wf1.write_text(yaml.safe_dump(wf1_doc), encoding="utf-8")
    out = _dry_run_output(cfg_path, sentinel)
    assert "Params have changed" in out, out
