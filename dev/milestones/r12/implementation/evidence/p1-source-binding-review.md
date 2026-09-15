# P1 existing-source binding review

Date: 2026-09-10. Reviewer: `model-validator` (`/root/model_validator_p0`).
Scope: read-only source/unit/preparation trace for existing CHIRPS and E-OBS
branches. This supplements the accepted [ERA5 trace](p1-forcing-units.md).

## Decision

**ACCEPT the code-derived CHIRPS and `chirps_global` hybrid interpretation for
preserving their existing declared pipeline.** This authorizes an explicit,
versioned binding with source/catalog/ancillary provenance, not an ERA5-only
source-name gate. It does not establish empirical old/new numerical equivalence
for those sources; the P0/rehearsal numerical evidence covers ERA5 only.

**E-OBS complete generation binding is not accepted.** Current WF1 explicitly
rejects `eobs` at parse time; `tests/test_cli.py` pins that refusal. The presence
of a dormant Makkink selection in the preparation helper does not establish
end-to-end support. Preserve that helper behavior and the existing support
boundary; there is no need for a new owner decision to retain them.

| Binding | Effective interpretation | Evidence and limits |
|---|---|---|
| `chirps` precipitation | mm per daily input interval; no physical scaling; source timestamps shifted +86,400 s exactly once during extraction | Actual catalog and installed adapter; staged African-source NetCDF header has `precipitation.units=mm` |
| `chirps_global` precipitation | Same declared precipitation/time interpretation, with its own source/catalog provenance | Same extraction branch and catalog operations; no global-source NetCDF is staged locally, so actual file metadata/coverage must still be checked |
| Both CHIRPS paths' six auxiliaries | Temperature/min/max in °C; pressure in hPa; incoming/outgoing radiation in W/m² under the existing ERA5 daily catalog convention | ERA5 catalog conversions occur before the hybrid grid is assembled; no additional unit conversion is introduced |
| Both CHIRPS paths' model preparation | Existing De Bruin PET; prepared temperature °C and precipitation/PET mm per daily model step | Existing HydroMT/Wflow contract; source-grid elevation sidecar is required for the second preparation stage |
| E-OBS | No complete forcing interpretation accepted here | WF1 refusal; incomplete generation-variable catalog; no staged NetCDF metadata or numerical execution evidence |

## Trace and preservation requirements

`blueearth_cst/climate_analysis/extract_historical_climate.py` owns extraction.
Its explicit `chirps`/`chirps_global` branch reads precipitation through that
source's catalog adapter, normalizes grid-dimension names, then reads six
auxiliaries through the `era5` catalog adapter. The source catalog entries in
`config/catalogs/deltares_data.yml` rename `precipitation` to `precip`, shift
`time` by 86,400 seconds and specify no physical precipitation conversion.
The source/ERA5 window intersection is preserved; it must not be replaced by
padding, extrapolation or an assumed common window.

The already-converted ERA5 pressure and radiation fields are reprojected to the
CHIRPS grid by `nearest_index`. Temperature/min/max are lapse-corrected using
the existing HydroMT `meteo.temp`, ERA5 source orography and the configured
hydrography DEM averaged onto the CHIRPS grid. The latter DEM is retained as the
extraction's declared orography sidecar. These spatial operations preserve the
established unit interpretation while changing values through the existing
downscaling method; this review does not authorize modifying them.

Unchanged R generation reorders the extracted arrays, and unchanged perturbation
adds the declared temperature change and transforms precipitation. The previously
reviewed weathergenr reader/writer retains native attributes without performing
physical-unit conversion. CHIRPS hybrid native labels may therefore differ among
variables because some fields retain ERA5 attributes while temperature has passed
through `meteo.temp`. Retain the observed attributes; do not assume their exact
strings equal those of an ERA5-only artifact.

`prepare_climate_data_catalog.prepare_clim_data_catalog` removes inherited
adapters for generated forcing. That prevents both reapplying physical source
conversions and shifting generated timestamps by another day. For the CHIRPS
branches it requires the explicit `oro_path` and registers the existing local
sidecar as `<source>_orography`. Current downscaling selects De Bruin for both
CHIRPS names. The successor must carry the resolved reader, PET settings and
sidecar through preparation context rather than recover them from scenario
meaning or substitute ERA5 source elevation.

`tests/test_climate_parity.py` contains an analytical example of the CHIRPS
extraction-to-model temperature correction and a wrong-DEM sensitivity case.
Their code was inspected, not rerun: they demonstrate why a matching sidecar is
part of the binding. This is not new empirical CHIRPS simulation evidence.

Acceptance requires interpretation provenance that identifies these existing
source/catalog/extraction operations and the ancillary artifact. An arbitrary
file named `chirps` cannot inherit the interpretation. Actual required variables,
physical metadata, grid/ancillary compatibility, calendar, timestep, coverage and
missingness remain subject to the accepted compatibility checks. Missing or
contradictory evidence must refuse explicitly; it is not permission to default
units or invent a conversion. Source availability or staging defects are runtime
limitations, not grounds for deleting the existing supported CHIRPS bindings.

## E-OBS boundary

`build_model.smk` contains the explicit `clim_source == "eobs"` rejection,
with supported sources listed as ERA5, CHIRPS and `chirps_global`.
`tests/test_cli.py::test_eobs_config_fails_wf1_dry_run_at_parse_time` protects it.
The current E-OBS catalog renames only `pp`, `qq`, `rr`, `tg` to pressure,
incoming radiation, precipitation and temperature, and shifts time by one day.
Generic extraction additionally requests `temp_min`, `temp_max` and `kout`;
there is no E-OBS extraction branch supplying them. R generation/perturbation
also uses temperature minima/maxima. Makkink's narrower model-input requirement
does not resolve that upstream completeness gap.

The installed HydroMT/Wflow Makkink contract requires temperature in °C, pressure
in hPa and incoming radiation in W/m², but this is a consumer requirement, not
proof that a particular E-OBS artifact satisfies it. No E-OBS NetCDF files were
found under the resolved configured local staging directory. Accepting a future
complete E-OBS path would need actual input-variable/unit/coverage evidence,
explicit handling of the existing generation requirements, and a decision to
expand the current WF1 support boundary. No such expansion is part of this
review or required for P1 preservation of the supported sources.

## Checks and limitations

Using the existing Python environment, a two-time, 2 × 2 raster with known
precipitation values was passed through installed
`RasterDatasetAdapter.transform` separately with the actual `chirps` and
`chirps_global` catalog adapters/metadata. Both passed: canonical rename,
unchanged value 5 and `units=mm`, and exactly +86,400 seconds. The resulting
timestamps differ from the unshifted control. No source or generated file was
written by this witness.

Read-only header inspection of staged
`C:/data/wflow_global/hydromt/meteo/chirps_africa_daily_v2.0/CHIRPS_rainfall_1990.nc`
found `precipitation.units=mm` and a `proleptic_gregorian` time axis. No NetCDFs
were found in the configured E-OBS or CHIRPS-global staging directories. This
single header is metadata evidence, not a record-length or quality assessment.
Direct environment invocation emitted GDAL data-location warnings; the adapter
assertions and header reads completed successfully.

Verification scope: `rapid`, numerical claims `unaffected` by this binding-review
document. Production code, catalogs, source datasets, P0 outputs and the standing
baseline remained read-only. No non-ERA5 generation, Wflow simulation, numerical
equivalence comparison, model-skill assessment or uncertainty interval is claimed.
The next simulator handoff must distinguish this code-supported interpretation
from the separately executed ERA5 preservation evidence.
