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

- [x] Scoping document with an indexed change register: `C-01`..`C-84`,
      `S1`..`S7`, `N1`..`N8`, `Q-A`..`Q-I`
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
- [ ] Re-measure the parameter inventory against the code. TWO errata so far
      from `parameter-placement.md`'s 2026-08-12 appendix (`save_grids` does not
      exist; `DEFAULT_MIN_REFERENCE` / `DEFAULT_MAX_FLAGGED_MONTHS` misclassified)
- [ ] Owner rulings on the REMAINING open questions: `Q-A`, `Q-E`, `Q-F`,
      `Q-H`, `Q-I`. `Q-B`, `Q-C` and `Q-D` are resolved; `Q-G` is RETIRED
      (`C-77` removed the section it asked about)
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
- [ ] Probe `Q-F`: can `_WF1_GUARDED` be derived from section membership? Now
      LOAD-BEARING rather than one probe among several — with `reporting:` gone
      (`C-77`), `compute:` is the only section outside configuration identity,
      so the whole S2 claim rests on this one probe (`C-79`)
- [ ] Probe D3: is every register row expressible as a pure path rewrite (`C-38`)?
- [ ] Land `C-35` independently - non-breaking under every outcome
- [ ] Point `dev/working/parameter-placement.md` at this document (outside this
      lane's declared scope; needs its own task)
- [ ] Intake + design on the R13 pattern, then the review loop

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
