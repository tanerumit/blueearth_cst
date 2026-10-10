# Landing scientific and visual acceptance

Status: final retry WF0/WF1 scientific, caption and map checkpoints pass; all 17 fresh WF2 figures pass
the bounded caption/visual checkpoint. Spatial title-clipping limitations are disclosed below.
The coordinator retains responsibility for all-five execution, inventory, provenance and landing gates.

Final retry candidate supplied by coordinator: `c567854e` (test/audit-only changes from first-run
candidate `b5ff0b41e890f05c1c71ca0c3965e946ef29e231`; rendering/scientific source unchanged).
The coordinator reports that the rebase delta from `99939abf` contains task records/TODO only;
this reviewer does not perform Git operations. Existing deterministic science acceptance is reused
from ../map-reference/scientific-report.md, scientific-preparation-report.md,
scientific-reference-report.md and scientific-consumer-report.md. The earlier calendar, units,
native-field, boundary, corruption and controlled missing/unscaled checks are not rerun here.

Final retry project root:
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/.tmp/pytest/run-4bf42bbc57744ddb8ec629e34230630c/test_all_five_workflows_run_en0/project`.
First-run project root, retained for the completed WF0 checks below:
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/.tmp/pytest/run-7dcd6ef3955a4ac798895553597914fd/test_all_five_workflows_run_en0/project`.
Workflow progress is read from its sibling run_workflows.log. NetCDF products will only be opened
after their owning producer completes. Source, Git, test execution and workflow writes are excluded;
this reviewer owns only this report and performs no nested delegation.

## Acceptance plan

| Claim | Completed-product evidence | Status |
|---|---|---|
| WF0/WF1 use common frame/reference/classes | Reference JSON and all map caption records | Pass |
| Captions honestly describe field and scale | Native support, dates, completeness, counts, exceedances | Pass |
| WF0 source maps retain native scientific display | Four fresh map PNGs and source fields/metadata | Pass |
| WF1 forcing maps preserve support and disclose actual window | Three fresh map PNGs, forcing dates, mask/counts | Pass |
| Annual/monthly figures remain legible | WF0 and all six WF1 annual/monthly charts | Pass |
| WF2 shared figure helpers remain usable | All 17 completed projection figures and captions | Pass |

The coordinator owns exact fresh WF0 before/after parity, complete workflow inventory and provenance,
execution gates and Git landing. WF1 comparisons will be conditioned on actual input/window identity;
the previously retained 2010-2016 case is not assumed equal to a fresh 2000-2016 forcing run.

WF2 review concerns scenario/period/member labels, variable units, honest ensemble captions, legend
placement and clipping in affected shared-helper outputs. It does not add observational hydrological
validation or treat projection ensemble spread as full uncertainty. Availability/unscaled edge cases
remain covered by the accepted controlled probes unless the fresh products exercise additional cases.

## Checked products and exceptions

WF0 was inspected after the coordinator confirmed its completion at 14:51:13 on 2026-10-10.
No active WF1 file was opened. No new synthetic oracle or production run was executed by this reviewer.

### WF0 measured scientific and caption facts

All four map caption records exactly match the completed reference ID, full frame object and their
full variable-specific historical-reference object, including class boundaries and colors. These
equalities were asserted in a read-only PowerShell inspection of the JSON records; it exited 0.
Reference ID: `dbb0803a2a3bcb009e03aff5b28f9a380562a9514a619a3c2241abc7c63cc071`.
Reference path relative to project: `data/climate/historical/_engine/map_reference.json`.

The selected ERA5 EPSG:4326 frame is [9.375, 10.125, 0.125, 0.625], aspect 1.0000214187946257.
Longitude ticks are [9.4, 9.6, 9.8, 10.0], latitude ticks [0.2, 0.4, 0.6]. Field and reference
completeness are both 3 missing days/month and 15/year. All four source periods are 2000-2016.

| Variable | Pool count | Extrema | Class boundaries |
|---|---:|---|---|
| Precipitation | 35 | 2360.604248046875, 2936.814453125 | 2300 to 3000 by 100 mm/year |
| Temperature | 6 | 25.04983139038086, 25.912567138671875 | 25.0 to 26.0 by 0.2 degC |
| Source PET | 6 | 1032.9930419921875, 1157.6995849609375 | 1000, 1100, 1200 mm/year |

These numbers agree with the previously accepted independent pool oracle. The new reference ID is
the fresh run's identity; equality with another run's ID is not required or inferred.

| Fresh map | Displayed / finite / unavailable | Eligible-year range | Strict under / over |
|---|---|---|---|
| ERA5 precipitation | 6 / 6 / 0 | 17 / 17 | 0 / 0 |
| ERA5 temperature | 6 / 6 / 0 | 17 / 17 | 0 / 0 |
| ERA5 PET | 6 / 6 / 0 | 17 / 17 | 0 / 0 |
| CHIRPS precipitation | 30 / 29 / 1 | 17 / 17 | 0 / 0 |

Every map is available. Captions correctly state annual totals versus temperature means, native
closed-frame support, upper-endpoint inclusion, gray unavailable versus white exterior cells, and
absence of interpolation. ERA5 is temperature-carrier; CHIRPS is precipitation-only. Source PET has
the de Bruin/model-PET distinction. This run does not naturally exercise unscaled or disjoint maps;
the accepted bounded scientific-consumer probes remain the evidence for those cases.

The coordinator's completed fresh-wf0-acceptance.json reports exact preservation of 12 native arrays,
54 CSV tables and 51 temporal PNGs, plus four map outputs. This reviewer read that result and the
comparison implementation; the coordinator executed the parity check. Numerical preservation is not
inferred merely from successful workflow execution or visual similarity.

### WF0 image inspection

All paths below are relative to project/data/climate/historical/. All four maps and seven listed
annual/monthly charts were opened directly using view_image. Visual verdict: pass, with no observed
clipping, ambiguous legend or lost native support. The map overlays/gauge labels and class bars remain
legible. CHIRPS's one gray cell is visibly distinct from the white area outside its smaller native grid.

| Folder | PNGs opened |
|---|---|
| era5_20000101_20161231/plots/ | era5_precip_annual_clim_map_basin_ext.png |
| same | era5_temp_annual_clim_map_basin_ext.png |
| same | era5_pet_annual_clim_map_basin_ext.png |
| chirps_20000101_20161231/plots/ | chirps_precip_annual_clim_map_basin_ext.png |
| era5_20000101_20161231/plots/ | era5_precip_annual_trend_ts_basin_avg.png |
| same | era5_precip_monthly_clim_band_basin_avg.png |
| same | era5_temp_monthly_clim_band_basin_avg.png |
| chirps_20000101_20161231/plots/ | chirps_precip_annual_trend_ts_basin_avg.png |
| same | chirps_precip_monthly_clim_band_basin_avg.png |
| comparison/plots/ | comparison_precip_annual_trend_ts_basin_avg.png |
| same | comparison_precip_monthly_clim_band_basin_avg.png |

Annual plots label precipitation in mm/year and descriptive trend slopes (-162 and +31 mm/decade)
without obscuring the series. Monthly plots label mm/month or degC and show all Jan-Dec ticks.
Comparison legends correctly distinguish ERA5 and CHIRPS; shaded 10th-90th percentiles are described
as variation across available years rather than a confidence interval. Their complete captions state
2000-2016 and equally weighted basin grid-cell averages. The upper-left or upper-right legends occupy
unused plot space and the comparison annual legend sits clearly above the plotting area.

Coverage boundary: 44 other WF0 temporal PNGs were not individually reopened in this landing review;
the coordinator's exact byte equality covers them. Fresh optional captioned variants are not enabled;
the same unchanged code's four captioned source variants were already accepted in the prior checkpoint.
WF1 maps and annual/monthly charts, and relevant WF2 outputs, remain pending their producer completion.

### Final retry WF0 reconciliation

The first all-five run stopped during WF1 when the external P-drive mount became unavailable; it had
not produced completed WF1 or WF2 outputs for this review. The coordinator restored the mount and
started a fresh root. Final retry WF0 completed at 15:43 on 2026-10-10. Inspection here was limited to
its closed WF0 products; active WF1 outputs remained untouched.

The final reference ID is
`7863a5e4c8425ab4307e563e919ae11261c6f292077c95fb21ea0b762b74e724`.
All four final map records were independently asserted to match this ID, the complete current frame
and the complete current variable-specific scale object. Caption prose is exactly unchanged from the
first-run records. Periods, policy 3/15, eligibility [17,17], displayed/finite/unavailable counts and
zero strict under/over counts remain exactly as tabulated above. All four are available.

Every final map PNG is byte-identical to the corresponding first-run PNG directly opened above.
Their visual verdict therefore carries forward exactly. Temporal figure science/visual evidence is
also reused: the coordinator's fresh-wf0-parity-v2.log and fresh-wf0-acceptance-v2.json again prove
12 native arrays, 54 tables and 51 temporal PNGs preserved, with four maps present. No new scientific
oracle or duplicate chart review was needed; there was no reduction in accepted output coverage.

The reference identity difference was traced rather than attributed to the changed project path.
Only source_preparations differs among top-level identity components. Within it, CHIRPS is unchanged;
ERA5's preparation identity differs only in the extraction-file input SHA-256:

- First run: `6c4c299d4f54e7bdba0df2b61b6c4dfb9d845b5a6de247ff96ca5b7a01e1a2c6`.
- Final retry: `a8c83c88ac575bbd5eabdd36bc05198eed41011a735823e53052abab607aee82`.

ERA5 preparation ID consequently changes from
`15b1b7987048af0982f27ef7edb1dd618feedc3377cb0efd82dd81701fc0bbe4` to
`9bf6f44c6968168d76b9101989e9f693bacc6265eb1a3c20f269e113cece42a8`.
Both sources' scientific field digests, code/catalog/environment identities, basin-cell hashes and
ERA5 orography hash are unchanged. The coordinator's exact raw scientific-data comparison passes in
both runs. Different extraction bytes correctly change a byte-sensitive provenance identity while
scientific equality remains intact. This review did not diagnose the NetCDF serialization byte cause
and does not treat scientific equality as byte identity.

Final retry WF0 verdict: pass. Fresh WF1/WF2 scientific and visual checkpoints are still pending,
with prior accepted evidence retained; no all-five landing pass is implied by this partial checkpoint.

### Final retry WF1 checkpoint

This later checkpoint supersedes the pending statement above. The coordinator confirmed completion
at 15:52:06; plot_model_forcing completed at 15:51:24. Only closed products were inspected.
All three forcing map caption records were independently asserted equal to the current reference ID
`7863a5e4c8425ab4307e563e919ae11261c6f292077c95fb21ea0b762b74e724`, its complete frame and their
variable-specific scale objects. The read-only JSON assertion exited 0.

Forcing input dates are 2010-01-01 through 2016-12-31, and all three field periods are 2010-2016.
Captions distinguish these dates from the historical scale's 2000-2016 period. Each map has 257
displayed, finite basin cells, zero unavailable cells, eligible-year range [7,7], and policy 3/15.
All are available. Strict under/over counts are precipitation 0/0, temperature 3/145 and PET 0/0.
The temperature over-class color is consequently extensive, as the actual image shows. Captions
describe native support, no interpolation, annual amounts versus temperature means, and model PET's
derivation distinction. Availability/unscaled and nonintersection edge cases reuse earlier probes.

The coordinator's fresh-wf1-acceptance.json reports 9 exact scientific arrays/attributes, 6 exact
CSV tables and 6 exact temporal PNGs against before-retained/wf1, after explicitly isolating rebuilt
latitude/GeoTransform representation differences. Both maximum absolute coordinate differences are
7.105427357601002e-15 degrees; full_dataset_identity is false. This is approximately 8e-10 metres or
8.5e-13 of the 0.00833-degree cell spacing, scientifically immaterial for these native-support maps.
The coordinator's 1e-12-degree guard is approximately 1.1e-7 metres. Exact scientific values,
counts/masks/attributes and identical support/exceedances justify acceptance; full raw dataset or
coordinate-byte identity is explicitly not claimed. The original strict identity failure is retained.

All nine PNGs under models/hydrology/wflow/forcing/plots/ were directly opened:
forcing_{precip,temp,pet}_{map,annual,monthly}.png (all nine combinations). Maps show legible gauge
labels, frame ticks, class bars, native basin support and white exterior. Annual charts show 2010-2016;
monthly charts show all Jan-Dec labels and clear Wflow forcing/10th-90th percentile legends. Trend
annotations are +327 mm/decade precipitation, +0.32 degC/decade temperature and -79 mm/decade PET.
No forcing chart label, legend or artist clipping was observed.

Additional affected-consumer visual coverage, paths relative to project:

| Folder | PNGs directly opened |
|---|---|
| data/spatial/plots/ | subbasins.png, elevation_basin.png, land_cover_basin.png |
| same | lai_clim_basin.png, soil_clay_basin.png |
| models/hydrology/wflow/evaluation/plots/ | wflow_aet_annual_ts_basin_avg.png |
| same | wflow_aet_monthly_clim_band_basin_avg.png |
| same | wflow_gwr_annual_ts_basin_avg.png |
| same | wflow_gwr_monthly_clim_band_basin_avg.png |
| same, stations/ | hydrograph_1010.png, performance_1010.png |
| same, stations/ | signatures_lows_1010.png, signatures_peaks_1010.png |

Subbasin labels, inset, scale bar, elevation colorbar and categorical land-cover legend are legible.
The evaluation charts and station panels have readable units, panel labels and legends. Their captions
correctly distinguish annual 2012-2016 from monthly 2011-2016 after initial-year exclusion. This is a
presentation review, not an assertion of observational hydrological skill, calibration quality or
physical adequacy based on the rapid fixture's reported metrics.

Residual spatial-layout limitations: LAI and soil-clay colorbar titles touch/cross the upper image
boundary. The directly opened export-mechanics/baseline/spatial/thematic/soil_clay_basin.png shows
the same clay-title clipping, proving that case inherited. No retained LAI image was available here.
The coordinator verified unchanged plot_spatial_maps.py renderer/label/layout code against main;
this is code-equivalence evidence, not a claim of before-image or byte equality for LAI. Record LAI
as a residual spatial-layout limitation outside the newly shared source/forcing-map acceptance.
Neither limitation changes map scientific fields. This checkpoint does not assert every spatial
figure is publication-ready.

Bounded coverage: 22 fresh WF1 PNGs were opened (9 forcing, 5 spatial, 8 evaluation). Six other soil
maps and the 12 evaluation panels for stations 1020/1030/1040 were not individually opened. Ordinary
outputs are covered here; previously accepted optional captioned variants remain reused evidence.
WF1 source/forcing scientific and caption/map verdict: pass, with the disclosed spatial limitations.

### Final retry WF2 checkpoint

The coordinator confirmed WF2 completion at 15:54:55. All 17 produced PNGs were directly opened;
their JSON caption manifest contains exactly 17 PNG keys, every key exists, and the plot tree contains
exactly 17 PNGs. The read-only inventory/count assertion exited 0. Each metadata record reports two
models and two contributing models for ssp245. The coverage figure names GFDL-ESM4 and INM-CM4-8,
each with one historical and one SSP2-4.5 member; family labels do not imply independence.

Image paths are relative to data/climate/projections/cmip6/plots/:

| Folder | PNG filename after cmip6_ prefix |
|---|---|
| full_period/ | ensemble_coverage_basin_avg.png |
| same | precip_annual_anomaly_ts_basin_avg.png, temp_annual_anomaly_ts_basin_avg.png |
| same | precip_annual_overview_basin_avg.png, temp_annual_overview_basin_avg.png |
| period_2036_2065/ | precip_monthly_clim_basin_avg.png, temp_monthly_clim_basin_avg.png |
| same | precip_monthly_change_pct_box_basin_avg.png, temp_monthly_change_box_basin_avg.png |
| same | temp_annual_seasonal_change_box_basin_avg.png |
| same | precip_annual_seasonal_change_pct_box_basin_avg.png |
| same | precip_annual_seasonal_change_abs_box_basin_avg.png |
| same | temp_annual_seasonal_sd_ratio_box_basin_avg.png |
| same | precip_annual_seasonal_sd_ratio_box_basin_avg.png |
| same | precip_annual_seasonal_cv_ratio_box_basin_avg.png |
| same | precip_temp_annual_change_cloud_basin_avg.png |
| same | precip_temp_annual_monthly_sign_agreement_basin_avg.png |

The images and captions consistently identify analysis reference WY 1985-2014 and future WY
2036-2065. Change captions explicitly distinguish the configured CSV horizon mid (reference
2000-2014, future 2046-2054); those configured windows must not be substituted for the figure windows.
Annual trajectories show the full loaded series. Anomaly trajectory captions identify the dashed
current-year line; overview captions identify the different 2014.5 historical/scenario divider.

Precipitation annual totals use mm/year, seasonal/monthly rates mm/day, relative changes percent,
temperature levels/changes degC, and SD/CV ratios dimensionless. Labels, Jan-Dec ticks, seasonal
panels, zero/unit reference lines and SSP2-4.5 legends remain legible with no observed clipping.
The two-point annual cloud agrees qualitatively with the sign grid: temperature +2/2 and precipitation
+1/2 annually. All temperature months show +2/2; precipitation changes and agreement vary by month.
These are visible consistency observations, not a rerun of the scientific reduction algorithm.

Captions distinguish member-range overview envelopes from equal-model reductions, say members are
averaged first where applicable, and explicitly reject confidence-interval or probability readings.
With two models, capped ranges and medians are drawn without IQR boxes (threshold at least 10 models).
Variability captions state detrending and geometric within-model ratio reduction, zero excluded
degenerate ratios and zero zero-future ratios. Sign-agreement captions explain k/n and dependence.
This limited two-model, one-scenario ensemble cannot establish full projection uncertainty.

Two conditional products are explicitly not produced: the annual member-ratio box (no model has two
eligible member ratios), and the multi-period cloud (fewer than two distinct windows). Their absence
is disclosed in figure_captions.md and is not missing required output for this case. Dense-ensemble,
multi-member and multi-window behavior remains prior accepted evidence, not fresh rapid coverage.

WF2 bounded shared-helper caption/visual verdict: pass. No fresh WF2 scientific recomputation or
observational model validation was performed. Final acceptance here concerns preserved scientific
map behavior and honest, usable affected figure outputs. It does not quantify observational,
parameter, structural, internal-variability or scenario uncertainty, nor authorize physical forecast
claims. All-five execution/provenance, route/repair/cost evidence and local landing remain coordinator
responsibilities; no unresolved new source/forcing-map or WF2 rendering defect was found.
