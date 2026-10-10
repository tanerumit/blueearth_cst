# Scientific acceptance preparation

The existing `diagnostics.annual` and `diagnostic_maps.annual_fields` pass 11 independent supported
known-answer cases. Two deliberately unsupported 31/366 controls fail the scientific oracle exactly
as intended. This is preparation evidence only; it is **not candidate acceptance**.

Approved design SHA-256: `4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
Executed 2026-10-10 in session-1, with Python 3.12.13, NumPy 2.4.6, Pandas 3.0.3, Xarray 2026.4.0.
Exact source byte hashes appear in `scientific-oracle.log`; no Git commands were used.

## Objective and independent method

Check eligibility, calendar coverage, amount/temperature aggregation, valid-year counts and unavailable
masks before trusting their extraction into shared preparation. This is deterministic numerical
verification, not hydrological predictive validation. Calibration splits, forecast benchmarks, ensemble
uncertainty, gauge skill and parameter inference are outside this packet.

The oracle independently enumerates dates using Python's standard `datetime` and `calendar`, looks up
observations by date, calculates each monthly estimate as observed mean times calendar-month length,
and combines months into full reporting years. It never calls production reporting-year, infill,
missingness or aggregation routines to construct expected values. Each synthetic variable is observed
at four native cells; precipitation and PET use amounts, temperature uses the daily mean. Integer and
constant-value cases allow exact equality, with no adjustable numerical tolerance.

Missing dates are reindexed before the direct `annual()` call, matching its dense-calendar precondition.
The `annual_fields()` call receives the original sparse timestamps, independently checking its own
reindexing. The oracle refuses to estimate an entirely unobserved month even in the deliberately
unsupported 31-day control. That produces a discriminating scientific falsifier.

## Executed results

| Case | Month/year limits | Amount field, count, unavailable | Result |
|---|---|---|---|
| Entire 2000 leap year NaN | 27/366 and 27/1000 | NaN, 0, true | Pass |
| Entire February 2001 NaN; other days 1 mm | 27/366 and 27/1000 | NaN, 0, true | Pass |
| February has 27 NaNs and one 1-mm value | 27/1000 | 365 mm/year, 1, false | Pass |
| Complete 2001 at 1 mm/day | 0/0 | 365 mm/year, 1, false | Pass |
| Three missing days in each of five months | 3/15 | 365 mm/year, 1, false | Pass |
| Above plus one missing day in June | 3/15 | NaN, 0, true | Pass |
| Missing timestamp 2000-02-29 | 1/1 | 366 mm/year, 1, false | Pass |
| Missing timestamp 2000-02-29 | 0/0 | NaN, 0, true | Pass |
| October years with partial ends and missing leap day | 1/1 | 365.5 mm/year, 2, false | Pass |

The last case spans 1999-07-05 through 2002-02-19 and drops 2000-02-29. Independently valid full-year
labels are 1999 and 2000; respective totals are 366 and 365 mm. Partial labels 1998 and 2001 do not
contribute. Temperature is exactly 1 degC wherever its year is eligible; otherwise it is unavailable.
The February boundary case implies exactly 28 mm for February: one observed 1-mm value plus 27 values
infilled at that same observed mean. Precipitation and PET produce identical expected amount results.

### Deliberate failing controls

| Unsupported control | Scientific expectation | Actual old amount/count/mask |
|---|---|---|
| Entire leap year NaN at 31/366 | NaN, 0, unavailable | **0 mm, 1, available** |
| Entire February missing at 31/366 | NaN, 0, unavailable | **337 mm, 1, available** |

The second control also returns a false eligible temperature field of 1 degC with count 1. The first
control's temperature remains NaN/count 0. These are existing false finite amounts/eligibility under
unsupported monthly tolerances; they are not introduced regressions. The proposed monthly maximum
of 27 avoids these cases without changing the old temporal algorithm. Both 366 and 1000 annual limits
were exercised, so an unbounded annual setting cannot bypass the supported monthly guard.

Calling `full_years()` directly on sparse, unreindexed October-year data returns only label 2000;
after the required daily reindex it returns 1999 and 2000. This establishes why the preparation-side
reindex must survive the extraction. It is not a request to change the lower-level function's contract.

## Commands and verification budget

Numerical axis: affected. Packet scope: rapid targeted numerical verification within the parent's
shared-contract acceptance program. No workflow, installation, Git, network or P-drive actions ran.
The scratch script/log/report are the only owned writes. No production or permanent test files changed.

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-oracle.py > .tmp/scratchpad/shared-rendering/map-reference/scientific-oracle.log 2>&1
pixi run ruff check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-oracle.py
pixi run ruff format --check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-oracle.py
```

Oracle exit 0; 11 passing supported cases and 2 detected failing controls. Final targeted Ruff lint and
format checks pass. Earlier Ruff calls without `--no-force-exclude` inspected no files and are not
counted as validation. A preliminary lint found scratch import ordering after explicit repository-path
setup; those imports carry specific E402 exemptions. Formatting only changed scratch code after execution.
The successful execution establishes Python parse/import validity; no separate compile artifact was made.

Caller search `rg -n 'annual_fields\(' blueearth_cst` found existing WF0 compute and the newly added,
unused source-preparation module. No candidate source-preparation functions were called in this run.

## Pending candidate acceptance

Await the parent's candidate handoff before checking new preparation, reference pooling and renderer
classes. Still unexecuted: real selected/enriched versus extra/native CHIRPS role handling; exact retained
arrays/counts/masks including auxiliaries; Celsius and catalog-normalized legacy K gates; PET input
failure; unequal/native-grid intersection extrema; final upper class endpoint and adjacent floats;
producer identity and reporting metadata; invalid setting guards; integrated pre/post products.
Full workflows, retained-output parity, visual inspection and combined software gates remain with root.

The existing temporal path is adequate for these tested, ordered Gregorian daily synthetic cases within
the approved monthly range. This evidence does not establish scientific quality of any forcing product,
derived PET, model simulation or future climate response, and quantifies no observational or structural
uncertainty. The unfinished map-reference candidate has no scientific acceptance verdict yet.
