---
title: "Choose and recalculate indicators"
subtitle: "Select results from the responses your simulation retains"
---

Choose indicators for the question, location and period you need to assess.
The toolbox's registry and calculation scripts define the indicators and formulas.
A set selects those calculations; it does not define a different method by editing YAML.

## Configuration

Edit `project_config_simulate_system.yml`, or the file named by `workflows.simulate_system.config_path`
in `project_config.yml`:

1. In `operations`, select `simulations`, `indicators`, or both.
   List each choice once. Their order does not matter.

2. In `indicator_sets`, choose the sets to calculate.
   You can list set ids or provide their settings inline. If you leave this setting out, the toolbox
   uses `[default]`. Start each set ID with a lowercase letter. After that, use only lowercase letters,
   digits, underscores or hyphens. Keep the whole ID to 64 characters or fewer.

   The `default` set is defined in `config/indicator_sets/default.yml`.
   It selects indicators for `model.outvars`. If that setting is absent, it uses the toolbox defaults.
   When calculating indicators without simulations, it uses the variables retained in the experiment.

3. To choose your own set of indicators, copy `config/templates/indicator_set.template.yml` and set
   its `config_path`. Use an absolute path or a path relative to the simulation file
   (`project_config_simulate_system.yml`) that declares it.
   The toolbox reads each selected set file once per invocation.

   A custom set chooses existing calculations and can give them your own indicator names.
   It does not change arithmetic, units, calendars, missingness or grain.

Before simulating, check that `model.outvars` retains all variables needed by your selection.
Indicators-only work reads retained responses; it cannot add a variable the model never wrote.

## Choose a set

Read the selected set's conventions and limits before using its values:

- [Default](../../blueearth_cst/indicators/sets/default/README.md): standard hydrological summaries.
- [Flow regime](../../blueearth_cst/indicators/sets/flow_regime/README.md): additional flow summaries.
- [eflow-erfa](../../blueearth_cst/indicators/sets/eflow_erfa/README.md): flow-regime indicators,
  without ecological risk classification.
- [Crop-water](../../blueearth_cst/indicators/sets/crop_water/README.md): screening indicators and the
  complete historical-threshold preparation requirements. These are not crop yield/damage estimates.
- [Flood discharge hazards](../../blueearth_cst/indicators/sets/flood_risk/README.md): opt-in hazard
  calculations. The supplied qualification supports only its 2- and 10-year examples;
  selecting every declared example fails at an unsupported probability.

For custom selections and exact settings, see [indicator requests](../technical-manual/indicator-requests.md).
Follow the selected set's instructions for any thresholds or historical inputs it needs.

## Handle missing inputs

The default `indicator_evaluation: strict` refuses a request with missing required inputs.
With `indicator_evaluation: partial`, check which input is missing:

- If a required response variable is absent, the whole calculation is omitted from the value tables.
  Find its declaration and missing-input explanation in the dictionary and `indicators.json` manifest.
- Missing parameters at retained locations can instead produce rows with `status: unavailable`
  and no value. Read their `reason` before comparing results.

Malformed supplied parameters still fail; partial mode does not make them valid.

Read each table's `status` and `reason`:

- `available`: a calculated value is present.
- `undefined`: the calculation produced an undefined value, such as an absent-event timing.
- `unavailable`: a required location parameter was missing; inspect the reason before comparing results.

Supplying a missing threshold can allow a new indicator publication from the same retained responses.
A missing response variable requires a new simulation with that variable selected.
See [outputs](outputs.md#reading-an-indicator-set) and the set conventions for interpretation.
Advanced readers can consult [input evaluation and recovery](../technical-manual/indicator-requests.md#inputs-evaluation-and-recovery).

## Recalculate from completed simulations

Follow [Calculate different indicators from existing simulations](running.md#calculate-different-indicators-from-existing-simulations).
Keep the existing experiment, set `operations: [indicators]`, and choose the sets to calculate.
The completed simulation record is required even for a dry run.
Changing model, scenario collection or scientific simulation inputs requires `--new-experiment` instead.

## Extend a calculation

Advanced readers can use the [independent module contract](../../blueearth_cst/indicators/README.md)
and [technical extension guide](../technical-manual/indicator-extension.md).
They cover trusted registration, explicit inputs and independent checks.
This user guide does not define a new formula or a supported response-surface construction procedure.
