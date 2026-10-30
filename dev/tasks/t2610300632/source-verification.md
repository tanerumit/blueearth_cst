# CIESM precipitation source verification

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

## Direct source verification (2026-10-30)

Public pinned Zarr metadata and the first global precipitation field were read directly, without
HydroMT or WF2 conversion code. Each store labels `pr` as `kg m-2 s-1`, original name `PRECT`.
The calculation was `sum(pr * cos(lat)) / sum(cos(lat)) / nlon * 86400` for time index zero.
This is a latitude-weighted diagnostic on the regular grid, not a multi-year climatology.

| Experiment | Version | Global mean (mm/day) | Global maximum (mm/day) |
| --- | --- | ---: | ---: |
| historical | v20200417 | 0.0030045478 | 0.0421855077 |
| ssp126 | v20200417 | 0.0029526440 | 0.0371448435 |
| ssp245 | v20200417 | 0.0029537240 | 0.0371140540 |
| ssp585 | v20200605 | 0.0029874603 | 0.0452251621 |

Store pattern: `https://storage.googleapis.com/cmip6/CMIP6/{activity}/THU/CIESM/`
`{experiment}/r1i1p1f1/Amon/pr/gr/{version}/`; metadata is `.zmetadata`.
Activity is CMIP for historical and ScenarioMIP for SSPs. Historical first month is January 1850;
SSP first month is January 2015. Only these four r1i1p1f1 first-month fields were sampled.

Conclusion: the scale anomaly exists in the published source and affects all four sampled stores.
WF2's multiplication by 86400 is dimensionally correct for the declared source units.
A missing upstream metres-to-mass-flux conversion is plausible: multiplying the sampled global means
by 1000 gives about 3 mm/day. The exact correction is not established by metadata or this diagnostic.
Do not silently rescale CIESM by 1000 without producer evidence or an independently verified replacement.
Prefer explicit invalid-source handling in WF2, including absolute products and coverage reporting.
This refines the earlier suspected WF2 conversion error to an upstream source-quality problem that WF2
must handle before analysis. The plotting branches remain unchanged.

Independent literature corroborates the problem: Monerie (2026), section 4, describes CIESM precipitation
climatology as too low, suspects post-processing errors, and recommends avoiding its precipitation.
[The Elo rating system as a new narrative for ranking climate models](https://doi.org/10.1088/2515-7620/ae661c).
This corroborates invalid-source handling; it does not establish a numerical correction.

Execution: `pixi run python` with anonymous gcsfs and `xarray.open_zarr`, consolidated metadata,
`decode_times=False`, `isel(time=0)`; all four reads/calculations completed, exit code zero.
An ignored gcsfs/aiohttp shutdown callback emitted a cross-event-loop error after results were printed;
no source read or calculation failed. Direct metadata reads also succeeded independently via HTTPS.
