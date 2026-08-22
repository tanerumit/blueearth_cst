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
updated: 2026-08-22
---

> [!note] Overview
> **What** — Reshape the project config WITHIN R13's tier split: retire the shared: heading in favour of kind-named sections (basin, climate, model, method, compute), regroup by kind, and apply one naming policy. 38 indexed changes C-01..C-38 in dev/milestones/r14/config-shape-scoping.md.
> **Why** — R13 fixed which FILE a key lives in and left which SECTION, and what a key is called, decided by history. shared: names a relationship rather than a kind; one concept has several spellings; and the experiment guard's key list is hand-maintained because no boundary separates changes-the-numbers from changes-only-the-wall-clock.
> **Effort** — large

## Progress

Walkthrough of the proposed shape, key by key, with the owner. Every decision is
recorded in `dev/milestones/r14/config-shape-scoping.md` and committed
separately, so `git log` is the decision log.

- [x] Scoping document with an indexed change register: `C-01`..`C-66`,
      `S1`..`S7`, `N1`..`N7`, `Q-A`..`Q-I`
- [x] Project file walked: `project`, `basin`, `climate`, `model`, `workflows`.
      `method:` and T1 `compute:` both dissolved (`C-52`, `C-55`)
- [x] `_build_model.yml` walked (`C-56`; `simulation_window` keeps its name)
- [x] `_analyze_projections.yml` walked (`C-57`..`C-66`; `relative_change:`
      dissolved)
- [ ] **RESUME HERE: `_run_stress_test.yml`** - `experiment_name`,
      `realizations_count`, `horizon_year`, `run_length`, `run_historical`, the
      `stress_test` grid, `compute:`, `reporting.surfaces`, and the `seed`
      arriving from `C-51`
- [ ] Re-measure the parameter inventory against the code. TWO errata so far
      from `parameter-placement.md`'s 2026-08-12 appendix (`save_grids` does not
      exist; `DEFAULT_MIN_REFERENCE` / `DEFAULT_MAX_FLAGGED_MONTHS` misclassified)
- [ ] Owner rulings on the open questions: `Q-A`, `Q-C`, `Q-E`, `Q-F`, `Q-G`
      (narrowed to `reporting:`), `Q-H`, `Q-I`. `Q-B` and `Q-D` are resolved
- [ ] Probe `Q-F`: can `_WF1_GUARDED` be derived from section membership?
- [ ] Probe D3: is every register row expressible as a pure path rewrite (`C-38`)?
- [ ] Land `C-35` independently - non-breaking under every outcome
- [ ] Point `dev/working/parameter-placement.md` at this document (outside this
      lane's declared scope; needs its own task)
- [ ] Intake + design on the R13 pattern, then the review loop

**Coupled rows to watch:** `C-64` folds `min_denominator` into the `C-57`
registry, and `C-57` is still PROPOSED - decline it and `min_denominator` has no
home. `C-49` and `C-57`/`C-58` should land together or the repo grows two
conventions for one variable registry.
