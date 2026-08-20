---
title: Snakefile parse imports the heavy stack via script modules
type: todo-item
status: active
effort: 2
area: performance / workflow parse
origin: test-runtime profiling (2026-08-20)
queue:
created: 2026-08-20
updated: 2026-08-21
---

> [!note] Overview
> **What** — Eight modules are imported at Snakefile parse time and each pulls
> hydromt, cartopy, geopandas, xarray, pandas, matplotlib or scipy. Defer those
> heavy imports into the functions that use them, so a parse costs ~0.1s of our
> code instead of 7-19s.
> **Why** — 78-89% of every dry-run is our own parse, not Snakemake's startup. A
> script: module is executed by Snakemake in its own process at rule runtime, so
> importing it at parse buys the heavy stack for nothing -- on every dry-run,
> every real run, and every one of the 11 test_cli dry-runs.
> **Effort** — large

## Progress

- [x] WF3 -- numpy off the Snakefile, pandas out of `surface_axes` and
      `prepare_cst_parameters` (5881c5c)
- [x] WF2 -- hydromt, geopandas, xarray, pandas out of the two projections
      modules (ac53685)
- [x] WF0/WF1 -- the plotting stack out of `climate_figures`, `compare_sources`,
      `plot_evaluation` (adfbba8)
- [ ] WF1's remaining 4.3s -- blocked, see t2608210029

## The enumeration was wrong — corrected 2026-08-21

The original list of five modules came from the WF2 cProfile alone and did not
survive contact with the other three workflows. **`run_stress_test.smk` imports
none of the five**, so as written this note could not have delivered its own
8.94s line. Three modules were missing:

| module | cost, imported alone | pulled into | pulled for |
|---|---|---|---|
| `shared/plot_evaluation` | 6.28s | WF1 | `STATION_PLOT_DIRNAME = "stations"`, one string |
| `experiment/prepare_cst_parameters` | 4.66s | WF3 | `refuse_out_of_domain_multipliers`, pure dict validation |
| `shared/surface_axes` | 4.57s | WF3 | `parse_surfaces`, `warn_on_heterogeneous_design` |

Plus `run_stress_test.smk` imported numpy at the top for three
`np.arange(1, N+1)` integer sweeps.

**Savings are a union over the heavy third-party deps, not a sum.** matplotlib
imported by any one module costs the same as by three, so a workflow only pays
off when EVERY path to a given library is closed. That, not the module count, is
what makes this large.

## Measured

`snakemake.exe` invoked directly so no `pixi run` wrapper is counted; min of 3
reps; `ours` = total minus snakemake's own startup, measured the same way in the
same sitting.

| dry-run | ours, before | ours, after |
|---|---|---|
| `analyze_climate.smk` | 7.27s | **1.57s** |
| `build_model.smk` | 9.53s | **4.27s** |
| `analyze_projections.smk` | 18.07s | **2.70s** |
| `run_stress_test.smk` | 6.74s | **1.71s** |
| total | 41.61s | **10.25s** |

**Caveat on the wall-clock pair.** The two sittings were not thermally
equivalent: snakemake's own startup measured 2.31s in the before sitting and
1.06s in the after, so the machine was materially faster the second time and the
`ours` columns above are not a clean A/B. A same-sitting re-measurement was not
possible from a task lane, which refuses `git checkout`.

The clock-independent evidence is which heavy libraries each parse-time import
set actually pulls into `sys.modules`. This one is immune to the drift:

| parse path | heavy libraries loaded, after |
|---|---|
| `analyze_climate.smk` | **none** |
| `analyze_projections.smk` | numpy |
| `run_stress_test.smk` | numpy |
| `build_model.smk` | cartopy, geopandas, xarray, matplotlib, pandas, numpy |

Before, from the module-level imports at a89927a (this work's base): WF0 geopandas + xarray +
matplotlib + pandas + numpy; WF1 those plus cartopy and scipy; WF2 hydromt plus
geopandas, xarray, pandas, numpy; WF3 numpy and pandas.

Per module, imported alone: `climate_figures` 6.19s -> 0.16s, `plot_evaluation`
6.28s -> 0.15s, `compare_sources` 6.78s -> ~0.2s, `get_stats_climate_proj`
13.40s -> 1.28s, `get_change_climate_proj` 13.53s -> 0.57s, `surface_axes`
4.57s -> 0.13s, `prepare_cst_parameters` 4.66s -> 0.16s.

## Why the WF2 import could not simply be dropped

`analyze_projections.smk:333` imports `get_stats_clim_projections` so
`REDUCER_KERNEL` can hold the FUNCTION OBJECT. `kernel_hash` hashes the
behaviour of the functions it is given and follows no call graph, so the
enumeration is what stops a changed weighting from being silently reused across
the series cache. The object is required; the heavy stack is not.

## The two hazards, and how each landed

1. **`import hydromt` is side-effecting** — it registers the xarray `.raster`
   accessor, so deferring it means guaranteeing it runs before any `.raster`
   access. In `get_stats_climate_proj` the accessor use turned out to be in the
   `__main__` block, not the enumerated function, so hydromt and geopandas moved
   there for free -- inside the `tee_to_log` block, per `fetch_gcm_raw.py`'s
   precedent. In `get_change_climate_proj` the import was simply STALE: the file
   has no `.raster` access at all. A four-case fresh-process probe checks every
   remaining reader still has the accessor; two sites that get it only by import
   accident are filed as t2608210029a.
2. **Deferring changes bytecode, so `kernel_hash` changes.** Both hashes moved:
   `get_stats_clim_projections`, `hydrological_year_bounds` and
   `get_change_annual_clim_proj` each gained an import statement. Every project
   re-derives its WF2 series cache once. Nothing pins either digest -- no literal
   in tests, no manifest entry -- so the blast radius is the runtime cache alone.
   Holding xarray at module level would have left `REDUCER_HASH` untouched at a
   cost of 5.00s instead of 2.94s; the owner ruled for the 2.1s.

## What ruff bought, and the hole it left -- corrected 2026-08-21

F821 is static, so for a PLAIN deferral it does catch every name left undefined
by a moved import, whichever branch reaches it. It found the
`__main__`-vs-function split in `get_stats`, nine annotation-only names in
`climate_figures` and twelve in `compare_sources`.

**But it does NOT cover a module carrying a `if TYPE_CHECKING:` guard**, and
this task added three of them (`surface_axes`, `climate_figures`,
`compare_sources`). The guarded import binds the name at module scope in ruff's
semantic model, so a runtime use with NO local import still resolves and the
missing import is invisible. Falsified at integration review, and re-confirmed
by hand: deleting the local `import pandas as pd` from `surface_axes.read_lookup`
leaves `ruff check` reporting "All checks passed" while the function raises
`NameError: name 'pd' is not defined`. The same deletion in `plot_evaluation`,
which has no guard, produces two ruff errors.

The claim originally written here -- that F821 covers this "regardless of which
branch reaches it" -- was therefore true of the pattern in general and false of
exactly the three files where the guards were introduced. The code was clean
anyway (checked independently with an AST auditor and with `TC004`), so nothing
shipped broken; the reasoning was what was wrong.

**`TC004` is the rule that actually closes it** and is now in
`[tool.ruff.lint] select` (t2608210029b). It flags the mutant above and was
clean repo-wide when enabled. This matters for whoever picks up t2608210029:
the deferral pattern and the TYPE_CHECKING guard arrive TOGETHER, because
postponing an import is what strands the annotations that then need the guard.
With TC004 on, scattering deferred imports through a 970-line module is a
mechanical change; with only F821, it was a hopeful one.

## Still open

WF1 stays at 4.27s. `shared/plot_spatial_maps.py` builds five module-level
`RasterStyle` constants and so cannot defer `shared/cartographic_map.py`
(cartopy). The registry representation cannot change instead -- tests read
`figure.style` as a real `RasterStyle`. The fix is a light home for
`RasterStyle`, which means editing `cartographic_map.py`: outside this task's
declared write scope. Filed as **t2608210029**.
