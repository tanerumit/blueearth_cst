# R13 — pass 1 (split-only) result

Record of the split-phase falsifier pass run from the primary checkout detached
at `9cbb72a` (below the `wflow_outvars` hoist), 2026-08-21/22.

**Outcome: the split is output-neutral. The one data target that moves is not
R13's, and its cause is dated and attributed.** Nothing was re-recorded; the
re-record is a gate, see the last section.

## What `check_baseline.py check` reports

Run from the primary at `9cbb72a`:

```
FAIL - 3 target(s) differ from manifest:
  config/runs/snake_config_analyze_projections.yml   1d7edd8b vs 00ef44f7
  config/runs/snake_config_build_model.yml           68708d48 vs 00ef44f7
  experiments/experiment/results/q_indicators.csv    610/630 rows, max rel 0.8284
```

Against the runbook's §16.4 acceptance this is **two** deviations, in opposite
directions: the WF3 config snapshot did *not* move (it was predicted to), and a
data target *did* (it was predicted not to). Both are now explained.

## The WF3 snapshot cannot move on this config — and that is R13's neutrality proof

The runbook predicted three `type: yaml` movers. Only two moved.
`experiments/experiment/config/snake_config_run_stress_test.yml` still
normalizes to `00ef44f7`, and this is correct rather than a failure to compose.

`compose_config` returns `project` + `shared` + the sections named by the entry
point's `CONFIG_PROJECTION`. WF1's and WF2's projections name one workflow each,
so their composed documents are strictly narrower than the pre-split whole
config and their digests move. **WF3's projection is wider**
(`run_stress_test.smk:52-63`): it is *derived* from `guarded_sections`, because
WF3 genuinely reads other workflows' sections, so

    R(run_stress_test) = {run_stress_test, build_model, analyze_projections}

On the baseline config, `analyze_climate` is the only remaining stanza and it
carries `enabled: true` and nothing else — verified against `b505233^`. So WF3's
composed document covers **every populated section of the pre-split config**,
and composition is an identity on it.

That is stronger than a null result. `copy_config_files` writes this snapshot as
`yaml.safe_dump(dict(composed_config))` where `composed_config = config` — the
exact in-memory mapping every WF3 rule reads. Pre-split, the same file was a
byte copy of the whole project config, i.e. of what Snakemake loaded. The
normalized digests being equal therefore says:

> the mapping WF3's rules read after the split is value-identical to the mapping
> they read before it.

**R13 cannot have moved a WF3 number by changing a config VALUE.** No bisect is
needed to establish it.

That covers the config-value channel. R13 also changed WF3 *code*, so the
channel of "same values, different handling" is closed separately, by
inspection of the branch diff against `main`:

- `prepare_weagen_config.py` — stops re-reading the project file and takes
  `realizations_num` and `stress_test_cfg` as params (D-10.6). Same two values,
  same `_transient_flag` on the same dict.
- `prepare_cst_parameters.py` — same conversion for the `stress_test` section,
  with a `load_composed_config` fallback for direct invocation.
- `run_stress_test.smk` — `stress_test_grid` is now the single source for the
  grid, which removes a leniency that defaulted a missing `step_num` to 1, and
  `validate_spell_factor` is new. Both REFUSE configs the baseline does not
  have (it sets both `step_num`s and twelve 1.0 spell factors), so neither
  changes a value here.

**`generate_weather.R`, `impose_climate_change.R` and `interchange_contracts.py`
are not in R13's diff at all** — the generator itself is untouched. So the only
WF3 code R13 changes is the plumbing that carries values proven identical.

The confound worth stating: the single WF3 run in evidence has both R13 code
*and* weathergenr 2.0.0 moved at once. There is no (pre-split + 2.0.0) or
(R13 + 1.2.0) run. The above closes it by inspection instead.

(An earlier scratch note recorded this as an anomaly — "the WF3 snapshot did not
compose". It composed; the observation was of an identity, not of a no-op.)

## The q_indicators drift is the weathergenr 2.0.0 upgrade, not R13

| date | event |
|---|---|
| 2026-08-16 09:23 | `82b76a0` — manifest recorded, incl. `indicator_ref/74ed83c06b2e7e6c.csv` |
| 2026-08-17 18:49 | `cf5daa0` — **weathergenr 1.2.0 -> 2.0.0 transition completed** |
| 2026-08-18 | `t2608132341` — Wflow invocation changed in rules 1.14 and 3.15 |

The installed package is now `2.0.0` (`packageVersion('weathergenr')`). The
reference table was recorded under `1.2.0`. A different weather generator draws
different realizations, so WF3's indicators must move.

**The 08-18 Wflow-invocation change is excluded by evidence, not by argument.**
Rules 1.14 and 3.15 did not receive the same edit in `850fb17` — 1.14 moved from
`-e "using Wflow; Wflow.run()"` to a new driver file, 3.15 already had one — but
both now call the **same function**, `WflowProgress.run_with_progress`
(`blueearth_cst/shared/wflow_progress.jl`), which mirrors upstream's
`Wflow.run(tomlpath)` clause for clause and touches no initial state, warm-up or
routing. WF1's discharge target was re-derived in this pass and reproduces the
manifest exactly, so that shared code is numerically inert. `cf5daa0` is the only remaining change that reaches WF3 and
not WF1 — which is also why WF1 matching is no longer the unexplained
counter-evidence an earlier note treated it as, and the manifest's mixed
provenance is not needed to explain it.

`cf5daa0` is a behavioural upgrade, not a version bump: `relax_priority` ->
`relax_order` at both entry points, and its own message records the argument was
**inert on 1.2.0 at both**. A previously-inert generator argument becoming live
changes the generated series.

### The signature agrees once the right expectation is used

Mean absolute relative move, by metric:

| metric | mean rel |
|---|---|
| q_driest_month_mean | 0.384 |
| q_baseflow_index | 0.317 |
| q_mean_annual_7day_min | 0.268 |
| q_mean_annual_min | 0.266 |
| q_annual_mean | **0.014** |

An earlier reading took "annual mean barely moves while baseflow index moves
32%" as evidence *against* re-drawn realizations, on the theory that new
realizations would move every metric about equally. That expectation is wrong
for a fitted stochastic generator: preserving monthly and annual means is what
weathergenr is *for*, while realized daily sequencing — and therefore recession
and low-flow behaviour — is precisely what is free to move between draws. Mean
preserved, extremes moved, is the signature of re-drawn realizations rather than
evidence against them.

Consistent with this, the drift is reproducible and seed-stable: three WF3 runs
at different core counts and batch compositions were byte-identical
(`63120f16`), so batch composition has no numeric effect.

## Also observed, and not R13's

- **Missing DAG edge for `river_attributes`.** Rule 1.06 consumes
  `data/spatial/geoms/river_attributes.geojson` through the spatial catalog at
  runtime but does not declare it, so nothing schedules rule 1.03 and the build
  dies with `NoDataException` on any project whose spatial layer predates
  `c6d35ba`. Belongs on `main`. Boarded.
- Forcing `inmaps_historical.nc` re-derived with a moved digest while
  `staticmaps.nc` and `wflow_sbm.toml` stayed byte-identical, so rule 3.06
  refused the experiment until the reference was re-recorded. WF1's discharge is
  unchanged across it, so the move is byte-level, not numeric.

## The gate

Pass 1 cannot be re-recorded as-is without deciding one thing first: recording
now folds R13's two config-snapshot changes **and** the weathergenr upgrade's
indicator change into one manifest revision, leaving neither separately
attributable. That is the failure mode `t2608071201` watches for. The
alternative is to re-record the indicator baseline on `main` first, attributed
to `cf5daa0`, so R13's pass has a control in which zero data targets move.

Owner's call. Until it is made, `dev/baseline/manifest.json` stays untouched.
