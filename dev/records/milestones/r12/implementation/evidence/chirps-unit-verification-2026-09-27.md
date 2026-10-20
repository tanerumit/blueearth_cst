# CHIRPS unit verification — 2026-09-27

Historical evidence relocated from the weather-generator reference at commit ed406a81.
This preserves the reported measurements; the relocation did not repeat the experiment.
Current requirements: [forcing units](../../../../../reference/toolbox-forcing-units.md) and
[weather-generator interface](../../../../../reference/toolbox-weather-generator-interface.md).

### CHIRPS closure evidence (2026-09-27)

The original 2026-08-16 CHIRPS store failed WG-1 on eight counts: float64
coordinates and temperatures, missing `crs`/`category`, and precipitation
labelled `mm`. Fetching a DataArray and calling `to_dataset()` lost the catalog
metadata. Commit `33bf0ef` moved metadata stamping and float32 coercion to the
shared write path so both `chirps` and `chirps_global` receive the fix. The rapid
hybrid store subsequently retained all seven variables, float32 coordinates
and values, and the catalog citation block; only the precipitation label failed
WG-1 before the label correction.

The magnitude witness compared raw `CHIRPS_rainfall_2000.nc` with the retained
`chirps_20000101_20161231/extract_historical.nc` in `test_case/test_rapid`:
366 daily records × 56 cells = 20,496 values, with 9,553 nonzero values. After
the catalog's `unit_add: {time: 86400}` timestamp shift, the source values cast
to float32 matched the store exactly (maximum absolute difference 0). Controls
using unshifted dates, multiplication by 86400, or division by 86400 failed.
The catalog performs no precipitation-value conversion. This establishes a
label discrepancy for this daily binding, not a magnitude defect. The official
[CHIRPS daily product description](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)
also records a one-day cadence and precipitation in mm/d.

The producer normalizes the verified CHIRPS `mm` label to `mm d**-1` without
scaling values or altering timestamps. A fresh one-year comparison-only
extraction from the staged catalog was also checked against the retained hybrid
over the same dates: all 20,496 precipitation values were identical. Its only
six WG-1 diffs were the intentionally absent ERA5 companion variables; its
catalog citation block survived. The retained full hybrid cleared WG-1 after
the label helper was applied in memory, without writing that retained file.
The comparison report smoke retained every diff in both CSV and Markdown.

Existing stores require regeneration
to obtain the repaired label; changed file metadata changes content hashes,
so downstream generation identities can change even though historical values
do not. The magnitude witness is local CHIRPS evidence; tests cover the shared
`chirps_global` path without claiming a real global-source run.
