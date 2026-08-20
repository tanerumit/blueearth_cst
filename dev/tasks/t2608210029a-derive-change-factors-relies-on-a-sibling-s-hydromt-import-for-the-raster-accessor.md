---
title: derive_change_factors relies on a sibling's hydromt import for the .raster accessor
type: todo-item
status: backlog
effort: 1
area: projections / correctness
origin: t2608202307 follow-up
queue:
created: 2026-08-21
updated: 2026-08-21
---

> [!note] Overview
> **What** — derive_change_factors.py reads .raster.vars but imports no hydromt of its own. It is registered for it by get_change_climate_proj_summary's module-level import, reached through the import chain. Have the module import hydromt itself, beside the .raster use.
> **Why** — t2608202307 removed the stale `import hydromt` from get_change_climate_proj.py, which was the other provider of that side effect. The chain still works today and a fresh-process probe confirms it, but it is a side effect travelling through an import graph rather than a stated requirement: whoever next defers an import in the summary module breaks a file that never mentioned hydromt. derive_change_factors.py was outside t2608202307's declared write scope.
> **Effort** — small

## Progress

- [ ] `projections/derive_change_factors.py` -- reads `.raster.vars` (l.194, l.214);
      supplied by `get_change_climate_proj_summary`'s module-level import.
- [ ] `climate_analysis/plot_climate_source.py` -- `load_source_orography` ends in
      `.raster.reproject_like` on BOTH branches, but imports hydromt only inside the
      `era5` branch. The `chirps` branch is carried by `shared/climate_parity`, which
      imports `hydromt.model.processes.meteo` at module scope. Verified live today
      (`hasattr(da, "raster")` is True on a bare import); the point is that nothing
      says so.

Both are the same shape: the `.raster` accessor arrives as a side effect of some
other module's import rather than being asked for where it is used. Neither is a
live defect -- each was probed -- and the fix in both cases is one explicit import
beside the access.
