---
title: WF0 starter suite implementation brief
lifecycle: temporary
created: 2026-10-03
updated: 2026-10-03
---

# Master Brief — Implement the WF0 starter suite in the lab

### Goal

Implement the six core components in [the starter proposal](wf0-starter-suite-proposal.md) inside the independent sibling project prepared by [the setup brief](wf0-lab-setup-instructions.md). Deliver reusable calculations, static figures, and a simple runnable example. Toolbox integration is a future assignment.

Execute from `C:/Users/taner/workspace/wf0-lab` after reading its `AGENTS.md`, the local proposal, and this brief. The 17-year BlueEarth development sample does not limit production analytical scope. SPI and robust trends are core deliverables, subject to eligibility checks on actual data.

Recommended executor: GPT-6.1 Sol at high effort for the suite. Consider xhigh for SPI method/edge-case work and trend uncertainty when high leaves unresolved reasoning or validation problems. Luna at high is suitable for bounded plotting or documentation edits after numerical behavior is fixed. These are judgment-based starting points, not measured guarantees; [OpenAI's guidance](https://developers.openai.com/api/docs/guides/model-selection) recommends choosing by task and evaluating the lightest adequate setting.

### Subsystem map

All targets below are proposed lab paths. Reconcile against the actual tree at start. One executor owns a selected phase; no parallel agents or orchestration are required.

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P1 | Current executor | Existing extracts or synthetic examples | Explicit input normalization, coverage policy, data-fitness and source comparison |
| P2 | Current executor | P1 daily series and eligibility flags | Seasonality and rainfall timing |
| P3 | Current executor | P1 daily series and reference-period controls | Anomalies, SPI-3/6/12, drought events |
| P4 | Current executor | P1 daily series | Standard rainfall extremes |
| P5 | Current executor | P1 daily series and P4 wet-day conventions | Sequencing and persistence |
| P6 | Current executor | P1 aggregation and P2 seasonal definitions | Sen slopes and qualified uncertainty |
| P7 | Current executor | P1–P6 results and renderers | Lab runner, examples, integration notes, optional compound panel |

### Sequencing

Follow P1 → P2 → P3 → P4 → P5 → P6 → P7 for straightforward serial delivery. P1 blocks all later phases because units, dates, missingness and spatial support must be agreed first. P2 supplies P6 seasonal definitions. P4 fixes wet-day conventions reused by P5. P7 needs all six result families. Other ordering edges are convenience, not technical dependencies.

A user may dispatch just one phase. Otherwise execute the selected suite through completion, updating the phase index in the lab copy after each meaningful result. Missing real data blocks real-data qualification, not synthetic development of unrelated components.

### Shared constraints

**Permitted:** lab source, targeted tests, examples and local documentation. Phase-owned paths are listed below. Every phase may update its own status row and write ignored generated outputs. P1 owns shared input/metadata helpers; request a small explicit amendment to that contract when another phase needs one, documenting it in the lab brief. Avoid simultaneous writers.

**Approval-gated:** changes to BlueEarth, upstream inputs, weighting conventions, public distribution, remote creation/pushing, or downloading new climate datasets. These are not part of this assignment.

**Excluded:** hydrological simulation, observation-validation/Budyko implementation, CMIP-driven generation, SPEI, wavelets, long memory, EOF/PCA, fitted return periods, and copulas. The optional P–T panel is descriptive only.

Use these implementation defaults, making assumptions visible in results:

- Accept explicitly named NetCDF files and variable mappings. Inputs are read-only. Load data and normalize metadata in one place; no toolbox imports, Snakemake objects, inherited run manifests, or discovery of arbitrary project folders.
- Normalize daily precipitation to amounts in mm and daily mean temperature to degrees Celsius, using explicit units and interval information. Missing units, ambiguous accumulation intervals, or unsupported calendars are reported rather than guessed. Inspect actual schemas first.
- Start with Gregorian/proleptic Gregorian daily records. Reject unsupported calendars explicitly until implemented; do not silently drop or manufacture dates. Reindex expected dates to expose gaps, and reject duplicates.
- For gridded extracts use an explicit cell selection, initially an existing basin-cell CSV, or accept a preaggregated basin series with declared support. Never average the buffered bounding box by default. Match cell coordinates with documented tolerance and fail on unmatched selections. Equal weights for selected intersecting cells preserve the toolbox convention; geometry processing and fractional weights can wait.
- Keep a fixed spatial support. Do not silently change the basin mean's membership as cells go missing. Report contributing-cell availability separately.
- Use common valid periods/support for source differences, and each source's explicitly labelled longer record for standalone characterization. No source accuracy ranking without independent observations.
- Fix reference periods and reporting seasons/water years through explicit function arguments or a small configuration. Prefer 1991–2020 when available; never silently substitute another period or refit SPI on each displayed window.
- Use strict complete daily periods for precipitation totals and extremes initially. Invalidate affected periods/windows when gaps occur; never replace missing rain with zero or impute silently. Temperature means also need an explicit completeness rule. Count eligibility per calendar month and accumulation scale for SPI.
- Separate calculations from rendering. Return xarray objects or tidy tables carrying units, source, reference/analysis period, spatial support, definition, sample count, and valid/unavailable status with reasons. Preserve numeric results so plotting can be repeated independently.
- Plain functions and small modules are sufficient. Do not build a plugin registry, generic framework, dashboard, task board, or custom uncertainty engine.
- Use existing xclim/SciPy capabilities where definitions match; consult installed-version APIs and primary documentation before relying on defaults. Synthetic examples must be clearly labelled and never represented as observed climate.
- Keep the lab's lightweight local Git policy. One verified milestone checkpoint per phase is sufficient; no branch switching, PRs, automatic pushes or toolbox gates.

### Human gates

None for routine lab implementation. Pause the affected component if unresolved units/calendar/source lineage make calculation ambiguous, scientific uncertainty cannot be justified, required external access is unavailable, or the work would cross the allowed scope. Continue independent authorized work. Report a precise missing input or methodological decision, not a generic request to proceed. Toolbox integration needs a future explicit assignment.

### Cross-cutting validation

During iteration, run the current phase's narrow check and visually inspect its changed figures. Add only checks that catch a plausible numerical error; do not test implementation details or PNG bytes. Cosmetic edits require rendering rather than rerunning numerical analyses.

Each phase below names a proposed test file to create. Commands are acceptance targets, not claims that those files exist. Once per completed six-component suite, P7 runs the lab tests together and its end-to-end synthetic demo. Repeat this combined check only after a shared-input change or an integration defect. No BlueEarth full suite, baseline run, hydrological model, DAG check or CI setup is required.

Scientific maturity also needs a representative real-data run. The input path is currently unknown: request `<HISTORICAL_NETCDF_PATH>` and `<BASIN_CELL_CSV_PATH_OR_DECLARED_BASIN_SERIES>` only when needed. Keep the full temporal record while reducing spatial extent. If only development data are available, report long-record SPI/trend qualification as outstanding.

### Phase brief index

This index records implementation status, not brief-authoring status. Update only the lab copy during execution; keep the toolbox bundle read-only.

| Phase brief | State | Last durable marker | Blocked on | Next action |
|---|---|---|---|---|
| [P1](#p1) | not started | — | Lab setup | Inspect an input schema and establish daily-series contract |
| [P2](#p2) | not started | — | — | Implement after P1 |
| [P3](#p3) | not started | — | — | Implement after P1; establish calibration eligibility |
| [P4](#p4) | not started | — | — | Implement standard wet-day and extreme definitions |
| [P5](#p5) | not started | — | — | Reuse P4 wet-day conventions |
| [P6](#p6) | not started | — | — | Qualify a dependence-aware uncertainty method |
| [P7](#p7) | not started | — | — | Assemble the six completed components |

<a id="p1"></a>

## Task Brief — P1 Data fitness

### Context

Lab AGENTS.md and the shared constraints above govern this phase. Available inputs may be gridded extracts or explicitly declared basin series.

### Goal

Establish trustworthy normalized daily inputs and show usable coverage and source disagreement.

### Non-goals

Downloading data, spatial regridding, fractional weighting, ranking source accuracy.

### Allowed scope

Own `wf0_lab/io.py`, `wf0_lab/fitness.py`, `wf0_lab/plotting/__init__.py`, `wf0_lab/plotting/fitness.py`, `tests/test_fitness.py`, and `examples/fitness.py`. Shared metadata/completeness helpers belong here. Keep package initializers minimal.

### Required changes (checklist)

- [ ] Normalize dates/units and selected spatial support; preserve variable-level source lineage.
- [ ] Implement explicit calendar completeness and common-period comparison.
- [ ] Return coverage and valid-count tables; plot coverage and precipitation summary differences.
- [ ] Demonstrate no-overlap and missing-variable cases with useful unavailable reasons.

### Validation

Run `pixi run python -m pytest tests/test_fitness.py -q` when calculations change; render `pixi run python examples/fitness.py` when the figure changes. A hand-calculated two-cell case with an extreme out-of-basin cell must exclude that cell; a missing date must invalidate a strict total. These catch bounding-box averaging and missing-as-zero errors. A shifted comparison period must not be compared as if paired.

### Acceptance criteria

Results identify period/support, reject ambiguous inputs, and visibly report missingness. Coverage and comparison figures agree with the returned table.

### Output requirements

Return the data contract, chosen units/calendar rules, example artifacts and actual check outcomes.

### Task constraints

Other phases consume this contract. Document any necessary later amendment here instead of duplicating normalization.

<a id="p2"></a>

## Task Brief — P2 Seasonality and rainfall timing

### Context

Use the lab rules and P1's valid daily basin series.

### Goal

Explain climate seasonality through amount, occurrence, intensity and timing.

### Non-goals

Regional monsoon onset inference or PET estimation.

### Allowed scope

Own `wf0_lab/seasonality.py`, `wf0_lab/plotting/seasonality.py`, `tests/test_seasonality.py`, and `examples/seasonality.py`.

### Required changes (checklist)

- [ ] Calculate monthly precipitation/temperature climatology and interannual percentiles.
- [ ] Separate wet-day frequency and intensity using the stated 1 mm/day convention.
- [ ] Calculate first dates reaching 25/50/75% of each valid reporting year's rainfall.
- [ ] Render curves/ribbons and timing summaries; explicitly distinguish variability from confidence intervals.

### Validation

Run `pixi run python -m pytest tests/test_seasonality.py -q` for numerical changes and `pixi run python examples/seasonality.py` for renders. Check a prescribed pulse sequence's rainfall-fraction dates and a zero-rain year; shifting the water-year anchor must change grouping as specified. No timing date is valid for zero total rainfall.

### Acceptance criteria

Figures agree with hand-computable examples, incomplete periods are excluded visibly, and no plot labels timing as onset.

### Output requirements

Return seasonal definitions, example PNGs, sample counts and actual checks.

### Task constraints

Temperature is optional. Do not mistake daily mean temperature for daily maximum or minimum temperature.

<a id="p3"></a>

## Task Brief — P3 Anomalies and SPI

### Context

Use the lab rules and P1 inputs. SPI is core functionality; the development record's length does not set the scientific scope.

### Goal

Deliver anomalies, SPI-3/6/12 and clearly defined drought-event summaries.

### Non-goals

SPEI, hydrological drought, automatic bias correction, or fitting unsupported records silently.

### Allowed scope

Own `wf0_lab/drought.py`, `wf0_lab/plotting/drought.py`, `tests/test_drought.py`, `examples/drought.py`, and `docs/drought-method.md`.

### Required changes (checklist)

- [ ] Record the chosen xclim implementation/version, distribution, fitting method, calendar-month grouping, zero handling, reference period, and accumulation alignment in the method note before coding their adapter.
- [ ] Start with a 30+ year calibration eligibility target, assessed after missing-data/window losses; check degenerate or failed fits. Do not equate meeting this target with a validated fit.
- [ ] Compute monthly anomalies and SPI-3/6/12; retain fit parameters/metadata for consistent later display windows.
- [ ] Define drought events explicitly before summaries. A suitable starting convention is a continuous negative-SPI run reaching SPI <= -1, ending at return to nonnegative SPI, with severity as the sum of negative SPI magnitudes over the run. Mark censored events and break unknown continuity at gaps.
- [ ] Plot anomaly calendars, SPI scale heatmaps and event duration/severity; show unavailable reasons for unsuitable fits.

### Validation

Run `pixi run python -m pytest tests/test_drought.py -q` when calculations change and `pixi run python examples/drought.py` for renders. Use hand-checked rolling totals and supplied SPI sequences for events; verify gap/short-record refusal. Compare one qualified result with a documented reference or independent calculation. Calling the same adapter twice is not independent verification. Render a seeded long synthetic record and, when available, a long real record.

### Acceptance criteria

Calibration and evaluation windows are distinct; leading incomplete windows and failed fits do not become valid drought values; events carry definitions and censoring flags. Any missing real-record qualification is explicit.

### Output requirements

Return method note, numeric outputs, figures, evidence and unresolved limitations.

### Task constraints

Long synthetic examples exercise behavior but do not establish realism. Ask for a decision only if evidence leaves a material methodological ambiguity.

<a id="p4"></a>

## Task Brief — P4 Rainfall extremes

### Context

Use P1's daily precipitation and standard Climdex definitions.

### Goal

Calculate Rx1day, Rx5day, SDII and wet-day frequency at declared reporting scales.

### Non-goals

Return-period fitting, percentile-threshold extremes, or Tmax/Tmin indices.

### Allowed scope

Own `wf0_lab/extremes.py`, `wf0_lab/plotting/extremes.py`, `tests/test_extremes.py`, and `examples/extremes.py`.

### Required changes (checklist)

- [ ] Reuse vetted implementations where compatible; document rolling-window boundaries and 1 mm/day threshold.
- [ ] Return index values, units, periods and eligibility flags.
- [ ] Render annual small multiples and common-period source comparisons.
- [ ] Make wet-day classification reusable by P5.

### Validation

Run `pixi run python -m pytest tests/test_extremes.py -q` for numeric changes and `pixi run python examples/extremes.py` for renders. Verify a known five-day storm crossing a year boundary, an exactly-1-mm day, a dry year and a gap. State expected values before computing; an off-by-one window or treating a gap as zero must fail.

### Acceptance criteria

Index definitions and period boundaries are visible; no-wet-day SDII is handled explicitly; basin-mean rainfall extremes are labelled as such.

### Output requirements

Return definitions, hand-calculated expectations, figures and actual check results.

### Task constraints

Do not silently interchange an index of basin-average rainfall and an average of cell-level indices.

<a id="p5"></a>

## Task Brief — P5 Sequencing and persistence

### Context

Use P1 inputs and P4 wet-day classification.

### Goal

Characterize rainfall spells and monthly anomaly persistence.

### Non-goals

Fitted Markov weather generators, causal claims, Hurst exponents or long-memory inference.

### Allowed scope

Own `wf0_lab/sequencing.py`, `wf0_lab/plotting/sequencing.py`, `tests/test_sequencing.py`, and `examples/sequencing.py`.

### Required changes (checklist)

- [ ] Compute wet/dry spell lengths, seasonal transition probabilities and longest dry spells.
- [ ] Declare how season/year boundaries assign spells; flag edge/gap censoring and count eligible transitions.
- [ ] Plot empirical exceedance curves using a documented treatment of censored spells; do not treat truncated runs as completed spells.
- [ ] Compute monthly anomaly ACF after seasonal-cycle removal, with valid-pair counts for each lag.

### Validation

Run `pixi run python -m pytest tests/test_sequencing.py -q` for numeric changes and `pixi run python examples/sequencing.py` for renders. Use a known wet/dry sequence crossing boundaries and a gap; no transition may bridge missing days. A purely deterministic seasonal cycle must not create interpreted residual persistence; zero-variance anomalies should give unavailable ACF.

### Acceptance criteria

Spells and transitions match manual counts, censoring is explicit and ACF is descriptive with valid counts.

### Output requirements

Return conventions, example plots, returned tables and checks.

### Task constraints

Never multiply evidence by treating overlapping windows or adjacent months as independent samples.

<a id="p6"></a>

## Task Brief — P6 Trends and uncertainty

### Context

Use the lab rules and P1/P2 aggregation. Descriptive slopes already exist in the toolbox; the lab's added value includes robust estimates and defensible uncertainty.

### Goal

Deliver Sen slopes, dependence-aware uncertainty and start/end-period sensitivity for annual/seasonal series.

### Non-goals

Attribution, automatic extrapolation, field-significance mapping or independent-error confidence intervals presented as dependence-aware.

### Allowed scope

Own `wf0_lab/trends.py`, `wf0_lab/plotting/trends.py`, `tests/test_trends.py`, `examples/trends.py`, and `docs/trend-method.md`.

### Required changes (checklist)

- [ ] Calculate Sen slopes using actual observation years and report per-decade units.
- [ ] Select and document a dependence-aware uncertainty procedure from primary references before implementing it. Residual moving-block resampling around a fitted trend is a candidate, subject to residual stationarity and block-length checks; do not resample raw trending values as though stationary.
- [ ] Record resampling seed, block choices, fit assumptions and minimum evidence requirements. Suppress unsupported intervals with a reason.
- [ ] Calculate sensitivity to reasonable start/end-year changes and plot slopes/intervals without significance-star summaries.

### Validation

Run `pixi run python -m pytest tests/test_trends.py -q` for numeric changes and `pixi run python examples/trends.py` for renders. Verify a known slope with irregular year spacing and an outlier. Once at method selection, use a small seeded independent/serially correlated residual experiment plus block-length sensitivity to expose obviously miscalibrated intervals. Document its limited power; do not certify coverage from one realization or widen acceptance tolerances to pass.

### Acceptance criteria

Slope units and timing are correct; uncertainty assumptions are justified and distinguishable from independent-error defaults; period sensitivity is visible. A supported descriptive slope may be returned with an unavailable interval.

### Output requirements

Return method rationale, uncertainty experiment evidence, figures and any qualification still outstanding.

### Task constraints

Escalate only a concrete unresolved scientific choice. Increasing model effort cannot substitute for numerical evidence.

<a id="p7"></a>

## Task Brief — P7 Assemble the runnable suite

### Context

All six diagnostic components should now expose callable calculations and renderers.

### Goal

Provide a simple lab execution path and a clear handoff for eventual toolbox integration.

### Non-goals

Adding Snakemake rules, changing BlueEarth, publishing a package, or a general-purpose application framework.

### Allowed scope

Own `wf0_lab/run.py`, optional `wf0_lab/compound.py` and `wf0_lab/plotting/compound.py`, `examples/starter-suite.example.yml`, `tests/test_run.py`, `README.md`, and `docs/integration-notes.md`. Coordinate any necessary dependency changes explicitly; do not reconfigure the environment speculatively.

### Required changes (checklist)

- [ ] Create the proposed runner interface `pixi run python -m wf0_lab.run --config <CONFIG_PATH>` and a `--demo` mode with seeded synthetic data. These commands are to be implemented, not existing interfaces.
- [ ] Allow selection of diagnostics; save numeric results and PNGs under the lab output directory. Summarize unavailable diagnostics and reasons.
- [ ] If requested or inexpensive with the settled series, add a seasonal P–T anomaly scatterplot. Preserve variable source identities and avoid joint-return-period claims.
- [ ] Document actual real-input usage and the mature functions/results that could later move into BlueEarth; separate remaining scientific limitations from integration work.

### Validation

Run `pixi run python -m pytest tests/test_run.py -q` for runner changes. Once at suite completion, run `pixi run python -m pytest tests -q` and `pixi run python -m wf0_lab.run --demo`. Inspect all six figure families. Verify a precipitation-only configuration yields valid precipitation diagnostics and explicit unavailable temperature products. Reuse P1's isolation checks and record toolbox status; broad toolbox testing is out of scope.

### Acceptance criteria

A new lab session can reproduce the synthetic suite; methods, source/period/support, eligibility and result locations are explicit. Real-data qualification status is honest. The suite runs without toolbox code or workflow infrastructure.

### Output requirements

Return commands/results, representative figure paths, phase completion markers, remaining limitations and integration notes. State whether each component is prototype-tested, real-data exercised, or scientifically qualified; do not collapse these claims into one status.

### Task constraints

Update the phase index. A completed lab suite does not authorize integration, publishing or pushing.

## Launch prompt

After setup, open a session rooted at the lab and paste:

> Implement the starter suite using C:/Users/taner/workspace/wf0-lab/docs/starter-suite-brief.md. Read AGENTS.md first. Work through its bounded phases using targeted numerical checks and visual inspection, with milestone commits on the lab's local branch. Keep BlueEarth and original input files read-only. Start with P1; continue through the suite unless a concrete blocker requires my input. Use the lab brief's phase index for resumption and report qualification gaps honestly.
