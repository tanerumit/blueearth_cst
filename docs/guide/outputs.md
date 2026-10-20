---
title: "Reading the outputs"
subtitle: "Find the generated climate series, model responses, and indicators"
---

Run products live under the configured `project_dir`. For production projects,
use a directory outside the toolbox checkout.

## The layout

```text
<project_dir>/
  config/                        configuration archives and run records
    analyze_climate/              latest WF0 run_record.yml and sources/
    build_model/                  latest WF1 run_record.yml and sources/
    analyze_projections/          latest WF2 run_record.yml and sources/
    _engine/                      execution inputs, locks and invocation history
  data/spatial/                  basin geometry, locations and maps
  data/climate/                  historical forcing and projection products
  models/hydrology/wflow/         model, historical run and evaluation
  scenarios/_engine/requests/<request_id>/  scenario generation settings
  scenarios/_engine/collections/<id>/
    collection.json              collection inventory
  scenarios/_engine/current.json  current scenario export identity and file inventory
  scenarios/                     stable copies of the current collection
    scenario_run_lookup.csv      generated series and their relationships
    perturbation_lookup.csv      monthly temperature and precipitation changes
    series/<run_id>.nc            generated climate series, e.g. run_01.nc
    config/                      copied creator configuration
    weathergenr/                 copied generator settings, products and diagnostics
  scenarios/_engine/data/<id>/   immutable collection, including original tables and series
  experiments/_engine/
    allocation.json             project-wide experiment numbering
    transactions/               experiment creation and recovery records
  experiments/<name>/
    _engine/simulation.json      simulation settings used
    hydrology/wflow/output/      retained model responses
    _engine/indicator_sets/<id>/
      indicators.json              indicator definitions and source records
      return_level_benchmark.json  scope of return-level checks
      coverage_evidence.json    per-series water-year block coverage
    _engine/indicator_sets/<id>/data/   immutable tables (same files as below)
    _engine/indicator_sets/names/<set-id>/
      current.json              committed publication of this set
    results/indicator_sets/<set-id>/    readable view of one indicator set
      indicators.csv            dictionary: units, method, policies, coverage
      group_members.csv         group_id,run_id (including singleton groups)
      group_metadata.csv        group_id,st_id,is_reference
      <token>_run_indicators.csv    indicator,location,run_id,value
      <token>_group_indicators.csv  indicator,location,group_id,value
  logs/<UTC timestamp>__<workflow scope>/
    summary.md                  execution summary and links
    console.log                 chronological launcher/child transcript
    wfN.log                     detailed messages grouped by rule/member
    wfN-benchmarks.md            compact timing and resource report
    wfN-benchmarks.tsv           precise individual-job measurements
    wf4-indicators.log          indicator details for this execution
    _parts/                     execution-owned working files
```

Two experiments can use the same generated climate series, but each experiment
keeps its own model responses and indicators. To relate an indicator to the
climate change that produced it, join a run table by `run_id` to `scenario_run_lookup.csv`,
then by `st_id` to `perturbation_lookup.csv`. For a group response surface, join the group table
by `group_id` directly to `group_metadata.csv`, then by `st_id` to `perturbation_lookup.csv`.
`group_members.csv` records the contributing runs. Reference groups have `is_reference=true`
and an empty `st_id`; retain them explicitly rather than losing them in an inner coordinate join.

Configuration archives are generated records. Edit the source configuration supplied to the runner;
the archived `sources/` files preserve what an execution used. WF3 and WF4 retain their configuration
inside the owning collection or experiment. The shared `experiments/_engine/` directory is reserved
for allocation and creation recovery; it is not an experiment.

Historical source-map fields live at
`data/climate/historical/<source_window>/tables/annual_climatology.nc`.
WF0 and WF1 share the same numerical producer. Diagnostic figures and the historical display
reference consume its sealed fields, so changing rendering or display classes does not repeat
annual-field preparation. Snakemake tracks the scientific inputs and implementation separately
from display dependencies.

Separating these dependencies changes preparation identities once. Existing fields and the display
reference are regenerated at their existing paths on the first affected run; acquired climate inputs
remain reusable. Scientific methods, defaults, payload corruption checks and environment qualification
are unchanged. Older fields fail the current-identity guard until regenerated.

Fresh collections and indicator sets keep their immutable data under `_engine/`. Readers still accept
completed legacy data at `scenarios/<id>/`; their manifests retain those paths.
The stable scenario export remains at `scenarios/`. Indicator sets publish one folder each at
`experiments/<name>/results/indicator_sets/<set-id>/`; a set id never takes over a legacy
`results/indicator_sets/<id>/` root.

### Indicator terminology migration

The toolbox now uses **indicator** consistently in configuration, Python APIs, logs and outputs.
New publications use `results/indicator_sets/<set-id>/`, immutable records under
`_engine/indicator_sets/<id>/indicators.json`, and an `indicator` column in result tables.
The calculation package is `blueearth_cst.indicators`; the inspection command is
`pixi run python scripts/inspect_indicators.py`.
WF1 model-evaluation tables are now named `performance_indicators.csv` and use an `indicators` index.

Existing `_engine/metric_sets/<id>/metrics.json` publications and named exports at
`results/metric_sets/<set-id>/` remain readable. Their original hashes and table schemas are checked
before their fields are translated in memory. Saved files are never renamed or rewritten.
`inspect_indicators.py --experiment <experiment> --list` discovers both layouts.
Fresh numerical rechecking of an old publication is unavailable because it names the old execution
sources; saved integrity checks and historical receipts remain available.

Rerun WF4 with `operations: [indicators]` to calculate and publish the new layout from retained
simulation responses, without running Wflow again. Calculation identities change with the renamed
source files and contracts, so old and new publications have different identifiers. Update downstream
scripts to the new paths, `indicator` column and manifest fields such as `indicator_set_id`.
The reviewed vocabulary-only change to the native reader's docstring is accepted when reopening
retained simulations. Saved reader identities remain unchanged; other reader changes and altered
native files still fail the existing integrity checks.
Old scalar `operation: metrics-only` / `simulate-and-metrics`, the `metrics` selection key and the
`--target metrics` alias remain accepted as inputs for compatibility; maintained examples use
indicator terminology. Older flat exports are preserved and no longer refreshed.

New projects use this layout from October 2026: the former `config/runs/` contents now sit directly
under `config/`, and former `config/experiments/` state sits under `experiments/_engine/`.
Existing output trees are not migrated or supported through path aliases; use a fresh output root
with this toolbox version.

### Climate extent and basin cells

Historical climate stores retain a rectangular basin bounding box plus **one
source-grid cell on each side**. For ERA5's 0.25° grid, the margin is approximately
0.25° per side, with the exact extent determined by grid alignment.
This margin supports the current nearest-neighbour forcing reprojection; it does
not enlarge the modeled basin.

The adjacent `basin_cells.csv` lists cells whose footprints intersect the basin.
Only those cells, with equal weight, determine the weather generator's resampled
dates. Generated climate series retain the full buffered rectangle for subsequent
regridding. Existing stores and retained scenario collections are not cropped
in place; the smaller extent applies when climate inputs are regenerated.

## Check whether a run finished

Open `logs/<UTC timestamp>__<workflow scope>/summary.md`, linked by the runner's closing output.
The same execution folder holds `console.log`, `wf0.log`–`wf4.log` for invoked workflows,
and their `wfN-benchmarks.md` reports with raw `.tsv` measurements.
The summary reads the structured parent and child invocation records and lists elapsed time,
execution mode, observed outcomes, warning counts when available, and source/diagnostic links.
Standalone workflows also produce a summary. Repeated attempts retain separate execution folders.
An unfinished attempt or an older record without a measured duration stays explicitly incomplete
or unavailable. See [Run summaries and WF4 benchmarking](benchmarking.md) for interpretation.
Only WF4 records the additional process-resource timeline; the other workflows record invocation
durations without resource sampling. Successful execution does not establish scientific output completeness.

An incomplete run can leave logs and partial files.
Check `collection.json` or `indicators.json` in the corresponding `_engine/`
metadata directory before treating a collection or
indicator set as complete.

The runners record each attempt under `config/_engine/invocations/`,
including failed runs and dry runs. These records help diagnose a run; they do
not establish that its results are complete.

## Reading scenario exports

The stable `scenarios/` path mirrors every file from the selected hashed collection, including the lookup
CSVs, `series/`, `config/`, and `weathergenr/` trees. Successful WF3 generation or reuse refreshes the copies.
`scenarios/_engine/current.json` records the collection ID, revision, source marker, and exported file
checksums. WF4 continues consuming an explicitly selected immutable collection. Copied configuration and
provenance retain their original contents and references to the hashed collection.

The series copies require additional disk space. Files that already match are not recopied. Read the
export after workflow completion: updates replace individual files, not the whole set at once. Failed
generation or validation leaves the previous export intact; ordinary export I/O failures roll back
replaced files. Dry-runs do not refresh it. Only previously exported files are removed when absent from
the new collection; unrelated files remain, and untracked filename collisions are refused. Rerun WF3
to populate the stable paths in an existing project.

## Reading projection diagnostics

WF2 writes under `data/climate/projections/<ensemble>/`. Its `summary/` directory holds
the aligned annual and monthly change-factor CSVs. The separate `analysis/` directory
holds analysis-window tables, `coverage.csv`, and `availability.csv`.
The ensemble root's `_engine/analysis_record.json` describes the analysis.
Read the record for requested and used windows, exclusions, and numerical methods.

The figure suite lives in `plots/full_period/` and `plots/period_<a>_<b>/`, where `<a>-<b>`
identifies the actual analysis water years. Horizons sharing those years share a folder.
WF0–WF2 retain figure titles separately in `plots/figure_titles.md`, with matching figure keys in
`figure_titles.json` beside each caption JSON inventory. Titles are metadata for later independent
title/caption rendering controls; the default images still omit figure titles.

`plots/figure_captions.md` explains each written figure and unavailable products;
`_engine/figure_captions.json` inventories written PNGs, with paths relative to `plots/`.
Optional captioned copies
live under `plots/captioned/`. Missing eligible support produces a recorded reason, not
a placeholder PNG.

Generated plot filenames use lowercase snake_case with dataset, variable, plot context and spatial
scope fields, for example `cmip6_precip_temp_annual_change_cloud_basin_avg.png`. Internal settings,
the plot manifest and the analysis record share one `_engine/` at the ensemble root. User-facing provenance
remains with its data products in `summary/`.

The former `plots/overview/` and `plots/windows/` figure paths are retired. Existing
files at those paths are not current suite outputs and are not deleted automatically.

## Reading an indicator set

For post-processing, read CSVs from `experiments/<name>/results/indicator_sets/<set-id>/`, one folder per
selected indicator set (`default` unless the WF4 file names others). Start with `indicators.csv`: one row
per indicator with its title, variable, input and output units, quantity, method and parameters, grain and
group policy, water-year start and block assignment, partial-block, missingness and validity policies,
references, and `block_coverage`. Coverage lists every contributing run/location pair with its blocks
(observed/expected days and missing values); it discloses coverage, not sample adequacy. An authored
indicator shows its registered counterpart in `equivalent_definition`; its numbers equal that
definition's, under its own indicator key.

Every successful WF4 invocation requesting indicators refreshes each selected set's folder, including
reuse of an existing set. `_engine/indicator_sets/names/<set-id>/current.json` records the committed
publication: the immutable indicator set, the captured set definition, the dictionary metadata and every
exported file's checksum. Sets publish independently: a failed set keeps its previous folder (the run
summary names such mixed-age exports) and the command exits nonzero. Editing only titles, descriptions
or authored citations refreshes `indicators.csv` without recomputing values.

Calculation identities include the selected calculation packages, their imported dependencies and shared
execution code. Adding or editing an unrelated indicator set leaves existing selections reusable; changing
a reused formula invalidates its dependent selections. The change from the former all-set code inventory
changes existing request identities once: the first indicator run after this update recalculates selected
sets from retained responses. Saved publications remain readable, and model simulations are unaffected.

Wait for workflow completion before reading an export: replacement is atomic per file, not across the
folder. Ordinary export I/O failures roll back the replaced files. Dry-runs and `simulations_only` do not
refresh exports. A folder is refreshed only when this set's committed publication owns it; an existing
folder with unknown files, or one claimed by a legacy indicator set, is refused and left untouched. A
rerun restores managed files edited by hand; keep custom tables elsewhere.

Annual-total indicators (`aet`, `gwr`, `precip`) report **mm**: daily depths summed within each
water-year block and averaged with equal block weight. Partial first and last blocks are kept without
duration normalization and missing days contribute zero, so the value equals mean annual depth (mm/yr)
only when every block is complete and nonmissing; `block_coverage` shows whether it is.

Read `experiments/<name>/_engine/indicator_sets/<id>/indicators.json` before
its tables. It identifies the
indicators, the model responses they came from, and the files in the set.

Run tables contain one value per simulation for run-level indicators. Group tables contain one value
per design point for those indicators and pooled return levels. Both tables are written for every selected
variable; a scope without applicable indicators has a header-only table. Group membership remains explicit
even for one-member groups and selections without return levels.

Each run-level group summary is an equal-weight mean of the realization-level values, including annual
mean, extrema, quantiles, seven-day extrema, baseflow index, basin reductions and wet/dry-month means.
Unequal record lengths do not change realization weights. A NaN member propagates to the group summary;
infinite values are refused. Existing per-run reduction rules remain in force. Wet- and dry-month indicators
use the same month selected from the unperturbed reference and first native discharge location.
Their new group means can differ from the former pooled-month carrier when records or missingness differ.

Return levels retain pooled estimation from member-local annual blocks, with the existing sample screening
and estimator validity rules. A singleton group uses those same rules, not a substitute run statistic.
The set records the members and reference location. Values are stored to four significant digits;
retain the underlying model responses for more detailed analysis.

### Opening an indicator table in Excel

Run IDs such as `run_01` and group IDs such as `group_01` are prefixed strings, so ordinary CSV opening
preserves them as text. Their suffix padding is consistent within the owning namespace. Groups are
numbered independently of run count and selected indicators. Matching labels in different collections or
indicator sets do not establish matching inputs or membership.

When reading in pandas, preserve identifiers explicitly with `dtype=str` on lookup tables and
`keep_default_na=False` to retain the empty reference `st_id`. Indicator `value` columns remain numeric.
Perturbation `st_id` values still require text-preserving import in Excel and code.

### Migrating existing outputs

The prefixed collection and split indicator contracts use new schema revisions. Numeric-ID collections
and mixed `<token>_indicators.csv` / `indicator_run_lookup.csv` products are not silently reinterpreted.
Keep old output roots for provenance; regenerate scenarios, then simulate under a new experiment name
to produce the new contract. Existing files are not migrated in place. `indicators-only` is for responses
whose retained collection and simulation records already satisfy the new contract.
Automatic weather seeds include provider-code identity, so regeneration after this update may resolve
a different seed. Use the same explicit seed and matched inputs when comparing generated samples.

## Return levels and their limits

Return levels are fitted from groups of simulated years with a GEV distribution.
Read `return_level_validation` in `indicators.json` before using them. It identifies
the return periods and conditions assessed by the supplied benchmark;
`return_level_benchmark.json` holds that assessment. The benchmark covers a
limited set of synthetic cases. It does not establish accuracy for your basin,
and the results have no uncertainty intervals. Treat these return levels as
screening indicators, not design estimates.

The recorded GEV parameters use SciPy's `(c, loc, scale)` convention. The shape
parameter often written as ξ is `-c`; check this sign when comparing fits with
another tool. Each fit also reports `shape_coverage`, including how far its
estimated `c` falls outside the shapes tested in the benchmark. A fit outside
that range has not been assessed by this benchmark. Small departures are not
strong evidence on their own because shape estimates from short records are
uncertain.

Keep an indicator table together with its `indicators.json` and
`return_level_benchmark.json` when sharing or comparing return levels. The CSV
alone does not identify the estimator or its assessment.

## Are these outputs current?

Simulation checks that its requested scenario collection still matches the
current inputs. If the request is missing or out of date, the error names the
generation command to run. Simulation does not automatically choose a
collection. You can also name an existing collection explicitly in the
simulation settings file.

The `_engine/simulation.json` record ties an experiment to its collection,
model, and simulation settings. Use a new experiment name when those inputs
change. If you change only the indicators, `operation: indicators-only` creates a
new indicator set from retained model responses without rerunning simulation.

Simulation implementation identity follows the forcing preparation and Wflow
execution sources, including their scientific helpers. Python logging, figure
exports, generation implementation and configuration archive code are outside
that boundary; selected collection contents and resolved simulation inputs
remain checked separately. Snakemake continues to schedule jobs.

Completed simulations accept the audited source transition from `040a8e61`
without rewriting their identity or provenance. Both source inventories are
pinned: an unknown historical implementation still requires a new experiment.
Incomplete experiments retain their strict freeze checks. Changed scientific
code, model inputs, settings, preparation, response requirements or relevant
environment also require a new experiment. The Julia progress helper remains
tracked because it invokes Wflow.

For a reproducible comparison, keep the whole project output directory, not
only the indicator CSVs. The model build settings used by HydroMT are recorded
in `models/hydrology/wflow/hydromt_build_config.yml`.

See [Running the workflows](running.md) to calculate different indicators
from retained responses.
