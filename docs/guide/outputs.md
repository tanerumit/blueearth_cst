---
title: "Reading the outputs"
subtitle: "Find products, check their status and read indicator tables"
---

Use the configured `project_dir` as your output root. Keep production roots outside the toolbox.
Edit source case configurations, not the generated configuration archives.

## The layout

```text
<project_dir>/
  data/spatial/                         basin geometry and resolved locations
  data/climate/historical/              extracted climate and diagnostics
  data/climate/projections/<ensemble>/  projection products
  models/hydrology/wflow/               model, forcing and historical evaluation
  scenarios/                           current exported climate series and lookups
  experiments/<name>/
    hydrology/wflow/output/             retained native responses
    results/indicator_sets/<set-id>/    named indicator tables and dictionary
  logs/<timestamp>__<scope>/            execution summary, transcript and diagnostics
  config/                              captured configurations and attempt records
```

For immutable records, complete file inventories and exact contracts, see
[retained handoffs](../technical-manual/retained-handoffs.md).
Keep the whole project output root for reproducible comparisons, not just the result CSVs.

## Check whether a run finished

1. Open the execution's `summary.md` named by the runner. Read failed/incomplete outcomes and warnings.
2. Follow its workflow-log links for diagnosis. A dry run or successful no-op does not prove computation ran.
3. Check the owning collection/simulation/indicator record before using retained results.
   Logs and a zero exit status do not establish scientific adequacy or output completeness.
4. Read the result dictionary and set limitations before comparing values.

Missing measurements remain unavailable, not zero. Use [benchmarking](benchmarking.md) for timings.

## Reading scenario exports

After WF3 finishes, `scenarios/` holds the selected collection's readable series and lookup tables.
WF4 uses a specific ready immutable collection, not whichever export directory appears newest.
Read exports after completion; publication replaces individual files rather than the entire folder at once.
Keep custom files outside managed result namespaces.

## Reading projection diagnostics

Look in `data/climate/projections/<ensemble>/summary/` for change-factor tables and provenance.
The `analysis/` tables describe diagnostic coverage/availability; read recorded exclusions before plotting.
Use the figure captions for each product's period, support and interpretation.
Projection spread is ensemble context, not a probability distribution over stress-test outcomes.

### Which run produced these files

Check the product's production/import record, not just the newest log folder.
A partial rerun can leave products from different invocations.
The [execution reference](../technical-manual/execution-and-provenance.md) owns attribution semantics.

## Moving WF2 results to another project

Use the [results-transfer reference](../technical-manual/results-transfer.md) for export/import commands,
integrity checks and destination differences. Imported products support reading and interpretation;
they do not reproduce the source environment or guarantee reuse by a later production run.

## Reading an indicator set

For post-processing, open the CSVs in `experiments/<name>/results/indicator_sets/<set-id>/`.
There is one folder per selected indicator set: `default` unless `project_config_simulate_system.yml`
selects others.

For example, a `default` set containing river discharge indicators looks like this:

```bash
experiments/stress_test_01/results/indicator_sets/default/
├── indicators.csv          # Indicator definitions, units and coverage
├── group_members.csv       # Runs included in each group
├── group_metadata.csv      # Climate perturbation and reference status of each group
├── q_run_indicators.csv    # Indicator values for each run and location
└── q_group_indicators.csv  # Indicator values for each group and location
```

Here, `q` means river discharge. Other selected variables have their own run and group tables.

Start with `indicators.csv`.
It has one row per indicator, describing:

- Its title, variable, input and output units, quantity, method and parameters.
- What each value represents (`grain`), how group results are calculated, the water-year start, and how days
  are assigned to blocks.
- Its partial-block, missingness and validity policies, references, and `block_coverage`.

`block_coverage` lists the blocks for every contributing run/location pair, including observed and
expected days and missing values.
This records coverage; it does not establish whether the sample is adequate.

For an indicator you name yourself, `equivalent_definition` identifies the existing calculation it uses.
The values are the same; they are reported under your indicator name.

Check `status` and `reason` in the result tables. `available` has a calculated value;
`undefined` describes an undefined calculation. In partial mode, missing parameters at retained locations
can produce `unavailable` rows with no value. If a required response variable is absent, the whole
calculation is omitted from the value tables; check its declaration and explanation in the dictionary
and `indicators.json` manifest instead.
Read these alongside the dictionary and selected [set conventions](indicators.md#choose-a-set).
Do not compare a missing value as if it were zero.
For advanced details, see [input evaluation and recovery](../technical-manual/indicator-requests.md#inputs-evaluation-and-recovery).

## Join an indicator to its climate settings

Run and group tables use different keys. Use the lookup from the collection retained by your experiment;
identical labels in another collection do not establish identical membership.
The examples below read tables only. Replace `run_root`, `experiment` and `set_id` for your results.

```python
from pathlib import Path
import pandas as pd

run_root = Path("C:/path/to/case-output")
experiment = "stress_test_01"
set_id = "default"
results = run_root / "experiments" / experiment / "results/indicator_sets" / set_id
scenarios = pd.read_csv(
    run_root / "scenarios/scenario_run_lookup.csv", dtype=str, keep_default_na=False
)
perturbations = pd.read_csv(
    run_root / "scenarios/perturbation_lookup.csv", dtype={"st_id": str}, keep_default_na=False
)
```

First confirm that the current scenario export matches the experiment's retained collection.
If it does not, use that collection's immutable lookup paths from its record instead.

1. Join a run-level table to scenario membership with `run_id`:

   ```python
   runs = pd.read_csv(results / "q_run_indicators.csv", dtype={"run_id": str, "location": str})
   run_settings = runs.merge(scenarios, on="run_id", how="left", validate="many_to_one")
   ```

2. Join a group-level table directly to group coordinates with `group_id`:

   ```python
   groups = pd.read_csv(results / "q_group_indicators.csv", dtype={"group_id": str, "location": str})
   coordinates = pd.read_csv(results / "group_metadata.csv", dtype=str, keep_default_na=False)
   group_settings = groups.merge(coordinates, on="group_id", how="left", validate="many_to_one")
   ```

For either table, `st_id` then joins to `perturbation_lookup.csv` for monthly changes.
That lookup has twelve rows per perturbed point, so this further join expands rows; it is not
a one-row-per-indicator table. The unperturbed reference has empty `st_id` and `is_reference=true`
in group metadata. Keep it explicitly: an inner perturbation join would drop it.
Use `group_members.csv` to inspect contributing runs, including singleton groups.
These joins identify table coordinates; a supported response-surface construction procedure is deferred.

### Opening an indicator table in Excel

Run IDs such as `run_01` and group IDs such as `group_01` are prefixed strings, so opening the CSV
normally keeps them as text.
When importing perturbation `st_id` values, explicitly preserve them as text in Excel and code.

When reading lookup tables in pandas, use `dtype=str` to preserve identifiers and
`keep_default_na=False` to retain the empty reference `st_id`.
Indicator `value` columns remain numeric.

Keep these identifier conventions in mind when joining tables:

- Each kind of ID uses a consistent number of digits within its collection or set.
- Groups are numbered independently of run count and selected indicators.
- Matching labels in different collections or indicator sets do not establish matching inputs or membership.

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

Use the retained simulation/indicator records and the runner's checks.
Changing scientific simulation inputs requires a new experiment; changing selected indicators can
publish a new set from completed compatible responses without running Wflow again.
See [recalculation](running.md#calculate-different-indicators-from-existing-simulations).
Read each named export after the invocation finishes: selected sets publish independently,
and a failed set can leave its previous results available. Check the summary for mixed-age exports.
Managed files may be restored on rerun; keep your own post-processing files elsewhere.

Annual-total depth indicators report mm. With the default set, partial blocks and missing days mean
these equal mean annual depth in mm/yr only when every block is complete and nonmissing.
Inspect `block_coverage` and the [default conventions](../../blueearth_cst/indicators/sets/default/README.md).

## Climate extent and basin cells

Historical stores include a one-source-cell margin around the basin bounding box for forcing preparation.
That rectangle does not enlarge the modelled basin. Read the
[dataset reference](../technical-manual/datasets.md) for spatial support and source substitution.
