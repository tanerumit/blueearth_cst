# P1 forcing-unit trace

Status: current ERA5 binding accepted by named model-validator; metadata hold discharged.
Date: 2026-09-10. P0 snapshot remains unchanged and accepted.

## Executed code path

1. `config/catalogs/deltares_data.yml`, `era5.data_adapter`, renames native
   variables and applies `temp/temp_min/temp_max += -273.15`,
   `press_msl *= 0.01`, and `kin/kout *= 0.000277778`. Precipitation has no
   conversion in this daily-data entry. Preserve the exact radiation coefficient;
   replacing it with a rounded or rational alternative would be a numeric change.
2. `extract_historical_climate.py` reads via `DataCatalog.get_rasterdataset`.
   Installed HydroMT 1.3.1 `RasterDatasetAdapter.transform` applies the configured
   arithmetic before metadata. `_apply_unit_conversions` explicitly copies the
   original variable attributes back after computing `da * m + a`; the selected
   source metadata supplies no replacement variable-unit attributes.
3. Installed weathergenr 2.0.0 `read_netcdf` reads with `ncdf4::ncvar_get`, masks
   missing values, reshapes and optionally rounds; it does not interpret physical
   unit strings. `generate_weather.R` constructs each root by indexing these
   already-converted historical arrays with `day_order`.
4. weathergenr `write_netcdf` copies `units` from the historical template into
   each variable definition, while writing the supplied numeric arrays (with
   configured significant-digit rounding). Thus it preserves the stale Kelvin,
   Pascal and radiation attributes while retaining the converted values.
5. `impose_climate_change.R` uses the same reader and writer. Its existing
   transform adds the configured temperature delta to temperature/min/max and
   applies the configured precipitation transformation. It does not apply a
   Kelvin, pressure or radiation unit conversion.
6. `prepare_climate_data_catalog.prepare_clim_data_catalog` removes the inherited
   `data_adapter` for generated files. Existing downscaling therefore reads
   converted values without applying the source arithmetic twice.
7. HydroMT's `meteo.temp` documents Celsius input and performs lapse correction
   and reprojection, then sets singular `unit="degree C."`. `meteo.pet` documents
   Celsius, hPa and W/m² inputs, computes PET using the existing method, and sets
   `unit="mm"`; `meteo.precip` likewise sets `unit="mm"`. The source uses singular
   `unit` for these results rather than clearing all inherited plural `units`.
   These explicit operations and caller contracts establish the intended adapter
   interpretation; value ranges are only a diagnostic and are not its basis.

## Public-adapter witness

A two-time, two-by-two synthetic raster was passed through the installed public
`RasterDatasetAdapter.transform` with the actual ERA5 catalog adapter and metadata.
Exact configured arithmetic and unchanged original `units` were asserted for all
seven variables. The probe passed:

| Native input | Converted value | Retained label | Binding interpretation |
|---|---:|---|---|
| temperature 300 K | 26.850000000000023 | K | °C |
| minimum 295 K | 21.850000000000023 | K | °C |
| maximum 305 K | 31.850000000000023 | K | °C |
| pressure 101300 Pa | 1013 | Pa | hPa |
| incoming radiation 720000 | 200.00016 | J m**-2 | W/m² under the existing daily ERA5 catalog convention |
| outgoing radiation 1440000 | 400.00032 | J m**-2 | W/m² under the same convention |
| precipitation 5 | 5 | mm d**-1 | mm/day, daily input to existing preparation |

The command was `pixi run --as-is python
.tmp/scratchpad/2026-09-10_2046/probe-unit-conversions.py`; its retained session
log is `probe-unit-conversions.log`. Installed function bodies were inspected
read-only using Python `inspect.getsource` and R namespace function printing;
scratch logs `trace-units-python.log` and `trace-units-r.log` retain that inspection.
No upstream package, numerical file, catalog or conversion was modified.

## Binding proposal and limits

Represent effective units separately from verbatim native attributes, with an
explicit versioned source/preparation interpretation and its provenance. The
descriptor must not silently prefer singular `unit`, plural `units`, or a value
range. For this verified ERA5 path, retain the existing conversion exactly once
and keep prepared daily temperature in °C and precipitation/PET in mm per step.
Preserve the existing calendars, clipping and endpoints independently of units.

This is preservation of the established catalog/preparation contract, not a new
assessment of the original ERA5 aggregation or the physical adequacy of PET.
Other source/catalog bindings need their own explicit evidence; this trace does
not authorize an unregistered source to inherit the ERA5 interpretation. Any
new conversion or numerical metadata repair remains a separate method decision.

## Named model-validator review

**ACCEPT — ERA5 binding interpretation; metadata hold discharged on 2026-09-10.**
Reviewer: `model-validator` (`/root/model_validator_p0`). This discharges the
unit-interpretation hold in [the P0 acceptance record](p0/prechange-snapshot.md#separate-p1-forcing-metadata-disposition)
for the traced ERA5 catalog → extraction → weathergenr → existing HydroMT/Wflow
preparation path. No owner method decision is required to document this existing
binding without changing values or native metadata.

Independent review checked the actual ERA5 catalog coefficients and metadata,
HydroMT's conversion-before-metadata order and original-attribute restoration,
the R root-generation indexing and template writer arguments, the retained
installed `read_netcdf`/`write_netcdf` bodies, and removal of the generated
catalog's inherited `data_adapter`. The reviewed installed preparation code
requires Celsius/hPa/W/m² and writes temperature/PET units as described above.
This closes the missing trace: effective units follow explicit existing
arithmetic and the preparation contract, rather than an inference from ranges.

The public-adapter witness was independently rerun with the existing environment
using `.pixi/envs/default/python.exe -B
.tmp/scratchpad/2026-09-10_2046/probe-unit-conversions.py`: **passed for all seven
variables**, including unchanged native `units` attributes and the exact
`0.000277778` radiation multiplier. Direct environment invocation emitted GDAL
data-location warnings; the conversion assertions completed successfully and
no geospatial accuracy claim depends on this witness.

Acceptance applies to the following implementation constraints:

- Keep verbatim native attributes distinct from explicitly declared effective
  units. Record the interpretation's binding revision and the source/catalog
  transformation provenance; a source label alone is insufficient authority.
- Apply the existing source arithmetic exactly once. Generated forcing already
  carries converted values; the simulator must not apply those conversions again
  because it encounters stale native labels.
- Retain the established prepared-variable interpretation: temperature in °C,
  precipitation/PET in mm per daily step. Preserve the existing calendar,
  clipping, timestep and endpoint operations independently.
- Refuse an unverified binding or a mismatch with the recorded provenance rather
  than borrowing this interpretation for another source or silently defaulting
  metadata. This review supplies no blanket acceptance for ERA5 catalog variants,
  CHIRPS, E-OBS or arbitrary external generated artifacts.

Verification scope: `rapid`; numerical claims `unaffected` by this documentation
decision. No upstream or production code was changed, no model was rerun, and no
new tolerance was introduced. Software implementation tests and the later GF-9
numerical comparison remain necessary. This verdict accepts preservation of the
existing binding; it does not validate original ERA5 temporal aggregation, PET
physical adequacy, or the native unit labels themselves.
