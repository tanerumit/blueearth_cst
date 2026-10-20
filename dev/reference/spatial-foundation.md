# Shared spatial foundation

Last updated: 2026-10-20

Use this reference when changing spatial ownership, region reuse, location identities or basin maps.
`blueearth_cst/spatial/` owns the implementation; the [implementation map](workflow-implementation-map.md) points
to rule definitions and consumer checks.

## Ownership and dependency direction

Delineate the project region once from basin settings and the catalog. Model-free climate extraction,
projection analysis and spatial products consume that same region artifact. They must not read a built
Wflow model to obtain their extent.

The shared vector foundation supplies basins, subbasins, rivers and the location registry. WF1 alone
prepares thematic raster products needed to parameterize Wflow. Keep model-neutral producers independent
of land/soil inputs they do not consume; changing a model build must not manufacture a new region.

`delineate_region.py`, `delineate_spatial_units.py`, `products.py` and `config.py` in
`blueearth_cst/spatial/` own the producer contracts. Their shared rule parameters must describe their
actual spatial inputs, not unrelated workflow selection or model settings.

## Spatial identities and controls

`blueearth_cst/spatial/identity.py` owns stable basin, subbasin and location identifiers and capacity
validation. Do not copy its encoding tables into another registry. `spatial/config.py` owns configuration
translation, while the project schema and `config/advanced_settings.yml` own admitted settings/defaults.

The foundation resolves each parent feature independently and snaps configured controls to the analysis
river network. Automatic partitioning supplies fallback parents when controls do not prescribe a split.
The implemented budget and ID capacities are enforced by the current spatial configuration and identity
code; old ADR descriptions of per-parent versus shared budgets are historical, not a competing contract.

The persisted location registry preserves stable spatial identifiers. Model-specific gauge positions and
outlet-index mappings are downstream representations; do not substitute positional model output labels
for the foundation's identity. The [WF1 contract](wf1-model-construction.md) describes those mappings.

## Basin maps

Draw the basin-area map from the shared spatial foundation, not from `staticmaps.nc` or a model-dependent
copy of the geometry. Physical waterbody layers are clipped from catalog sources by
`spatial.products.clip_waterbodies`; the hydrological model keeps its own filtering and setup behavior.
Empty layers and missing-source warnings follow that producer's implementation.

`blueearth_cst/shared/plot_map.py` owns the map reader. Figure layout and export conventions belong in
[plot style](plot-style.md), rather than being repeated here.

## Verification entry points

Use `tests/test_spatial_identity.py`, `tests/test_spatial_config.py`, `tests/test_spatial_products.py`
and `tests/test_spatial_units_rule.py` for their respective contracts.
`tests/test_cross_workflow_inputs.py` checks workflow dependency boundaries.
Select the applicable checks through the [validation ladder](validation-ladder.md).
