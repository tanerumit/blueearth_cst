---
title: Verify and correct WF2 CIESM precipitation scale
type: todo-item
status: backlog
effort: 1
area: wf2
queue:
created: 2026-10-30
updated: 2026-10-30
---

> [!note] Overview
> **What changes** — Verify THU/CIESM source precipitation units and correct WF2 ingestion or quarantine invalid data before absolute statistics are produced.
> **Why it matters** — Retained CIESM precipitation is about 1000 times smaller than peer models and depresses annual precipitation envelopes; dry filtering drops anomalies but retains absolute values.
> **What it takes** — Trace original source metadata and values through acquisition, reduction and analysis; handle historical and SSP stores, cache identity and regression coverage without plot-side corrections.

## Progress

Next: Inspect pinned CIESM historical and SSP source metadata before WF2 adapter conversion and unit stamping.

- [ ] Verify original CIESM precipitation units and values against the pinned source stores.
- [ ] Implement an evidence-backed WF2 conversion or explicit invalid-source handling with cache invalidation.
- [ ] Verify annual totals, absolute changes, dry eligibility and percentage invariance on retained inputs.

## Investigation evidence (2026-10-30)

Read-only checks used the retained `wrt-egypt-v2` Egypt run under
`data/climate/projections/cmip6/`. No processing or plotting code was changed.

- `analysis/member_anomalies.csv`: CIESM r1i1p1f1, SSP126, reference 1985-2004 has
  reference precipitation 0.1115142195 mm/year and 0.0003055184 mm/day; status is `dry`.
  Its 1950 total is 0.1057370918 mm/year, with an empty anomaly and a retained absolute value.
- Historical scalar CIESM mean is 0.0003073052 mm/day; other retained model means span
  0.0633794 to 0.4782602 mm/day. These comparisons support a scale problem but do not prove its cause.
- Acquisition-cache CIESM precipitation means are 0.0003087567 (historical),
  0.0003160028 (SSP126), 0.0002959391 (SSP245), and 0.0002987023 (SSP585), labelled mm/day.
  These are spatial/time means, not the basin-weighted annual reference statistic.
  The tiny scale therefore exists before scalar reduction and plotting.
- `config/catalogs/cmip6_data.yml` inherits one adapter with precipitation multiplied by 86400
  for all models. This assumes a flux numerically compatible with kg m-2 s-1.
- `blueearth_cst/projections/fetch_gcm_raw.py` stamps configured units after the adapter read;
  `get_stats_climate_proj.py::merge_member_series` stamps units again. The local cache label
  cannot establish the original source units. CIESM retains original variable name PRECT.
- `projection_trajectories.py::member_anomalies` suppresses anomalies below the default
  0.1 mm/day reference threshold but deliberately retains absolute values.
  Session-3 `projection_suite_figures.py::annual_overview` plots those retained values in mm/year.

## Scope and acceptance

Verify original pinned historical and each SSP store before applying any model-specific factor.
A metres-versus-millimetres error is a hypothesis; do not infer a correction from peer agreement alone.
Do not hand-edit the generated catalog; fix its generator or the owning processing contract.
Distinguish invalid units from genuinely dry climate so valid dry members remain interpretable.
If correction is justified, invalidate affected acquisition/scalar/analysis caches through their
owning identities, regenerate derived artifacts, and retain evidence of the conversion.
Check absolute totals and differences, dry-threshold eligibility and exclusion counts.
A common multiplicative correction preserves finite percentage changes only when applied consistently
to historical and future values; threshold eligibility can still change. Confirm temperature and
unaffected models remain unchanged. Keep this work separate from the plotting branches.

## Refs

- Reported during WF0/WF1/WF2 figure review; no roadmap origin is established.
- Retained data: Egypt run `wrt-egypt-v2`, CMIP6 raw, scalar and analysis directories.
- Inspected session-2 processing and session-3 annual overview implementation on 2026-10-30.
