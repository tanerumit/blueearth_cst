"""Reconstruct REDUCER_HASH at HEAD under each worktree's pixi.lock."""

from blueearth_cst.projections import series_identity as si
from blueearth_cst.projections.get_stats_climate_proj import get_stats_clim_projections
from blueearth_cst.projections.grid_weights import (
    cell_area_weights,
    latitude_weights,
    longitude_weights,
    midpoint_edges,
    weighted_spatial_mean,
)

KERNEL = [
    get_stats_clim_projections,
    weighted_spatial_mean,
    cell_area_weights,
    latitude_weights,
    longitude_weights,
    midpoint_edges,
]
for label, lock in (
    ("session-1 (CRLF)", "pixi.lock"),
    ("primary   (LF)  ", "C:/Users/taner/workspace/blueearth_cst/pixi.lock"),
):
    print(label, si.kernel_hash(KERNEL, env_fingerprint=si.file_digest(lock)))
print(
    "ref tree recorded  b1245b016889b0f72476a281867a652c4aa63d7c22e771cb2c4797eeee60ee2e"
)
print(
    "cur tree recorded  3f549e3d26166828e81d485ff658049ed4db5db479d5983680589a9de71da34f"
)
