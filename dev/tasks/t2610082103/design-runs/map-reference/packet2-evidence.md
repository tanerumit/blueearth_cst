# Packet 2 — shared producer and current-byte provenance

Owned only `blueearth_cst/shared/map_reference.py`, `produce_map_reference.py` and purpose-named scratch.
Existing climate-store factory and active workflow consumers unchanged. No Git operations or full runs.

## Usable interfaces

`historical_map_reference_rule(*, project_dir, model_region, climate, data_sources, region_geojson,
basin_geojson, m0, hydrography=DEFAULT_HYDROGRAPHY, basin_index=DEFAULT_BASIN_INDEX)` returns
`HistoricalMapReferenceRule.script/inputs/outputs/params/source_specs`. The output key is `reference`.
Factory params are executable source-spec dictionaries, `selected`, `m0`, `completeness`, `shared_inputs`,
preparation/reference code digests, current environment and policies. Store files need not exist at parse;
the qualified static local catalog-backed ERA5 DEM does. All executable paths use forward slashes.
Extra stores use exact WF0 flags: minimum years only for selected; forcing required for selected or
non-CHIRPS sources. The selected-store factory contract is unchanged.

`source_map_inputs(spec)` is the identical per-source climate/cell/catalog/optional-sidecar/concrete-DEM/
preparation-code/lock input set for WF0 compute and reference/adapter dependencies.
`source_spec_dict` / `source_spec_from_dict` carry executable specs, never semantic absolute paths.
`reference_arguments(factory.params)` creates the clean `specs/selected/m0/completeness/shared_inputs`
kwargs for `build_reference`, `validate_reference`, `load_reference` and `publish_reference`.

WF0 consumer params agreed with root: `map_source_spec`, `map_completeness`, `preparation_code_digest`,
`map_environment`. WF0 and WF1 renderer params: `map_reference_params=dict(factory.params)`.

`preparation_identity(spec,m0,completeness)` snapshots current consumed bytes, dates/full reporting labels,
original units, roles, code closure and qualified loaded environment. `seal_fields(fields,expected)`
computes actual payload identity and sets the four approved attrs, returning the per-source record entry.
`publish_source_fields(path,fields,spec,m0,completeness,expected)` writes a private sibling, reopens and
checks actual payload, rechecks current input identity and atomically replaces. Caller must obtain
`expected` before preparation. `validate_fields(fields,expected,reference_entry,source=...,target=...)`
requires exact current/prepared/reference identities and rehashes actual arrays/counts/masks.

`build_reference` prepares sources independently one at a time, pools closed cell/frame intersections,
filters contribution by genuine source role, seals each payload and discards fields. It rechecks all
current identities before returning a record. `publish_reference` validates current identity and payload
before and after private-sibling JSON writing, then atomically replaces. No extra project lock is added.
`drawing_frame` / `drawing_scale` return the portable records; `field_edges`, `frame_intersection`,
`geographic_ticks`, `frame_record` and `scale_record` implement approved display policy.

## Qualification and controls

Final successful command (read-only P-drive escalation, tiny scratch data only):

```text
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/packet2-probe.py
pixi run ruff check blueearth_cst/shared/map_reference.py blueearth_cst/shared/produce_map_reference.py
pixi run ruff format --check blueearth_cst/shared/map_reference.py blueearth_cst/shared/produce_map_reference.py
```

All exit 0. `packet2-probe-final.log` is final successful evidence. Its first attempted final run refused a
synthetic fixture lacking explicit EPSG:4326; the fixture was corrected, without weakening the CRS check.
`packet2-probe.log` retains the earlier pass before strict nested-schema/coordinate/URI refinements.

Passed: closed config defaults and valid 27/1000; rejection of month 28, bools, negative/fractional/unknown
settings and WF0 disagreement; strict JSON nonfinite refusal/negative-zero normalization; exact paired-root
JSON bytes with no checkout root; source-role exclusion while borrowed CHIRPS temperature stays 20 degrees;
4 finite precipitation cells at 366 mm/year; closed boundary-touch support; descending native axes and
explicit one-cell resolution; masked/complex/irregular coordinate refusal; constant darkest-class colors;
deterministic ticks/classes; unknown schema, payload corruption, rehashed wrong units/frame/unknown summary
refusal; fractional count and mask value 2 refusal before casting; normalized signed zero/NaN payloads,
distinguished signed infinities; reopened NetCDF digest equality; atomic JSON newline/private-sibling
cleanup; same-mtime catalog mutation invalidating both fields/reference; production ERA5-selected and
CHIRPS-selected factory resolution with original extra-ERA5 flags.

HydroMT current descriptor qualification resolves one local NetCDF without driver/raster loading. Logical
orography identity uses its root-relative catalog URI, plus streamed byte hash, and verifies agreement with
the declared concrete spec. Whole ordered catalog hashes cover descriptor/adapter text. Remote, VRT, Zarr,
wildcards/placeholders, preprocessor and unsupported-driver closures fail qualification explicitly.

Actual imported numerical/geospatial package versions match relevant active Pixi v7 Conda versions/builds.
Loaded GDAL 3.12.3, PROJ 9.7.1 and netCDF 4.10.1 also match locks and installed build metadata. Identity
contains active environment/platform, actual versions/builds and both lock byte hashes, never prefixes.
Checks read only relevant Conda metadata files; there is no mtime cache. Preparation closure includes the
conservative qualification list plus now-imported `prepared_maps.py`; reference adds its producer module.

## Integration boundaries and remaining gates

Legacy `tests/data/tests_data_catalog.yml` concretely fails current HydroMT Pydantic validation at parse:
missing `uri`; forbidden `path`, `filesystem`, `meta`, `crs`. Root owns official-schema fixture correction.
No legacy adapter or missing DEM dependency fallback was added.

Source helper still returns only fields/lineage in this packet. Packet 3 must return real preparation
identity separately, obtained before preparation and rechecked after; no fake identity is used meanwhile.
Root owns DAG wiring/config/tests. Independent scientific oracle, complete real paired-root execution,
actual stale DEM/extraction repair scheduling, all final maps/captions and separate E9 timing/memory costs
remain owed. Scratch paired roots establish helper byte determinism, not workflow-route independence.
