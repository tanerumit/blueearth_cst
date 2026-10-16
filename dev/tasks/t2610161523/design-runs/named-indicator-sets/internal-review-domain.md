# Stage-1b domain review: named indicator sets, design-v1.md

**Reviewer role:** independent domain reviewer (model-validator, documentation-evidence mode). I did not author the design.
**Scope:** whether the calculation interface, aggregation semantics, default-preservation claims and acceptance plan are scientifically defensible. This is not an empirical Wflow validation.
**Evidence basis:** read-only inspection of source at the working checkout. I ran nothing, so I made no numerical parity, execution or fault observations. Where I state pandas behaviour (e.g. `resample().sum()` default `min_count=0`), it comes from library knowledge, not execution.

## Summary judgement

The P3 default-preservation map is accurate to source in every row I checked, and the method contracts are well bounded. They wrap existing reducers, take closed parameters and expose no return-period parameter, so the tested-probability guard cannot be bypassed. But three things block G1 approval:

1. **The parity falsifier (C4) can't be met from the evidence the design names.** The rapid responses cannot cover the tokens and edge policies C4 says it covers, and the design does not name the independent pre-change oracle.
2. **The new /4 unit and policy metadata would misstate what some numbers mean.** It is the first authoritative metadata of this kind, and as drafted it leaves out partial edge years, the one-day block shift from interval-end labels, and how missing days enter annual totals. Its unit for annual totals (`mm`) also conflicts with the source's documented `mm/yr`.
3. **Named result folders don't describe themselves.** User-facing metadata, units, grain and the water-year anchor reach only `_engine/`. So authored indicators and metadata-only edits are invisible in the readable results.

## E1–E6 premise dispositions

| ID | Disposition | Source evidence (inspected) | Narrow confidence |
|---|---|---|---|
| E1 | **Supported** | `experiment/simulation_runner.py:36-39` limits scalar `operation` to `{simulate-and-metrics, metrics-only}`. `:56-84` needs exactly one target, with the allowed set depending on operation. Metrics-only also accepts one exact plan target path. | High, for the target-validation function only. I did not trace runner subprocess behaviour. |
| E2 | **Supported, with qualification** | `experiment/metric_export.py:52-53` exports to the flat `results/metric_sets/` with tracking `_engine/metric_sets/current.json` (`metric-export/1`). Qualification: legacy immutable result roots may also sit at `results/metric_sets/<short-digest>/` (`metric_plan.py:828`, `:1011-1015`; `metric_result_pattern` `:543-544`). The proposed named folders share that parent. | High for the export path. Medium for how many legacy per-ID roots exist in real projects. |
| E3 | **Supported, with qualification** | `metric_registry.declarations` (`:164-195`) gives grain `bundle` for class B and `run` otherwise, plus two `group_reduction` policies. `reduce_group_mean` (`:356-379`) is gated by `GROUP_MEAN_STATISTICS` and propagates NaN with equal weights. `reduce_bundle` (`:522-627`) pools member-local blocks. Qualification: `shared/indicator_tables.py:242` (`METRIC_CLASSES`, "C": "pooled") and `metric_grain()` still mark class C as pooled-only, contradicting the registry. Neither is used in code. | High. |
| E4 | **Supported** | `metric_plan.py:449-477`: the definition digest covers declarations, grouping and reference strings, resolved references, anchor, code inventory and return-level validation. The identity projection adds simulation ID, response identity, environment digest, groups and run groups. `implementation_revision` hashes the whole bytes of `metric_registry.py`, `metrics_definition.py` and `indicator_tables.py` (`metric_registry.py:147-150`). So the planned edits change every default identity, and C4 can prove numerical parity only, not identity reuse. The design acknowledges this. | High. |
| E5 | **Supported, with qualification (as the design states)** | `metric_plan.metrics_only_configuration` (`:84-158`) reads live `simulate_system.metrics`, `model.outvars`, `climate.water_year_start` (anchor `YS-<MON>`, `:136`) and an optional `scenario_collection` assertion. Everything else comes from retained `_engine/simulation*.json` and the retained `response_request`. It opens no generation or model workflow config. | High for this function. I did not inspect the rule bodies of `metrics_only.smk` past its header. |
| E6 | **Untestable as stated** | It is a hypothesis about future code. Every P3 row matches source (see "Supported aspects"), so the hypothesis is plausible. The falsifier (C4) currently lacks a named oracle and coverage map (domain-1). Static text cannot establish equivalence. | No confidence either way until pre-change parity evidence exists. |

## Findings

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: major
    section: "Capability map, handoffs and acceptance"
    finding: >
      C4 promises coverage of "all tokens, references/ties, missing/partial years, rolling
      boundaries, singleton and pooled GEV policies". The same section says "Reuse the same
      affected rapid responses/outputs; no new simulation is required". The rapid responses
      cannot supply most of that coverage, and the design names neither the independent
      pre-change oracle nor a case-to-evidence coverage map.
    rationale: >
      Rapid retains only q/aet/gwr (test_case/project_config_rapid.yml:70) with
      n_realizations: 2 (project_config_rapid_generate_scenarios.yml:3). Singleton groups
      exist only at n_realizations=1 (scenario_rows.stochastic_rows; metric_groups keys by
      st_id). Rapid sets no water_year_start, so the anchor is January and the
      partial-edge-block policy is barely exercised. Its real data almost never produces
      monthly-sum ties, NaN days, all-NaN years, a zero annual mean (the infinite-BFI
      refusal, metric_registry.py:337-338), fewer than 10 GEV blocks
      (InsufficientReturnLevelBlocks) or estimator refusals (InvalidReturnLevelFit).
      Token precedence also has unstated edge cases. On the simulation path,
      simulate_and_metrics.smk:63 uses .get("outvars", DEFAULT_WFLOW_OUTVARS), so an
      explicit `outvars: null` gives no tokens. Metrics-only (metric_plan.py:129-134) and
      the export (metric_export.py:26-34) instead fall through to response_request. If
      post-change code generates the oracle, or the oracle covers only rapid, then a parity
      claim for E6, the central default-preservation premise, would rest on partial
      coverage.
    suggested_fix: >
      Make a named pre-change evidence set a precondition for any parity claim. Produce it
      with the code at 791fd1f (or the last commit before the change), then retain the
      bytes and their sha256 before the first implementation commit:
      (a) the rapid retained /3 sets as configured, plus a metrics-only re-reduction of the
      same retained responses with climate.water_year_start: OCT. Indicator-only uses the
      live anchor, so this exercises partial edge blocks without a new simulation.
      (b) synthetic native CSV/TOML fixtures, built from existing producer schemas, for
      precip/snow/overland_flow, n_realizations=1, NaN days, an all-NaN water year, a
      constructed monthly-sum tie, a zero-mean year, fewer than 10 blocks, and a constant
      GEV sample.
      (c) the full captured surface: run/group CSV bytes, group_members/metadata,
      expected_result_keys, resolved_references (month and counts),
      return_level_evidence.json (block counts, parameters, shape coverage), and each
      refusal's exception class and message.
      (d) the token-precedence matrix (metrics absent/null/list; outvars absent/null/[];
      simulation vs indicator-only).
      (e) hand-solved values, computed outside the package, for at least one fixture per
      proposed method ID.
      Put the case-to-evidence map in the design, so each C4 clause names its source.
  - id: domain-2
    severity: major
    section: "Closed set schema and ownership (P2)"
    finding: >
      The proposed registration metadata (output units plus temporal, missingness and
      validity policies) does not state three real properties of the preserved reducers.
      (1) For any non-January water year, two partial edge blocks are always included with
      equal weight. (2) Blocks are assigned by interval-end label without shifting, so each
      annual or monthly block includes the previous period's last day. (3) Annual sums treat
      missing days as zero and give 0 for an all-missing block. The stated unit rule
      ("annual totals integrate mm dt-1 to mm over an annual block") also conflicts with
      the source's documented mm/yr for the mean of annual totals.
    rationale: >
      simulation_window is set in calendar years (snake_utils.resolve_simulation_window via
      historical_window_bounds) while the anchor is YS-<water_year_start>
      (metric_plan.py:136; simulate_and_metrics.smk:64). With water_year_start OCT and a
      Jan–Dec window, the first and last blocks hold about 9 and 3 months. Because every
      annual block gets equal weight, a 9-year run's mean annual total comes out about 10%
      low, mean annual maxima come out low, and partial blocks enter the GEV samples
      (PARTIAL_BLOCK_POLICY retain_partial_period_blocks/1).
      wflow_response_reader.py:95 and :134 put the first label at starttime+step, labelled
      interval_end. reduce_run, the md.* reducers and reduce_bundle resample on labels
      directly (metric_registry.py:322-329, :578-582).
      getattr(frame.resample(anchor), "sum")() (metric_registry.py:325) uses pandas'
      default min_count=0.
      indicator_tables.py:220-221 documents annual_total "in mm/yr". The published value is
      a mean over years, so "mm" per block is not its unit.
      These are existing behaviours, and keeping them is correct. But /4 is the first place
      the toolbox makes authoritative unit and policy claims, and authored YAML titles such
      as "mean annual total" will rely on them. C6 fails only when metadata contradicts the
      method; it does not fail when a policy is left out. So the design's claim that
      "registry metadata describes the method truthfully" is not yet checkable.
    suggested_fix: >
      Without changing any numbers, make each method contract record: block assignment by
      interval-end label without shifting; partial edge blocks retained with equal weight
      (in both annual reductions and GEV blocks); the NaN rule for each statistic (sum skips
      NaN with min_count=0; mean/max/min/quantile skip NaN; rolling(7) needs 7 complete
      values). Make G1 decide the output unit for mean-of-annual-totals explicitly, either
      "mm yr-1" or "mm per water year, partial edge blocks included", consistent with the
      indicator_tables docs. Extend C6 into a positive check: each declared policy must be
      confirmed by a behaviour fixture from domain-1(b), not just checked for contradiction.
  - id: domain-3
    severity: major
    section: "Planning, identity and publication (P4)"
    finding: >
      Named readable folders contain only the 4-column CSVs and group_members/
      group_metadata. Titles, descriptions, output units, method/parameters, grain, group
      policy and the water-year anchor reach only _engine/ JSON. So the agreed user-facing
      metadata never appears in the readable results.
    rationale: >
      Default IDs are interpretable through a fixed vocabulary and the derived glossary
      (indicator_tables.py:45-49). Authored indicator IDs have no such glossary. One
      *_group_indicators.csv mixes equal-weight means of run reductions with pooled GEV
      fits under the same group_id (metric_plan.py:701-746), and only the declarations tell
      them apart. A metadata-only edit makes a new publication_id but a byte-identical
      readable folder. An indicator-only reduction after a change to
      climate.water_year_start replaces default/ contents, with nothing readable recording
      the anchor change. The likely consequence is a units or grain misreading by people
      and downstream analysts who use the readable tables. This contradicts no settled
      preference: a derived readable dictionary is neither machine JSON nor a hash.
    suggested_fix: >
      Make it a G1 decision. Either add a derived, hash-free indicators.csv to each named
      folder (metric, title, description, variable, output_units, method, parameters,
      grain, group_policy, water_year_start, references), generated from the immutable
      publication record and listed in its file inventory. Or accept non-self-describing
      exports explicitly and document where readers find the metadata.
  - id: domain-4
    severity: minor
    section: "Closed set schema and ownership (P2)"
    finding: >
      "The registry derives definition records from" indicator_tables. But
      indicator_tables.METRIC_CLASSES and metric_grain() mark wet/dry (class C) as
      pooled-only, while metric_registry.declarations emits them at run grain. The design
      warns only about stale prose, not this stale code contract.
    rationale: >
      indicator_tables.py:242 has "C": "pooled", and metric_grain returns that.
      metric_registry.py:177 has grain="bundle" if kind=="B" else "run". A grep found no
      code caller of metric_grain. If a resolver took grain from METRIC_CLASSES, wet/dry
      run values would disappear. C4 key parity would catch that, hence minor.
    suggested_fix: >
      State that grain and group-policy authority is metric_registry.declarations only.
      Correct or retire METRIC_CLASSES, metric_grain and the POOLED_REALIZATION prose in the
      same implementation.
  - id: domain-5
    severity: minor
    section: "Decision and boundary"
    finding: >
      `low_flows` appears as the selected set in the Decision sentence and the P1 config
      example. Despite the disclaimer, this risks adopting an illustrative science set.
      The existing method vocabulary also has no low-flow exceedance percentile.
    rationale: >
      indicator_tables.py:151-155 records that q_mean_annual_p95 is a high flow, the
      opposite of the conventional Q95. A "low flows" set assembled from existing
      definitions would be limited to q min, 7-day min, BFI, the 2-yr 7-day min return level
      and the driest month. A conventional low-flow percentile would need a new method and
      its own qualification, as the design itself says for new methods.
    suggested_fix: >
      Use a neutral placeholder (e.g. `example_subset`, already used in P2) in the Decision
      sentence and the P1 example. State that any low-flow content is a separate
      commission. Keep the p95 parameter value tied to the existing `_p95`
      non-exceedance meaning in the method docs.
  - id: domain-6
    severity: minor
    section: "Compatibility and migration (P5/P6)"
    finding: >
      Named folders `results/metric_sets/<set-id>/` share a parent with legacy immutable
      /3 result roots `results/metric_sets/<short-digest>/`. A hex-prefix digest can match
      the set-ID pattern `[a-z][a-z0-9_]*`.
    rationale: >
      metric_plan.py:1011-1015 accepts result_root `results/metric_sets/{short}`, and
      metric_result_pattern keeps that layout for forced reuse (:543-544). Those
      directories may hold the very pre-change evidence C4 depends on. "Reject ID/path
      collisions" is generic, and the C6 matrix does not list this case.
    suggested_fix: >
      Refuse set IDs that match the short-digest pattern or an existing child directory of
      results/metric_sets, and add that case to C6.
```

## Supported aspects

These match the code I inspected:

- **q mean/max/min/p95:** annual statistic, then mean over years. p95 is `quantile(0.95)`, a non-exceedance high flow (`metric_registry.py:326-329`).
- **7-day extrema and BFI:** rolling is done per member (`reduce_run` is called per run, `metric_plan.py:723-733`; per member in `reduce_bundle`, `:577-582`). Windows can cross water-year boundaries but never member boundaries. BFI is the mean of annual ratios, and infinite values are refused.
- **Basin variables:** sum/max/mean per `BASIN_METRIC_SUFFIXES`, at the per-location grain.
- **Wet/dry reference:** pooled unperturbed members (all stochastic rows are `evaluated=True`), first native q gauge, calendar-month sums, the first month wins ties, and one resolved month applies everywhere (`:235-295`, `metric_plan.py:418-434`).
- **Group means:** equal weights with NaN propagation (`:342-379`).
- **Return levels:** member-local blocks pooled per `st_id`, including singletons. Required blocks are max(ceil(T), 10). T is fixed at 10/2 years (`indicator_tables.py:183-184`), and exact-probability coverage is guarded.
- **Screening:** correctly labelled provisional.
- **Serialization:** float32 formatting is preserved (`metric_plan.py:754`).
- **Method contracts:** they forbid user-set units, calendar, grain, missingness, aggregation and reference policy, and expose no return-period or probability knob. This keeps numerical meaning out of user YAML.
- **Reference-free subsets:** they don't acquire reference requirements, consistent with `metric_plan.py:418`. Bundle-only subsets with header-only run tables match HM-7 v2 (`interchange_contracts.py:859-861`).
- **Water-year anchor in indicator-only runs:** the current anchor is used and recorded in numerical identity, which is honest about today's behaviour.
- **Separating parity from science:** the design distinguishes numerical parity from scientific adequacy, makes no acceptance claim for the second set, and requires its own qualification for new methods.

## Material framing decisions for G1

1. **Pre-change oracle:** contents, coverage map, producing commit and custodian (domain-1). This is a precondition, not a later deliverable.
2. **Output unit for mean-of-annual-totals** (`mm yr-1` vs per-water-year), and whether /4 contracts must state partial-block, label-assignment and NaN-sum policies (domain-2).
3. **Readable indicator dictionary** in named folders vs explicitly accepting non-self-describing exports (domain-3).
4. **Grain authority** is `metric_registry.declarations`, and stale `METRIC_CLASSES` is fixed or retired (domain-4).
5. **Token-precedence edge cases:** in the new mode, reproduce the current split behaviour for `outvars: null` exactly, or refuse it. Legacy mode must reproduce it (domain-1(d)).
6. **Placeholder name** for the unspecified second set (domain-5).

## Limitations of this review

- These are inspection-only conclusions. I made no execution, numerical parity check or fault injection.
- I did not inspect `gev_lmoments`, `return_level_validation`, `response_series.validate_responses/compatible_bundle`, the full `metrics_only.smk`, or the rest of the HM-7 validator. Statements about their behaviour come from call sites.
- The pandas behaviours I cite (`min_count=0`, skipna, rolling completeness) come from library knowledge, not execution. Their exact effect on the fixtures should be confirmed by domain-1(b).
- Indicator-only runs reduce with the current `climate.water_year_start`, while generation also consumes a water-year setting (`generation_plan.py:224`). Whether mismatched year definitions matter scientifically for a given case is outside this design's scope. It stays visible through identity, and domain-3 would make it readable.
- I did not assess whether the existing default indicators are fit for any decision. Preserving them is not validating them.

## Skills applied

- **model-validator** role rules: evidence-coverage mapping, keeping inspection separate from execution, naming failure regimes (partial blocks, refusals), and refusing to read equivalence from static text.
- **claim-evaluation**, including the claim-and-inference reference: a claim map of E1–E6 and the P3 rows, a check of the inference chain from "delegate to existing reducers" to "parity", and confidence language held to the weakest load-bearing step.
- **time-series** and **hydro-model-validation** considerations (block construction, rolling completeness, water-year partitioning, interval-end labelling, pooled-block extremes) came from the role rules. I did not load those skills' separate files in this session.