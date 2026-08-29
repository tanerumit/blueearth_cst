# R14 P2 — the three rung-2 falsifiers, as observed

Run 2026-08-29 against `test_case/test_rapid` at `fd5e0b83`. P2's brief asks for
each falsifier's OBSERVED behaviour rather than a passing suite, because two of
the three assert an ABSENCE and no test suite reaches them.

## Preparing the project

The tree had to be rebuilt before any falsifier meant anything, exactly as the
brief warned:

- **WF1** re-run in full (20 jobs, 4m04s). Its snapshot was the pre-migration v1
  document.
- **WF2's snapshot** regenerated through rule 2.01 alone. The first control run
  refused with a wall of v1 diffs — `shared:`, `candidate_sources`,
  `horizontime_climate` — all sourced from the stale WF2 snapshot, which the WF1
  rebuild does not touch. The guard reads only the snapshot, so rule 2.01 was
  enough and the four CMIP6 downloads were not needed.
- **WF3** run to completion (34 jobs, 16m16s) to arm the freeze for falsifier 3.

**The control is what makes the rest evidence.** With the project coherent, the
unmodified `snake_config_rapid.yml` passes the guard (`exit 0`, `Project
consistency OK`). Without that line, falsifier 1's refusal would be
indistinguishable from the stale-snapshot refusal above.

## 1. "the guard now covers `climate:`" — REFUSES, as required

```text
$ snakemake .../.project_consistency_ok --configfile test_case/p2_falsifier1.yml
exit=1
  - climate.selected: 'chirps' (experiment) vs 'era5' (snapshot)
```

The hole `D-9.1` exists to close. Before P2 this edit was accepted and WF3 ran
an experiment against a model forced with a different dataset.

One diff, not two. The section is compared against the FIRST snapshot that
witnesses it, so a T1 key present in both snapshots is not reported twice.

## 2. "toggling a workflow does not refuse" — PASSES, as required

```text
$ snakemake .../.project_consistency_ok --configfile test_case/p2_falsifier2.yml
exit=0
02:23:31 - guard - Project consistency OK.
```

`workflows.analyze_projections.enabled: false`. The one structural exception;
without it the derived rule would refuse an experiment for a change that cannot
move a number in it.

Worth recording because it was not obvious: composition is driven by
`declared_sections`, not by `enabled`, so a disabled workflow's section is still
fully composed. Had it not been, the live stanza would have been unexpanded
against an expanded snapshot and this would have refused.

## 3. "`batch_size` no longer invalidates a run" — PASSES, but VACUOUSLY

```text
$ snakemake .../config/experiment.yml --configfile test_case/p2_falsifier3b.yml
exit=0
```

**This result is worth nothing on its own, and the control is why we know.**
Changing `n_realizations` — a real identity key — was ALSO accepted after a
complete run. Nothing freezes at rule level, so "batch_size did not freeze" says
nothing about `batch_size`.

The cause is a pre-existing defect with no connection to P2: Snakemake removes
rule 3.07's declared output before the job runs, so `check_not_frozen` finds no
recorded file and returns early. Probed directly, reverted in the same session:

```text
02:49:06 - probe - PROBE prev_exists=False marker=True
```

Boarded as `t2608290250`.

Asserted instead where the freeze IS decidable, against a record staged as a
project would carry it from before `C-79` — with `compute:` in it:

```text
document carries compute: False
RESULT:  not frozen   <- C-79 holds
CONTROL: REFUSED ['n_realizations']
```

Both halves on the same staged record: the batching change passes and a real
identity change still refuses. That is the property `C-79` claims, and it is the
strongest form available until `t2608290250` is fixed.

## What the falsifiers found that the suite could not

- **The registry was the wrong lever.** `compute:` registered in
  `RETIRED_EXPERIMENT_KEYS` made WF3 refuse to PARSE — the table is read a
  second time by `refuse_retired_experiment_keys`, which rejects any config
  declaring a listed key. Every unit test passed. Fixed in `fd5e0b83`.
- **The freeze has never fired.** Above.

Both are the same shape as the fixture defect P2's first commit fixed: a
mechanism whose input is produced by the harness cannot be verified by a test
that stages that input itself.
