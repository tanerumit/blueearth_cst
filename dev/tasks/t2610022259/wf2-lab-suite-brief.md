---
title: WF2 starter suite lab brief
lifecycle: temporary
created: 2026-10-06
updated: 2026-10-06
---

# Master Brief — Implement the WF2 starter suite in the lab

### Goal

Implement the coverage foundation and six components of the accepted
[WF2 starter suite proposal](wf2-starter-suite-proposal.md) as a `wf2_lab/` package inside the existing lab at
`C:/Users/taner/workspace/wf0-lab` (decision 4). Deliver reusable calculations, result tables, static figures
and a runnable example on a real development ensemble. Toolbox integration is a later, separate assignment.

The six owner decisions in the proposal are settled (2026-10-06) and bind every phase. In particular, every
component reports both the simulation-aligned window and the 30-year analysis window, except C4, which uses
the analysis window only (decision 1). The development ensemble (decision 2) is an approved download.

Recommended executor: a capable coding agent at high effort. P2 (change core) and P5 (variability and
sensitivity) benefit from the strongest available reasoning setting, because their errors are numerical and
silent. This is a judgement-based starting point, not a measured result.

### Subsystem map

Lab paths below are proposed targets; reconcile them against the actual tree at the start of each phase. One
executor owns a phase; no parallel agents or orchestration are required.

| Phase | Where | Input | Expected output |
|---|---|---|---|
| P0 | BlueEarth session | CMIP6 catalog, baseline basin | WF2 run of the development ensemble, list recorded |
| P1 | Lab | P0 `scalar/` series, `composition.csv` | `wf2_lab` setup, input contract, C0 coverage |
| P2 | Lab | P1 normalized series | Long per-member change table (shared core) |
| P3 | Lab | P2 table | C1 mean change, C5 scenario agreement |
| P4 | Lab | P1 series, P2 table | C2 seasonal conditions, C3 trajectories |
| P5 | Lab | P1 series, P2 table | C4 interannual variability, C6 model sensitivity |
| P6 | Lab | P1–P5 results and renderers | Runner, captions, integration notes, status ladder |

### Sequencing

P0 → P1 → P2, then P3 → P4 → P5, then P6.

- **P0 blocks P1:** the lab's input contract is written against the real ensemble's files, calendars and
  member structure. Synthetic development may start before P0 lands, but P1 is not done until it reads P0.
- **P1 blocks P2:** units, calendars and the (model, scenario, member) identity must be settled before any
  change is formed.
- **P2 blocks P3–P5:** every component is a reduction of P2's table. P2's acceptance reconciles it against
  the toolbox's own change-factor tables. Until that holds, a later phase's numbers prove nothing.
- **P3, P4 and P5** follow the proposal's delivery increments. They are ordered by value, not by technical
  dependency, and touch disjoint lab files. P5's sensitivity component reruns P3's reductions, so it
  reuses P3's reduction functions rather than re-implementing them.
- **P6 needs all component results.**

A user may dispatch a single phase. Otherwise execute through P6, updating the phase index in the lab copy
after each meaningful result.

### Shared constraints

**Permitted (lab phases):** new files under `wf2_lab/`, `tests/test_wf2_*.py`, `examples/wf2-*.yml`,
`docs/wf2-*.md`, and the lab `README.md`/`AGENTS.md` edits named in P1. Generated outputs go under ignored
`outputs/wf2/<case>/`.

**Approval-gated:** any change to BlueEarth source, configuration or tracked seeds; downloads beyond the P0
ensemble; changes to `wf0_lab/` that alter a WF0 render or result; adding lab dependencies; remote creation
or pushing.

**Excluded:** daily extremes, global warming levels, spatial maps, SPI, model-versus-observation comparison,
uncertainty partitioning, model weighting, time of emergence, storylines, bias adjustment and the CST
exposure-space overlay (proposal § Deferred). No dashboard or web page beyond what P6 reuses from the lab.

Implementation defaults, made visible in results:

- **Inputs are declared, never discovered.** Read the P0 project's `summary/composition.csv` and the
  `scalar/` NetCDF files it names, read-only, plus the two change-factor CSVs for reconciliation. No toolbox
  imports, Snakemake objects or path injection.
- **Identity is (model, scenario, member).** The model ID keeps its `institution/model` form; derive the
  institution from the segment before `/`. A scenario series pairs with the historical series that
  `composition.csv` names as `reference_series_key`, and with no other.
- **Calendar weights.** Series may use `noleap` or other model calendars. Weight months by their length in
  the series' own calendar for seasonal and annual means of rates; never average monthly percentages.
  Precipitation is mm/day and temperature °C, matching the toolbox. Reject other units rather than guessing.
- **Windows.** Two window kinds:
  - simulation-aligned: the P0 config's reference and horizon, 2000–2014 and 2046–2054;
  - analysis: reference 1985–2014, plus a 30-year future window centred on each horizon. With
    `c = floor((start + end) / 2)`, the window is `c − 14 … c + 15`, so 2046–2054 gives 2036–2065.
  A window that would leave the data is reported as unavailable, never shortened silently.
- **Seasons.** DJF/MAM/JJA/SON (decision 3). DJF is labelled by its January year; a DJF missing any month
  inside a window is excluded from it, and the count is reported.
- **Ensemble reduction.** Form changes per member first. Average members within a model, then summarize
  across models with equal model weight. Keep member-level spread as a separately labelled product. Always
  show individual model points; add median and IQR only for at least 10 contributing models (a lab
  heuristic). Call the summary ensemble spread, never a confidence interval.
- **Figures.** Follow the lab's accepted rules (`docs/figure-rules.md` current section; reusable decisions
  FIG-001–005), with captions off by default and kept recoverable (decision 5). Scenario is the colour
  channel, using the toolbox SSP palette from `blueearth_cst/projections/projection_plots.py`
  `SCENARIO_COLORS`, copied as values rather than imported. Run the lab's CVD check on the four SSP colours
  and record the result.
- **Figure tokens.** Reuse `wf0_lab` figure tokens by one-way import (`wf2_lab` → `wf0_lab`), never the
  reverse. If they are not importable without side effects, extract a small shared style module only when WF0
  renders stay visually unchanged; otherwise copy the tokens and record the duplication.
- **Results.** Return tidy tables carrying window kind and years, period, statistic, units, contributing
  model and member counts, and an unavailable status with its reason. Plotting reads only those tables.
- **Plain modules.** Plain functions and small modules; no plugin registry, framework or uncertainty
  engine. Lab Git policy applies: one verified milestone commit per phase on lab `main`; no pushes.

### Human gates

None for routine work; the ensemble download is approved. Pause the affected component only when:

- the P0 run cannot meet the ensemble criteria;
- reconciliation with the toolbox fails without an identified cause;
- a method choice the brief leaves open cannot be justified from evidence.

Report the precise missing input or decision, not a generic request to proceed, and continue independent
authorized work.

### Cross-cutting validation

During iteration, run only the current phase's tests and render only its changed figures. Commands below
name test files to create; they are acceptance targets, not claims that the files exist.

The program-level falsifier is P2's reconciliation. For the simulation-aligned window, the lab's per-member
`mean` changes must match `cmip6_change_factors_annual.csv` and `cmip6_change_factors_monthly.csv` from the
same P0 run. The tolerance is 0.001 in each table's printed relative units; the CSVs are rounded to three
decimals. A mismatch means the lab computes a different quantity from the toolbox, and later components
cannot be integrated as stated.

Once per completed suite, P6 runs `pixi run python -m pytest tests -q` (WF0 and WF2 together, confirming
`wf0_lab` is unaffected) and the end-to-end run on the P0 ensemble. Repeat only after a shared-input change.
No BlueEarth test suite, baseline check or DAG check is required for lab phases.

### Phase brief index

This index records implementation status. P0 updates the toolbox copy of this brief (a board commit to
BlueEarth `main`). P1 then copies the brief into the lab, and from that point the lab copy is the
resume record; the toolbox copy stays read-only.

| Phase | State | Last durable marker | Blocked on | Next action |
|---|---|---|---|---|
| [P0](#p0) | not started | — | — | Select the ensemble from the catalog; dry-run the DAG |
| [P1](#p1) | not started | — | P0 | Copy docs into the lab; read one P0 scalar file |
| [P2](#p2) | not started | — | P1 | Build the change table; reconcile against the CSVs |
| [P3](#p3) | not started | — | P2 | Reduce C1 changes; draw dot strips |
| [P4](#p4) | not started | — | P2 | Monthly climatologies; smoothed anomalies |
| [P5](#p5) | not started | — | P2, P3 | Fix the detrending method; variability ratios |
| [P6](#p6) | not started | — | P3–P5 | Assemble the runner and integration notes |

<a id="p0"></a>

## Task Brief — P0 Acquire the development ensemble

### Context

Execute from a BlueEarth session; the lab's own instructions forbid running toolbox workflows. BlueEarth's
`AGENTS.md` governs this phase. WF2 already supports everything needed without code changes:

- fixed acquisition spans of 1950–2014 (historical) and 2015–2100 (scenarios), in `series_identity.py`;
- the `members.selection: all` policy, with per-model `members.overrides` replacing the preference list.

The catalog (`config/catalogs/cmip6_data.yml`, crawled 2026-07-29) lists 67 models with 41–47 per main SSP.
Re-measure availability from the catalog itself rather than trusting these counts.

### Goal

A completed WF2 run, on the baseline basin, of an ensemble meeting the decision 2 criteria. Its `scalar/`
series, `composition.csv`, change-factor tables and `report.md` sit in a project directory outside the
repository, and the chosen list and fetch volume are recorded in this brief.

### Non-goals

Any BlueEarth code, tracked config or seed change; tuning WF2 figures for many models; running other
workflows.

### Allowed scope

- **Permitted:** untracked config files `test_case/test_wf2_ensemble.yml` and
  `test_case/test_wf2_ensemble_analyze_projections.yml`. Both are ignored by `.gitignore` line 140
  (`test_case/*`), verified 2026-10-06 with `git check-ignore -v`.
- **Permitted:** the run's output under `<WF2_ENSEMBLE_PROJECT_DIR>`, an owner-chosen directory outside
  every repository.
- **Permitted:** this brief's P0 row and the "Development ensemble" record below, committed to `main` as a
  board-only change.
- **Forbidden:** generated catalogs, tracked `test_case/` seeds, `dev/working/`.

### Required changes (checklist)

- [ ] Ask the owner for `<WF2_ENSEMBLE_PROJECT_DIR>` if it is not given.
- [ ] Select at least 12 models from at least 10 institutions, at most two per institution. Each must
      publish `r1i1p1f1` (or a single recorded alternative) for historical and all of SSP1-2.6, SSP2-4.5,
      SSP3-7.0 and SSP5-8.5.
- [ ] Select three of those models with at least five members present in historical and all four SSPs, and
      list those members in `members.overrides`. If no model meets all four SSPs, relax to SSP2-4.5 and
      SSP5-8.5 and record that.
- [ ] Copy `test_case/project_config_baseline.yml` and its `analyze_projections` file into the two
      untracked files. Set `project_dir` to `<WF2_ENSEMBLE_PROJECT_DIR>` and enable only
      `analyze_projections`. Set the models, the four scenarios and `members.selection: all`. Keep the
      reference window 2000–2014, the horizon `mid` 2046–2054 and the variables unchanged.
- [ ] Dry-run the DAG and confirm the fetch-job count equals the selected (model, experiment, member)
      combinations.
- [ ] Run WF2 detached, because long runs in a background tool task get reaped. Launch with
      `Start-Process`, redirecting output to a log file, and wait on that file.
- [ ] Record the model and member list, `composition.csv` outcome, wall-clock time, and the size of `raw/`
      and `scalar/` in the "Development ensemble" section below. Update the P0 index row and commit.

### Validation

Measure catalog availability with a short script over `config/catalogs/cmip6_data.yml`; never select by
memory.

Dry run, then run, through the WF2 entry point (both flags exist in `scripts/run_workflow.py`):

```powershell
python scripts/run_workflow.py analyze_projections --config test_case/test_wf2_ensemble.yml --project-dir <WF2_ENSEMBLE_PROJECT_DIR> --cores 3 --dry-run
python scripts/run_workflow.py analyze_projections --config test_case/test_wf2_ensemble.yml --project-dir <WF2_ENSEMBLE_PROJECT_DIR> --cores 3 --keep-going
```

Falsifiers:

- any requested combination not `resolved` in `composition.csv`, other than those recorded as unavailable;
- a scalar historical series not spanning 1950–2014, or a scenario series not spanning 2015–2100;
- `git status --short` showing a tracked change after the run.

### Acceptance criteria

The ensemble meets the criteria, or every relaxation is recorded with its reason. All selected combinations
resolve, and the outputs exist outside the repository. The record below lets P1 start without re-deriving
anything.

### Output requirements

Return the selected list, composition outcome, fetch volume and time, the commands run with their outcomes,
and any observations on how WF2's existing figures behave at this ensemble size. Do not fix those figures.

### Task constraints

Use the configuration-set layout of the copied baseline files; check the stanza schema against the files
rather than this brief. A WF2 lock after a crash is released with `snakemake --unlock`.

### Development ensemble (filled by P0)

`<NOT YET RECORDED>`

<a id="p1"></a>

## Task Brief — P1 Lab setup, input contract and C0 coverage

### Context

Lab `AGENTS.md` and the shared constraints govern this phase. The lab currently has two workstreams,
`wf0_lab/` and `cst_maps/`.

### Goal

Add `wf2_lab` as a third workstream that reads the P0 ensemble through one explicit input contract. Show
evidence coverage.

### Non-goals

Forming changes, which belongs to P2; refetching data; reading `raw/` grids.

### Allowed scope

- **Lab files owned:** `wf2_lab/__init__.py`, `wf2_lab/inputs.py`, `wf2_lab/coverage.py`,
  `tests/test_wf2_inputs.py`, `examples/wf2-input-paths.example.yml` and an ignored
  `examples/wf2-input-paths.local.yml`.
- **Docs:** copy this brief and the proposal into lab `docs/` as `wf2-suite-brief.md` and
  `wf2-starter-suite-proposal.md`, with their links localized.
- **Instructions:** edit the lab `AGENTS.md` and `README.md` to add the WF2 workstream, its output root
  `outputs/wf2/<case>/`, and the one-way `wf2_lab` → `wf0_lab` import rule.

### Required changes (checklist)

- [ ] Load `composition.csv` and the scalar files it names. Normalize to one tidy monthly table: model,
      institution, scenario, member, time, variable, value, units, calendar, plus a pointer to the series'
      historical reference.
- [ ] Check units, calendars, monotonic monthly time, spans and duplicate identities. Fail on ambiguity.
- [ ] C0: a coverage table and matrix (model × scenario, members per cell, status and reason, institution),
      plus a reusable "n models / n members" annotation for later figures.
- [ ] Demonstrate an excluded combination and a missing scenario with useful unavailable reasons, on a
      small synthetic fixture.

### Validation

Run `pixi run python -m pytest tests/test_wf2_inputs.py -q` when the calculations change. Render the
coverage matrix when it changes.

Falsifiers:

- a scenario series paired with another member's historical series;
- a `noleap` series whose day counts are taken from the Gregorian calendar;
- a duplicated identity accepted silently.

### Acceptance criteria

The P0 ensemble loads with every identity, span and calendar reported. Coverage agrees with
`composition.csv` row for row. `wf0_lab` tests still pass.

### Output requirements

Return the input contract, calendars found, coverage figure path and the checks actually run.

### Task constraints

Later phases consume this contract. Amend it here rather than re-normalizing in another module.

<a id="p2"></a>

## Task Brief — P2 Shared change core

### Context

This is the single calculator for every component. It extends the toolbox change-factor table's shape
(model, scenario, member, horizon, period, variable, statistic, reference value, future value, change,
status) with the columns `period` and `window_kind`.

### Goal

Produce the long per-member change table for both window kinds, the annual, seasonal and monthly periods,
and the statistics mean, detrended SD and precipitation CV. It must match the toolbox on the overlap.

### Non-goals

Ensemble summaries and figures.

### Allowed scope

Own `wf2_lab/core.py` and `tests/test_wf2_core.py`.

### Required changes (checklist)

- [ ] Implement window construction per the shared constraints; report unavailable windows.
- [ ] Day-weighted seasonal and annual means. Precipitation changes go in % and mm/day; temperature changes
      in °C.
- [ ] Apply the dry-reference guard. Where the reference precipitation for a period is below 0.1 mm/day (the
      toolbox's dry-month threshold; confirm in `blueearth_cst/projections/dry_month.py`), report the
      absolute change only, with a reason.
- [ ] Interannual SD of period values per window, with a declared forced-response removal. The default is
      a per-member linear detrend within each window. Report the undetrended SD beside it under a distinct
      statistic label, and the CV of detrended precipitation where the mean is above the dry threshold.
- [ ] Reconcile the aligned-window `mean` rows against the P0 CSVs.

### Validation

Run `pixi run python -m pytest tests/test_wf2_core.py -q`.

Known-answer checks:

- a hand-computed `noleap` DJF mean;
- a series with a pure linear trend, which must give a detrended SD of 0 and a positive undetrended SD;
- a window centred on 2046–2054, which must come out as 2036–2065;
- a horizon near 2100, which must be reported unavailable rather than shortened.

Reconciliation is the cross-cutting falsifier above.

### Acceptance criteria

Reconciliation passes for every resolved P0 combination, with the worst-case deviation reported. The
known-answer checks pass, and every row carries its counts and window years.

### Output requirements

Return the table schema, the reconciliation result (worst case named), the detrending choice and its
rationale, and the checks run.

### Task constraints

If reconciliation fails, stop and diagnose before any later phase uses the table.

<a id="p3"></a>

## Task Brief — P3 C1 mean change and C5 scenario agreement

### Context

These are reductions of the P2 table, using the shared ensemble-reduction rules.

### Goal

Show what mean changes are projected per scenario, horizon and season, and how far models agree.

### Non-goals

Probabilistic statements; model weighting; the AR6 Atlas robustness method.

### Allowed scope

Own `wf2_lab/means.py`, `wf2_lab/agreement.py`, `wf2_lab/figures_wf2.py` (P3 figure functions; later
phases add theirs), `tests/test_wf2_means.py` and `tests/test_wf2_agreement.py`.

### Required changes (checklist)

- [ ] C1: model-level ΔT and ΔP (% and mm/day) per scenario, horizon, period and window kind. Count, median,
      range, and IQR when at least 10 models contribute. Show dot strips with every model, faceted by
      period and coloured by scenario, with counts.
- [ ] C5: the fraction of models sharing the median's sign, with its denominator, plus a configurable
      small-change band, labelled as a heuristic. Draw a sign-agreement matrix (variable × period rows,
      scenario × horizon columns).
- [ ] C5: paired scenario contrasts on the common model set, drawn as a slope plot linking each model
      across scenarios.
- [ ] Expose the reduction functions for reuse by P5.

### Validation

Run `pixi run python -m pytest tests/test_wf2_means.py tests/test_wf2_agreement.py -q`.

Checks:

- two members of one model must count as one model;
- a model missing a scenario must be excluded from paired contrasts but kept in the per-scenario summary,
  and the counts must say so;
- with exactly half the models on each side of zero, the agreement fraction must be reported against its
  denominator rather than rounded to a sign.

Render and inspect the figures.

### Acceptance criteria

Figure values equal the returned tables, and counts are visible. No interval is labelled as confidence.

### Output requirements

Return the tables, figure paths and checks run.

### Task constraints

Do not pool members as if they were independent models.

<a id="p4"></a>

## Task Brief — P4 C2 seasonal conditions and C3 trajectories

### Context

Builds on the P1 series and P2 windows. The current toolbox already draws a monthly change-factor figure and
annual overviews; these views complement them rather than replace them.

### Goal

Show how the seasonal cycle changes, and how the projected changes develop through time.

### Non-goals

Season timing or onset, and daily statistics.

### Allowed scope

Own `wf2_lab/seasonal.py`, `wf2_lab/trajectories.py`, their figure functions in `wf2_lab/figures_wf2.py`,
`tests/test_wf2_seasonal.py` and `tests/test_wf2_trajectories.py`.

### Required changes (checklist)

- [ ] C2: reference and future monthly climatologies per model, in absolute units, for both window kinds.
      Show monthly change as the median and model range, with individual points.
- [ ] C3: annual anomalies against each model's own reference. Apply a declared running mean (20 years by
      default; label the endpoint treatment) and draw a scenario-faceted fan of the model median and range,
      with faint smoothed traces.

### Validation

Run `pixi run python -m pytest tests/test_wf2_seasonal.py tests/test_wf2_trajectories.py -q`.

Checks:

- the C2 aligned-window monthly mean change must equal P2's monthly rows;
- a constant series must have zero anomaly;
- the smoothed series must not extend past the declared endpoint rule.

Render and inspect the figures.

### Acceptance criteria

The figures agree with the tables. The smoothing length and window years appear in the captions. The fan is
not described as annual variability.

### Output requirements

Return the tables, figure paths, smoothing settings and checks run.

### Task constraints

Keep model identity out of the colour channel.

<a id="p5"></a>

## Task Brief — P5 C4 interannual variability and C6 model sensitivity

### Context

C4 uses P2's detrended statistics on the analysis window only (decision 1). C6 reruns P3's reductions on
altered memberships and windows.

### Goal

Show whether interannual variability changes, and how much the headline conclusions depend on ensemble
membership and window choice.

### Non-goals

Global warming levels, climate-sensitivity estimates, weighting and formal uncertainty partitioning.

### Allowed scope

Own `wf2_lab/variability.py`, `wf2_lab/sensitivity.py`, their figure functions in `wf2_lab/figures_wf2.py`,
`tests/test_wf2_variability.py` and `tests/test_wf2_sensitivity.py`.

### Required changes (checklist)

- [ ] C4: future/reference ratios of the detrended SD and precipitation CV, per model, scenario and period.
      Draw a ratio dot plot and paired reference/future distributions. For the three multi-member models,
      show member spread as a separate, labelled within-model product.
- [ ] C6 primary: for each headline C1 median, compute leave-one-model-out, leave-one-institution-out,
      common versus all available models, and aligned versus analysis window. Draw a sensitivity dot plot.
- [ ] C6 secondary: per-model %ΔP per °C of local ΔT across scenarios and horizons, as a scatter, labelled
      as neither a global-warming-level nor a climate-sensitivity result.

### Validation

Run `pixi run python -m pytest tests/test_wf2_variability.py tests/test_wf2_sensitivity.py -q`.

Checks:

- a series whose variance doubles must give an SD ratio of √2 after detrending;
- removing a model must change the median exactly as recomputed by hand;
- for a single-model institution, leave-one-institution-out must equal leave-one-model-out.

Render and inspect the figures.

### Acceptance criteria

C4 never draws on aligned windows. Every sensitivity variant reports its membership count. The scaling plot
carries its disclaimer.

### Output requirements

Return the tables, figure paths, the detrending choice used, the checks run, and any conclusion that changes
sign under a sensitivity variant.

### Task constraints

Report a sign flip under sensitivity as a finding, not a defect to smooth away.

<a id="p6"></a>

## Task Brief — P6 Assemble the runnable suite

### Context

Mirrors the WF0 lab's P7: one runner, one output tree and integration notes, reusing the lab's caption
mechanism.

### Goal

One command renders the whole WF2 suite on the P0 ensemble, with tables, figures, recoverable captions and
an honest status report.

### Non-goals

Toolbox integration, the HTML page redesign and new diagnostics.

### Allowed scope

Own `wf2_lab/run.py`, `wf2_lab/captions_wf2.py`, `tests/test_wf2_run.py`,
`docs/wf2-integration-notes.md`, and the WF2 sections of the lab `README.md`.

### Required changes (checklist)

- [ ] Runner: `pixi run python -m wf2_lab.run --config examples/wf2-input-paths.local.yml`. It writes
      `outputs/wf2/<case>/` with `figures/`, `results/` and a `summary.json` carrying settings, windows,
      membership, unavailable products with reasons, and the result-table list.
- [ ] Captions: a separate, recoverable caption per figure, with an opt-in captioned variant, following
      FIG-003.
- [ ] Integration notes, modelled on `docs/integration-notes.md`:
      - a component status table using the three-level ladder (prototype-tested, real-data exercised,
        scientifically qualified);
      - candidate functions for BlueEarth;
      - the mapping of new figures onto WF2's `overview/…` and `windows/<horizon>/…` grammar via
        `figure_relative_paths` (decision 6);
      - the open caption decision (decision 5);
      - the remaining scientific limitations.
- [ ] Add reusable-decision entries only for lessons that are genuinely new beyond FIG-001–005.

### Validation

Run `pixi run python -m pytest tests -q` once, which runs WF0 and WF2 together. Run the full suite on the P0
ensemble once, then inspect every figure at its final size.

Falsifier: any `wf0_lab` test failure, or any figure whose plotted values differ from its result table.

### Acceptance criteria

A fresh lab session can reproduce the suite from the README. The status table is evidence-based. Nothing
claims scientific qualification beyond what was checked.

### Output requirements

Return the run command, output tree, test result, status table and the lab checkpoint SHA.

### Task constraints

Do not start toolbox integration; it needs its own brief.

## Launch prompts

**P0 — BlueEarth session.**

> Execute phase P0 of `C:/Users/taner/workspace/blueearth_cst/dev/tasks/t2610022259/wf2-lab-suite-brief.md`
> from a BlueEarth session. Read its Shared constraints and the P0 brief first. Select the development
> ensemble from the CMIP6 catalog, run WF2 alone into the owner-chosen project directory outside the
> repository using untracked config files, record the ensemble and fetch volume in the brief, and commit
> that record to `main` as a board-only change. Make no tracked BlueEarth changes beyond the brief.

**P1–P6 — lab session.**

> Implement the WF2 starter suite in `C:/Users/taner/workspace/wf0-lab` by executing phases P1–P6 of
> `C:/Users/taner/workspace/blueearth_cst/dev/tasks/t2610022259/wf2-lab-suite-brief.md`, after P0 has
> recorded the development ensemble. Read the lab `AGENTS.md`, then the brief. P1 copies the brief into the
> lab, where the lab copy becomes the resume record. Keep BlueEarth and the P0 outputs read-only. Stop
> after P6; do not start toolbox integration.
