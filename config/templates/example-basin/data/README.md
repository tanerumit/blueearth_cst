# Case data

Keep basin-specific sidecar files in this directory. The supplied
`output_locations.csv` identifies model output locations with columns
`station_name`, `x`, and `y`; `x` is longitude and `y` is latitude in decimal
degrees. Replace the example row with the intended outlet and use coordinates
consistent with `basin.region` in the project config.

Optional observations are configured under `observations` in
`project_config_build_model.yml`. Before adding a series, consult the toolbox's
current configuration and data-format documentation for supported variables,
units, date/time format, and station matching. Follow the documented matching
requirements and record the units and matching choices here or alongside the
file; do not infer or convert units silently.

For every sidecar, record its source and provenance, retrieval or preparation
date, any transformations, and whether values are measured, derived, or
synthetic. Label synthetic examples explicitly and replace them before
scientific interpretation.
