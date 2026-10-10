---
title: Consider bounded-window forcing preparation for WF4
type: todo-item
status: backlog
effort: 2
area: wf4
queue: 9
created: 2026-10-09
updated: 2026-10-10
---

> [!note] Overview
> **What changes** — Evaluate bounded-window forcing preparation while preserving WF4 outputs and HydroMT
> calculations.
> **Why it matters** — Liberia PET preparation ran out of memory with three concurrent downscaling jobs.
> **What it takes** — Estimated 2-3 developer days plus run time; memory, speed and equivalence need measurement.

## Progress

- [ ] Confirm the allocation mechanism and compare serial versus concurrent preparation on Liberia inputs.
- [ ] Decide whether measured memory pressure and throughput justify bounded-window preparation.
- [ ] Prototype windowed HydroMT preparation, bounded final-file assembly and interrupted-run cleanup.
- [ ] Check calendar boundaries, numerical equivalence, NetCDF metadata and Wflow compatibility.
- [ ] Benchmark one full Liberia member; choose window size and concurrency from memory and elapsed time.

## Context

Deferred for future consideration.

Observed in the 2026-10-09 sp2-liberia experiment `active_20261009`: rule 4.04
`downscale_scenario_series` failed for runs 13 and 14 inside HydroMT De Bruin PET at
`np.isclose(k_ext, 0.0)`. Each failure reported a 1.47 GiB allocation for a float32 array of
shape `(7665, 231, 223)`. Three jobs ran concurrently; other members completed preparation.
Concurrent memory pressure is inferred from these logs, not measured; peak memory was not captured.

Candidate: prepare one year at a time through the existing HydroMT APIs, persist temporary windows,
release arrays, and assemble the same single forcing NetCDF using bounded reads. Retain calculations, output contracts and calendar handling. Smaller Dask chunks or output-file splitting alone may not bound
this eager NumPy operation. Serial downscaling is the immediate workaround.

## Refs

- Code: `blueearth_cst/experiment/downscale_climate_forcing.py`, function `prepare_model_forcing`.
- Rule: `blueearth_cst/experiment/rules/simulate_and_metrics.smk`, rule 4.04.
- Logs: `C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/logs/_parts/simulate_system/active_20261009/4.04_downscale_scenario_series/`.
