# Case data

Keep basin-specific sidecar files in this directory. The supplied
`output_locations.csv` identifies model output locations with columns
`station_name`, `x`, and `y`; `x` is longitude and `y` is latitude in decimal
degrees. Replace the example row with the intended outlet and use coordinates
consistent with `basin.region` in the project config.

Optional observations are configured under `observations` in
`project_config_build_model.yml`. Before adding a series, consult the toolbox's
current data-format documentation in `blueearth_cst:config/templates/README.md`
for supported variables, units, date/time format, and station matching. Follow the documented matching
requirements and record the units and matching choices here or alongside the
file; do not infer or convert units silently.

`observed_daily_discharge_template.csv` contains only the semicolon-separated
header `time;1010;1020`. Replace the illustrative station IDs with the resolved
`wflow_id` values and add your observed daily series before configuring its
absolute path under `observations`. The starter leaves observations disabled
(`river discharge: null`); the header-only file is not a usable observed record.

For every sidecar, record its source and provenance, retrieval or preparation
date, any transformations, and whether values are measured, derived, or
synthetic. Label synthetic examples explicitly and replace them before
scientific interpretation.
