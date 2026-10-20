# Plot integration acceptance evidence — 2026-10-08–09

This record preserves the reported WF0/WF2 plotting and subsequent WF1 acceptance evidence.
It was condensed on 2026-10-20 without rerunning calculations, tests or rendering. Results apply
to the named historical candidates and inputs, not automatically to the current toolbox.
Current plotting guidance belongs in [toolbox-plot-style.md](../../../reference/toolbox-plot-style.md).

## Provenance and recovery

The complete original narrative is recoverable with:

```text
git show 53d07f52:dev/records/reviews/plot-improvements/verification.md
```

The same commit retains the original `dev/records/reviews/plot-improvements/evidence/` directory:
six `project_config_rapid*.yml` files and `config-hashes.json`, workflow run records,
`wf2-analysis-record.json`, `wf2-figure-captions.json`, inventories, gate receipts and complete logs.
The old path migration is `dev/records/reviews/plot-improvements/migration_plot_paths.md` at that commit.
These historical configurations and output layouts are not current instructions.
Referenced untracked scratch outputs are not guaranteed recoverable through Git.

Environment: Windows 11, Pixi default, Python 3.12.13, pytest 9.0.3. The WF1 record additionally
identifies Matplotlib 3.11.0, xarray 2026.4.0 and hydromt_wflow 1.0.2. Lock SHA-256:
`797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.

## WF0/WF2 integration

The initial reviewed branch started at `594b4bc0`; final figure candidate was `001b958c`.
Scope covered terminal graphics, captions, inventories and displayed statistical reductions.
Retained climate calculations were required to remain unchanged; WF1/WF3/WF4 runtime consumers
were outside this batch.

Fresh rapid used ERA5/CHIRPS, historical 2000–2016, two CMIP6 models, one SSP and one future window.
Only the project root was redirected to scratch; WF2 captioned figures were enabled.
The copied root configuration SHA-256 was
`61d7f7613f5d7be18d418943d92c0536b85bb07a95d556a98a2f5283488344d8`.
Rapid did not cover unequal member counts, multiple SSPs/windows, the ten-model IQR threshold or
optional subbasin figures; separate retained and synthetic cases covered those claims.

The larger case used read-only `wf0-lab/outputs/wf2/gabon-ntoum-dev-ensemble` tables:
13 models, 25 members, four SSPs, 2036–2065 relative to 1985–2014.
[gabon-inputs.json](gabon-inputs.json) preserves the nine input paths and SHA-256 values, checked
before and after rendering. The adapter mapped identity and agreement fields, resolved existing family
metadata, and rebuilt an unsmoothed model envelope from `c3_model_trajectories.csv`.
It did not use the lab's smoothed fan. Explicit lab-render availability was not treated as proof of
production availability.

Numerical evidence:

- Matched synthetic main/candidate inputs produced 187 change rows with maximum absolute difference
  zero, including change tables, model changes and member ratios.
- An independent weighting oracle used model A ratios 1 and 9, giving geometric mean 3, and model B
  ratio 1. Their equal-model median was √3; the member-count-weighted alternative was rejected.
  Exact retained results are in [numerical-results.json](numerical-results.json).
- Intentional graphical estimands differed: annual overview member summaries, trajectory equal-model
  medians, and geometric member/equal-model variability summaries. The documented seasonal
  precipitation rate-versus-lab-total exception was unchanged.
- Boundary checks covered an empty historical-only scenario tail, multiple windows, annual gaps and
  ACF confidence limits. For ten pairs, ±1.96/√pairs ≈ ±0.619806 must not be clipped at ±0.5.
- A small-ensemble sign-agreement canvas needed a 90 mm minimum width; the four-SSP canvas was unchanged.

Fresh WF0 completed 11 jobs and WF2 13. Optional WF0 renders had CHIRPS 25 ordinary + 25 captioned,
comparison 25 + 25 and ERA5 33 + 33 PNGs; caption paths covered all 166 files. Ordinary subbasin
counts were respectively 8, 8 and 12. WF2 had 17 ordinary + 17 captioned products, with two explicit
unavailability reasons: one member per model and one future window. Gabon had 18 + 18 products;
its combined cloud was unavailable because it had one window. Availability, captions and actual files
agreed. All ordinary WF0/WF2/Gabon products, optional contact sheets and synthetic edge cases were
reported visually inspected. WF2 rendering was explicitly forced after an imported-helper change.

Eleven optional production/lab parity checks lacked their expected input tree and were skipped.
Synthetic parity and retained Gabon rendering did not replace that missing parity claim.

### Coordinate tolerance and software outcome

The initial fast-gate failure reproduced with main's validator against the same existing fixture:
`snapped_y` differed by about `7.1e-15` degrees. The approved correction allowed absolute tolerance
`1e-12` degrees, relative tolerance zero, only for `snapped_x`/`snapped_y`. Other numeric attributes,
dtype, identity and missingness remained exact; geometry retained its separate tolerance.
All 31 spatial tests passed, including rejection of `2e-12` drift, finite/missing or finite/infinite
mismatches, and tiny changes to other attributes. No stored output or workflow calculation changed.

Candidate `d1a2ad02` passed fast: 4007 passed, 17 skipped, one expected failure.
Landing candidate `c7b47b34a3c1b050158e7926f43f6483a82232d6` repeated those totals in 184.97 seconds.
Its tree was `cd30cd5cf276f5b60a0d420ecb23ae15f86e668d`; local merge `566abca4` passed tree-equality
and ancestry checks. The landing log SHA-256 was
`b1ceb8828abfa33fbbd379eea455fd420b4b9cc76802c775a26e07ecf22dd23e`.
The 17 skips were five Linux-only controls, eleven absent-input parity cases and one separately
opt-in integration test; the xfail was the known HydroMT catalog round-trip defect.
Lint and format checks passed. This terminal-figure batch did not claim all-five execution.

## WF1 acceptance

WF1 used read-only `cst-cases/runs/sp2-liberia/active/` inputs.
The forcing `models/hydrology/wflow/forcing/inmaps_historical.nc` SHA-256 was
`56b1213999320c9968cd9e7ee6840d207380bcce3d1e6e0bc4950f8650a04e1d`.
It contained 231 × 223 cells, 20,983 basin cells and 6,209 days, 2000-01-02 through 2016-12-31.
The rapid configuration identity for focused DAG checks was
`ba8d72cbc0d178188b3309483e5fe1effc48b61e1343160848b5d63bc39013bd`.

### Forcing and station hydrographs

Forcing candidate `8a2ebccb` used full years 2001–2016, excluding partial 2000, and shared WF0
completeness, Sen trends and mean/p10–p90 monthly summaries. The precipitation trend changed
intentionally from approximately −151 mm/decade (OLS) to −183 (Sen).
A nine-year synthetic temperature outlier case gave Sen 10 °C/decade versus OLS above 50.
Independent quantile and cellwise WF0 checks covered tolerated/excessive gaps and non-January years.
Three numerical tests and 51 related focused tests passed; nine forcing plots, six WF0 source
plots and an annual comparison were rendered and inspected. Underlying forcing was unchanged.

Station candidate `c7ddb673` used eleven retained five-decimal `output_q.csv` series because native
`output.csv` was absent. This was a plotting comparison, not native-precision hydrological validation.
After the adapter's first-year exclusion, daily support was 2001-01-02–2016-12-31.
Partial 2001 was excluded from annual summaries, leaving 2002–2016; January 2001 was excluded
from monthly climatology while other complete months remained independently eligible.

Analytical checks covered omitted leap days, paired dates, negative exclusion, partial periods,
equal-weight monthly means, valid-day Weibull ranks, zero-flow mass, a positive `1e-8` tail,
all-zero/disjoint series and rejection of sixteen distributed missing days per year.
The predecessor retained the partial year and hid the small positive tail. Eleven real before/after
pairs and a synthetic paired example were rendered; selected real/synthetic figures were inspected,
and every real caption stayed inside its canvas. All 49 focused tests passed.

### Basin summaries and performance

Basin candidate `75183c20` reconstructed native model-cell means from disjoint subcatchment counts
(20,983 Liberia cells), not physical-area weights. Every zone required finite daily support;
missing zones did not trigger weight renormalization. Checks covered unequal/absent zones,
leap dates, full boundary periods, three missing days per month/fifteen per year, negative recharge,
flux gap-adjusted totals versus rate/state means, snow water-depth means, Sen trends and
equally weighted eligible-month p10–p90 bands.

Four Liberia basin and 44 optional individual figures were rendered, plus ten synthetic figures
covering all five quantity types. Six independent acceptance cases and 91 focused tests passed.
The four standard basin renders and an individual recharge example were reported inspected.

The subsequent performance revision used concurrent finite, nonnegative daily discharge pairs for
scatter, cumulative volume and exported metrics; monthly means used those same pairs.
Missing days interrupted both cumulative curves without filling; undefined scores stayed NaN in CSV
and appeared as dashes. Squared Pearson correlation remained metadata rather than a displayed score.
Five complete/gapped/zero/disjoint cases were rendered. An independent complete-record probe preserved
all 14 original metrics and CSV shape within `1e-12`. Final focused checks passed 48 tests.
Later removal of temporary figure-only checks left 32 existing/numerical tests passing;
the removed checks are recoverable from the historical revisions.

### Integrated outcome and limits

The approved WF1 batch candidate was `8eb326cd`; integrated final candidate was
`929cfdc6d38f47201ad6a8acd2b402acf414123a`. Lint, format and the full suite passed:
4086 tests, 17 skips, one known upstream xfail, 8645 warnings.
Skipped categories matched the earlier Linux/local-parity/opt-in integration limitations.
Plotting DAG, retained inventory and independent basin/metric probes passed.
No all-five execution or baseline validity was claimed.

Nine integrated forcing figures were regenerated with the historical-grid frame. Independent
edge assertions checked west −10.625°, east −8.375°, south 6.625°, north 9.125°; all three
maps were visually inspected. Six WF0 source figures and an annual comparison were regenerated.
The integrated rendering changed no forcing, interpolation or simulation calculation.

A fresh WF1 rebuild was attempted but stopped during unrelated global basin-index reading;
no complete fresh WF1 execution was established. Acceptance rests on the retained-input renders,
numerical probes and software/DAG checks stated above. The original record describes the final
integrated candidate and preparation for managed landing, not proof of its subsequent landing.
