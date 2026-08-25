---
title: R14 config shape - naming, nesting and section policy
type: todo-item
status: active
branch: feat/r14-config-shape
effort: 2
area: config / schema
origin: R14
queue: 1
created: 2026-08-22
updated: 2026-08-24
---

> [!note] Overview
> **What** — Reshape the project config WITHIN R13's tier split: retire the shared: heading in favour of kind-named sections (basin, climate, model, compute), regroup by kind, and apply one naming policy. 85 indexed changes C-01..C-85 in dev/milestones/r14/config-shape-scoping.md. C-85 bundles in the snake_config_ -> project_config_ file rename (t2608191733a).
> **Why** — R13 fixed which FILE a key lives in and left which SECTION, and what a key is called, decided by history. shared: names a relationship rather than a kind; one concept has several spellings; and the experiment guard's key list is hand-maintained because no boundary separates changes-the-numbers from changes-only-the-wall-clock.
> **Effort** — large

## Progress

Walkthrough of the proposed shape, key by key, with the owner. Every decision is
recorded in `dev/milestones/r14/config-shape-scoping.md` and committed
separately, so `git log` is the decision log.

- [x] Scoping document with an indexed change register: `C-01`..`C-85`,
      `S1`..`S7`, `N1`..`N8`, `Q-A`..`Q-I` (all nine questions now CLOSED)
- [x] Project file walked: `project`, `basin`, `climate`, `model`, `workflows`.
      `method:` and T1 `compute:` both dissolved (`C-52`, `C-55`)
- [x] `_build_model.yml` walked (`C-56`; `simulation_window` keeps its name,
      and takes years under `C-71`)
- [x] `_analyze_projections.yml` walked (`C-57`..`C-66`; `relative_change:`
      dissolved; windows stay CALENDAR, `C-74`)
- [x] `_run_stress_test.yml` walked (`C-67`..`C-69`, `C-77`, `C-81`, `C-82`).
      The window is declared (`C-67`), `run_historical` goes (`C-69`),
      `stress_test:` becomes `climate_perturbations:` (`C-68`), `reporting:`
      leaves the config entirely (`C-77`, `C-78`), and the generator enters by
      PATH rather than by promoted keys (`C-81`). `N8` is the new rule the pass
      produced: a window is declared in inclusive integer YEARS
- [x] Re-measure the parameter inventory against the code - DONE 2026-08-24.
      All 85 rows tested against 104 config-file keys (templates + every
      test_case set, commented-out keys included) plus the 37 `get_config`
      keys. ONE substantive defect: **`C-82` WITHDRAWN** - `parallel` and
      `n_cores` live in `config/defaults/weathergen_config.yml`, which
      Constraint 1 puts out of reach, and `C-81` already makes them reachable
      per basin. Two lesser: `disk_headroom_gb` has no template surface, and
      `C-52` retires a section this document drafted. `C-45`'s precedent
      verified live. The earlier errata (`save_grids`;
      `DEFAULT_MIN_REFERENCE` / `DEFAULT_MAX_FLAGGED_MONTHS`) stand as found
- [ ] Make `C-37` assert its ground truth is non-empty before it reports. The
      first run of the re-measure above was itself broken - its extraction
      returned zero keys and it then reported MORE flags while knowing LESS,
      with nothing in the output saying so. `C-37` is the same shape of check
      and would fail open the same way
- [x] Owner rulings on ALL NINE open questions - the register has none left.
      `Q-B`/`Q-D` 2026-08-22; `Q-C`/`Q-G` with the WF3 cluster; `Q-A`, `Q-E`,
      `Q-F`, `Q-H`, `Q-I` in the walkthrough of 2026-08-24. `Q-A` keeps
      `project_dir` as N3's named exemption (`C-06` withdrawn), `Q-E` puts
      defaults in `advanced_settings` by AUTHORITY (`C-36` unblocked), `Q-H`
      rules ONE `climate.selected`, `Q-I` rules TWO variable keys
- [ ] Settle `C-85`'s scope: the `snake_config_` FILE prefix only, or also the
      identifiers carrying it (`snake_config_fixture`, fixture and variable
      names across 33 test modules). The rename itself is RULED IN as of
      2026-08-24 and rides the bundle; only its breadth is open. Implementation
      reference stays on `t2608191733a`, including the `.gitignore` trap that
      makes `git status` lie
- [ ] Rule where `C-48` lives. It was to be a `reporting:` key placed by `Q-G`,
      and `C-77` deleted the section while `Q-G` retired - so the row is the one
      loose thread the 2026-08-24 cluster created. Its S2 classification is
      untouched (which variables get drawn cannot move a number); only the
      destination is open, and no question in the table covers it
- [x] Probe `Q-F` - DONE 2026-08-24, and it re-scoped `C-04` rather than
      confirming it. The drift guard was never the mechanism: a WF1 snapshot
      does not carry WF3's sections, so `compute:` was never in it and the
      carve-out is a no-op. `C-04` becomes "the whole WF1 snapshot except the
      `workflows.*` enabled flags", which needs no maintained tuple because
      R14 empties T1 of every non-identity key. **S2's surviving payoff is the
      DIGEST carve-out (`C-79`) alone** - the guard never rested on the class
      split, which is the claim the design must now carry
- [ ] Probe D3: is every register row expressible as a pure path rewrite (`C-38`)?
- [ ] Land `C-35` independently - non-breaking under every outcome
- [ ] Point `dev/working/parameter-placement.md` at this document (outside this
      lane's declared scope; needs its own task)
- [x] Intake MATERIALIZED 2026-08-24 (`design-review-loop` stage 0):
      `dev/milestones/r14/config-shape-intake.md`, with the derived-artifact
      register, a ten-row evidence register verified against the code, and the
      gate-materialization check. Every cited gate runs today
- [ ] Resolve the baseline's provenance before criterion 5 leans on it. The
      gate is 7/7 green, but the fixture is UNTRACKED and shared by every
      branch, and `t2608220920` is still open against the indicator reference.
      Either R13's pass-2 re-record resolved it and that note is stale, or the
      green is the shared-fixture artefact
- [x] Design DRAFTED 2026-08-24: `dev/milestones/r14/config-shape-design.md`
      (725 lines, 43 decision IDs). The `design-review-loop` was WAIVED by the
      owner - authored directly, no lens panel, no external round
- [x] Implementation briefs written: `config-shape-master-brief.md` plus eight
      phase briefs P0..P7. Complexity gate classified R14 as a PROGRAM, so it
      is decomposed rather than packed into one brief
- [x] The design's two NEW decisions RULED 2026-08-24: `C-48` withdrawn
      (D-7.10, boarded as `t2608242212`) and `C-85` at full breadth (D-12.1)
- [x] ONE external review round, `gpt-5.6-sol` via headless `codex exec`,
      against v2. Verdict REVISE - 3 blocking, 3 major, **all six accepted and
      fixed in v3**. Ledger and verbatim findings:
      `dev/milestones/r14/config-shape-review-record.md`. The sharpest was
      `ext1-5`: the digest break did NOT resolve on its own, and without the
      new design section 11.6 every already-run experiment would have been
      permanently unrunnable under its own name
- [ ] **P0 FIRST, and it now blocks every other phase** (was concurrent;
      re-sequenced by `ext1-3`). The baseline fixture is untracked and shared
      between worktrees, so once any phase migrates a config and a WF3 run
      touches it, the pre-change state is unrecoverable - it was never in git.
      P0 must record the four data targets' hashes into a TRACKED file before
      any implementation commit
- [ ] Owner approves or returns design v3 (the round cap is 1; there is no
      second dispatch)

**Coupled rows to watch:** `C-64` folds `min_denominator` into the `C-57`
registry, and `C-57` is still PROPOSED - decline it and `min_denominator` has no
home. `C-49` and `C-57`/`C-58` should land together or the repo grows two
conventions for one variable registry. `C-77` and `C-79` must be presented
together, or removing `reporting:` leaves S2's class split with no instances at
all. `C-32` should land with `C-75`, which sweeps the technical note onto the
vocabulary `C-32` adopts.

**Not behaviour-preserving, and deliberately so:** `C-69` for a config that set
`run_historical: false` (it gains `st_0` and two class-C metrics), and `N8` for
a project that sets `water_year_start != Jan` (`C-38` REFUSES that window by
name rather than shifting it silently). Both are per-row exceptions to success
criterion 5, recorded rather than hidden, and together they are why `C-38`
needs a "mechanical, but tell the user what changed" hook.

**Boarded out of the 2026-08-24 walkthrough, both number-movers and both out of
R14 by construction:** `t2608241413` (the generated series is anchored to a
hardcoded 2010) and `t2608241414` (the two baseline WF3 configs have diverged).
