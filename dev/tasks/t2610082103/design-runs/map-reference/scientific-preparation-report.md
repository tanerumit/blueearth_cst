# Source-map preparation scientific checkpoint

**The new source-preparation helper preserves the tested native scientific fields exactly.**
Real-data comparisons and actual helper calls for unit, availability and auxiliary-field cases pass.
This checkpoint does not accept the unfinished reference producer, contribution filter or consumers.

Approved design: SHA-256 `4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
Helper tested: `source_map_fields.py`, SHA-256
`cd7e679e54c06117e6e062ad4c1aa2cb227f268f5aafd5c845c2f1c132478db0`.
All commands executed on 2026-10-10 in the session Pixi environment. Source, lock, catalog, extraction,
basin-cell, retained-output and fixture fingerprints are retained in the phase logs and the additional
fingerprint log. No production code, Git state, installation, workflow or external transmission changed.

## Real native-grid comparisons

The assertions use `xarray.testing.assert_identical`, comparing complete datasets: scientific values,
valid-year counts, unavailable masks, coordinates and variable/dataset attributes. No numerical tolerance,
common-year intersection, regridding or field subsampling was used for these retained comparisons.
Each original extraction and basin-cell file was checked against its own retained metadata's SHA-256
before preparation. Liberia's original inputs/catalog were used for Liberia; rapid inputs were not
substituted.

| Matched case | Native grid | Daily span | Eligible annual counts | Result |
|---|---|---|---|---|
| Fresh rapid ERA5 | 2 × 3 | 2000-01-01–2016-12-31 | 17 everywhere | Exact, all 9 arrays |
| Fresh rapid CHIRPS | 5 × 6 | 2000-01-01–2016-12-31 | 0 or 17 | Exact, all 3 arrays |
| Retained Liberia ERA5 | 10 × 9 | 2000-01-02–2016-12-31 | 16 everywhere | Exact, all 9 arrays |
| Retained Liberia CHIRPS | 40 × 39 | 2000-01-01–2016-12-31 | 17 everywhere | Exact, all 3 arrays |

ERA5's nine arrays are precipitation, temperature, source PET, their three counts and three unavailable
masks. CHIRPS's original retained Liberia extraction contains only precipitation; its three arrays remain
precipitation-only. ERA5's incomplete first Liberia calendar year correctly does not contribute.
Fresh rapid CHIRPS retains 29 finite cells and one unavailable cell, with their exact masks and counts.
All 1,560 CHIRPS cells and all 90 Liberia ERA5 cells were checked, with no spatial or temporal omissions.

Both ERA5 cases used the exact configured catalog DEM:
`P:/wflow_global/hydromt/meteo/era5/meta/era5_orography_2018.nc`, SHA-256
`77aa8f51a556ac21155dcd58636c4d58167b43bbb6a76beb36b2b84b1e74612f`.
Authorized read-only escalation was needed for that mirror. The exact returned PET arrays match the
captures; no claim is made that source-grid PET equals model PET. Historical DEM-byte immutability is
not independently recorded in the old Liberia metadata; current DEM bytes and exact reproduced outputs
are the evidence available here.

## Actual unit and PET gates

These controlled cases use all six cells of the fresh ERA5 grid for calendar year 2001 only: 365 daily
values per cell. The other 16 years are deliberately omitted from these gate probes, while the complete
17-year preparation was separately compared above. New-helper results were compared exactly with the
unchanged old compute module's map-preparation branch. That branch was extracted with Python AST and
executed verbatim except that its final NetCDF write was replaced with an eager load. No workflow ran.
The old compute source hash is
`77b1e09d8280fb2d51e29aae6abe604ee060fa074495daa30cb9772cb6276530`.

| Controlled case | Expected behavior | Executed result |
|---|---|---|
| Existing K label, catalog −273.15, region fingerprint | Already Celsius; no second conversion | Exact match |
| Same numbers labeled degC | Same scientific fields as normalized legacy K | Exact match |
| Unknown units | Temperature/PET NaN, count 0, unavailable; precipitation preserved | Pass |
| K without region fingerprint | Same suppression | Pass |
| K without catalog temperature offset | Same suppression | Pass |
| All temperature values 71 degC | Same suppression | Pass |
| Missing required `kin` | Fail preparation | `KeyError: 'kin'` |

The legacy/celsius equality checks all nine arrays, so a hidden second subtraction of 273.15 or an altered
PET path cannot pass. Suppression cases independently assert NaNs, zero counts and unavailable masks,
and require unchanged precipitation. Their expected warning lineage is retained in the logs.

## CHIRPS auxiliary preservation

The actual rapid CHIRPS extraction is enriched: 7 × 8 native cells with borrowed temperature and
radiation/pressure fields. It has **no raw PET variable**. For all 56 cells in 2001, the helper exactly
preserves old preparation's precipitation and temperature arrays/counts/masks. Precipitation is finite
in 53 cells, with counts 0 or 1; auxiliary temperature is finite in all 56, with count 1. Source identity
still returns `carries_temp("chirps") == False`; auxiliary presence does not change that identity.

A precipitation-only variant of the same extraction retains only the three precipitation arrays and
matches the old branch exactly. The separate full Liberia case supplies an actual unenriched CHIRPS
store, so this controlled variant is not misrepresented as independent real data.

Since the real enriched store has no PET, a separate, explicitly synthetic raw auxiliary was added as
half of its daily precipitation solely to test preservation. All nine resulting arrays match the old
branch exactly; 53 finite PET cells retain counts 0 or 1 and the corresponding unavailable masks. This
synthetic auxiliary is **not a PET estimate** and offers no evidence of PET physical validity.
The new reference producer must still prove that both CHIRPS variants contribute only precipitation;
this checkpoint establishes preserved source preparation and source-role identity, not final pooling.

## Evidence and limits

Executable: `scientific-preparation-probe.py`. Phase logs:

- `scientific-preparation-fresh.log`: fresh ERA5 exact comparison.
- `scientific-preparation-fresh-chirps.log`: complete fresh CHIRPS exact comparison.
- `scientific-preparation-liberia.log`: complete original-input Liberia comparisons.
- `scientific-preparation-gates.log`: old-branch parity, units/PET gates and CHIRPS variants.
- `scientific-preparation-auxiliary.log`: explicit synthetic raw auxiliary PET preservation.
- `scientific-preparation-fingerprints.log`: additional source/catalog/fixture/original-input identities.

Commands (each phase redirected to its corresponding complete log):

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py fresh
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py fresh-chirps
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py liberia
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py gates
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py auxiliary-pet
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py fingerprints
pixi run ruff check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py
pixi run ruff format --check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-preparation-probe.py
```

All six phases exit 0; final targeted Ruff lint and format checks pass.
Earlier scratch lint found import ordering after the intentional
repository-path setup; specific E402 exemptions and formatting resolved it. No permanent tests were added.
The earlier independent annual known-answer oracle remains separate and unmodified. Scope is targeted
checkpoint verification; numerical claims are affected. Parent-owned combined gates remain outstanding.

The tested preparation extraction is scientifically behavior-preserving for these matched stores and
controlled gates. This is neither observational validation of ERA5/CHIRPS nor validation of de Bruin PET:
it estimates no observational, parameter or structural uncertainty. Native fields and auxiliary records
are retained correctly; pooling support, classes, producer identity, reporting metadata, renderer meaning
and integrated WF0/WF1 products still require their own acceptance evidence.
