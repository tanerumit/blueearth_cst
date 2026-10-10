# Private repair, route identity and cost evidence

Command (Pixi default environment, authorized read-only P-drive access):

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/repair-and-cost-probe.py `
  *> .tmp/scratchpad/shared-rendering/map-reference/repair-and-cost-probe.log
```

All mutations and publications are under `repair-cost-cases/`. Baseline/candidate roots and the P-drive
are read-only sources for copying. The probe pins all `REFERENCE_FILES` before/after execution. No source,
dependency, Git, workflow-rule or upstream changes were made. The full log and incremental `costs.json`
retain diagnostic and measurement details.

## Input scope and method

The real fresh rapid extraction copies cover 2000-01-01 through 2016-12-31, 6,210 daily records, selected
ERA5 and extra CHIRPS. ERA5 has a 2×3 native grid and a 660,180-byte extraction; CHIRPS extraction is
298,280 bytes on a 5×6 grid. In the final reference frame, all six ERA5 cells and 30 CHIRPS cells intersect;
precipitation has six ERA5 and 29 CHIRPS finite cells, each with 17 eligible reporting years. Genuine ERA5
PET is finite in all six cells. A private copy of the qualified catalog-backed ERA5 DEM is 2,086,436 bytes.
The private catalog retains the official source driver, relative URI, renaming and elevation conversion. Both routes
use this same catalog and DEM; source/cell/geometry bytes are copied into different project roots.

No full workflow or extraction was executed here. Preparation and reference construction use the shipped
APIs independently and never reuse retained WF0 fields. The factory route comparison supplements actual
workflow evidence; it does not itself prove the real Snakefiles or their scheduling.

Mutation uses netCDF4 on bounded private copies, then restores exact `st_mtime_ns` using `os.utime`.
Current-byte digest changes and restored mtime are asserted. Source precipitation gains 1 mm; the catalog
DEM `z` values gain 1,000 in original geopotential units. Rebuild only reference first, then call the real
WF0 renderer while intercepting `Figure.savefig`; any save invalidates the refusal claim. Repair publishes
new fields and compares reopened arrays, counts, masks and scientific attributes with another fresh
preparation via `xr.testing.assert_identical`, plus the actual binary field digest.

The publication-swap discriminator constructs a figure from the initial valid pair, then changes source
bytes and installs a newly valid reference/field pair before the renderer's publication recheck. It tests
the captured-reference guard, rather than merely presenting invalid current data.

## Executed acceptance

- Source preserved-mtime mutation: reference-only rebuild rejected stale fields before any figure save.
- Source repair: reopened fields and actual digest exactly matched independent fresh preparation.
- Catalog-backed DEM preserved-mtime mutation: reference-only rebuild rejected stale fields before save.
- DEM repair: reopened fields and actual digest exactly matched independent fresh preparation.
- Publication swap: after a figure was constructed, a new valid reference and fields were installed and
  independently validated. WF0 rejected `Historical map reference changed during figure preparation`
  before `Figure.savefig` was called. This checks the WF0 publication path; no WF1 publication race was
  injected in this probe.
- Matched factory roots: independently built records from identical source/cell/catalog/DEM/geometry
  bytes in different project roots had exactly equal canonical JSON bytes and `reference_id`. These are
  the same shared factory used by WF0/WF1; actual Snakefile scheduling is not established by this probe.
- Current-reference validation and retained actual-field validation passed after final repair.
- All pinned producer/preparation closure file bytes were unchanged from entry through completion.

Final exit code: **0**. Full diagnostic log: `repair-and-cost-probe.log`; assertion/measurement summary:
`repair-cost-cases/summary.json`. Matched-route reference ID:

```text
95f1c1cef78fb0ba8ed9d3450547737d56302623ca2ee10847fded0863a4a460
```

## Measurement interpretation

Every timed operation records inclusive walltime, starting/ending current-process RSS and sampled maximum
RSS, with a nominal 50 ms sampling interval using installed psutil. Nested reduction/daily-series timings
are components of preparation/build timings, so they must not be added together. Samples include loaded
Python/native libraries and retained process allocations; they are not isolated allocation sizes or a
guaranteed instantaneous peak. Cold factory resolution includes imports and environment qualification.
This is a small real rapid grid, not a basin-size scaling or performance-acceptability result.
Host workloads were not controlled; ranges cover different mutation/candidate states in one session,
not repeated statistical benchmarks.

Observed timings (seconds, inclusive where noted):

| Operation | Walltime |
|---|---:|
| Cold factory resolution / later warm factory | 13.16 / 2.38 |
| Source byte hash, 660,180 bytes | 0.0022 |
| Local DEM byte hash, 2,086,436 bytes | 0.0051 |
| Current ERA5 preparation identity | 4.01 |
| Basin daily reduction, all instrumented preparations | 0.043–0.087 |
| Native annual-field reduction, all instrumented candidates | 0.228–1.301 |
| Initial full ERA5 preparation, including identity snapshots | 8.35 |
| Repaired/fresh repeated ERA5 preparation | 5.68–8.00 |
| Two-candidate reference builds, including preparation/identity checks | 26.23–36.32 |
| Reference atomic publication, including repeated current validation | 14.25–22.68 |
| Fields atomic publication, including current identity validation | 2.50–3.77 |
| Stale-field consumer refusal after reference validation | 6.74–8.78 |
| Current two-candidate reference validation | 10.23 |
| Actual retained field payload/identity validation, opened dataset | 0.0162 |

The deliberately injected swap's 80.58 s includes building/publishing a new valid pair inside the render
hook and the subsequent validation; it is not ordinary rendering cost. Maximum sampled process RSS over
the recorded operations was **383.02 MiB**. The cold factory began at approximately 183.41 MiB and its
sampled maximum was 348.27 MiB; those values include imports/native libraries. Most warm stages were
approximately 372–383 MiB. No cost is called acceptable, and larger-grid scaling was not assessed.

## Limits and unestablished claims

This checks real-source byte invalidation, catalog-backed DEM closure, exact repaired/fresh payload
equality, WF0 publication snapshot protection and matched shared-factory record bytes. It does not test
ordinary Snakemake rerun scheduling, actual WF0-disabled versus WF0-enabled executions, a WF1 publication
race, full-workflow inventories, baseline temporal parity or all real-data visual products. Root/validator
own those integrated claims. Sampled RSS is not an OS guaranteed high-water mark; preparation/build
measurements are inclusive and nested component timings overlap. No permanent tests or production roots
were modified.
