# Shared map-reference implementation evidence

Task: t2610082103. Date: 2026-10-10. Branch: refactor/t2610082103-shared-plotting.
Approved design SHA256: 4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278.
Source base: 22fbe441cef67db45130834eab87a31f8e3b6fc7.
Final source commit: 99939abfe59e5ac015714d6d72968e2c403ef85f.
Checks ran on the corresponding uncommitted file candidate before commit; staging/commit added no source
delta. Repository lint/format predated only two caption adapters, a Snakefile comment and fixture text;
the adapters passed touched-file Ruff checks, and the final CLI covered rule/fixture behavior. Independent
science, route, repair and cost probes pin the current preparation closure. Working tree is clean.

## Implementation and scope

The portable prepared-map core imports NumPy and Matplotlib only and owns deterministic frame, scale,
raster and overlay drawing. Workflow adapters retain IO, geospatial loading and scientific preparation.
WF0/WF1 share one historical producer/factory and independently consume its frame/classes. Source
preparation preserves native arrays, counts, masks, coordinates and scientific attributes. Sealed fields
and records carry current-byte identities and actual payload digests; each publication rechecks inputs
and the captured reference. Optional map completeness is project-owned, closed and bounded as approved.

Retired the unused diagnostic-map drawing helpers after a caller search; annual_fields is unchanged.
No canonical PNG filename, scientific output table or run output was deleted. The small local NetCDF
orography fixture and updated official HydroMT fixture schema support hermetic DAG checks on both platforms.
Documentation, templates, rule index and historical-tree inventory reflect the shared record.

## Environment and retained roots

Windows 11, win-64 Pixi default environment, Python 3.12.13. Loaded HydroMT 1.3.1, NumPy 2.4.6,
Xarray 2026.4.0, Pandas 3.0.3, Matplotlib 3.11.0 and backend dependencies qualify against installed
build records and pixi.lock; full identities are retained in qualification.md and produced records.

All execution evidence lives below `.tmp/scratchpad/shared-rendering/map-reference/` in session-1.
Keep these roots for task review and landing verification; they are ignored generated outputs.

- before-project: fresh rapid WF0 at the source base, 2000–2016 ERA5/CHIRPS.
- before-retained: retained real source/forcing before capture, read-only after capture.
- candidate-wf0: fresh candidate WF0, same rapid project settings and scientific source inputs.
- candidate-wf1-only: fresh producer execution with only WF1 enabled and no WF0 products.
- candidate-retained/wf1: nine figures from existing 2010–2016 model-grid forcing.
- candidate-retained/wf0-captioned: isolated optional source-map caption variants.
- repair-cost-cases: private real source/DEM copies for mutations, repairs and measured costs.

Each owned runner captured project/workflow/catalog bytes under its root's config/runs/_engine tree.
Provenance records preserve concrete input/code/environment hashes; capture summaries and probe logs
pin their inputs. Fresh ERA5 files can have different storage bytes despite exact Xarray identity;
that semantic equality is not substituted for matched-byte reference identity.

## Checks and scientific acceptance

Commands below are run from session-1 with full logs redirected to scratch files.

| Check | Result | Retained evidence |
|---|---|---|
| pixi run pytest tests/test_cli.py | 20 passed, 247.39 s | cli-final-authorized.log |
| Focused map-reference runtime contracts | 17 passed | runtime-contracts-final.log |
| Reference rule contracts | 3 passed | reference-rule-contract.log |
| Consumer + existing WF0 diagnostic contracts | 25 passed | consumer-contracts.log |
| Conditional rule/log registration contracts | 21 passed | log-contract-fixed.log |
| Config-composition matching suite | 127 passed + isolated 1 passed | config-composition*.log |
| Project-tree inventory | passed | inventory.log |
| pixi run lint / pixi run format-check | passed | final-lint.log / final-format.log |
| Caption adapter Ruff lint/format checks | passed after final text fixes | coordinator tool results |
| git diff --check | passed | coordinator tool results |

The config-composition isolated pass used authorized subprocess access after a sandboxed child stalled.
Likewise, the first final CLI attempt stalled; verified task-owned parent/children were stopped and the
authorized replacement passed. Preserve failed/stopped logs; neither is represented as a passing run.
The combined region/spatial/store/log check initially had one log-label failure; its bounded correction
passed all 21 log contracts. No full-suite result is claimed.

Independent scientific evidence: scientific-report.md, scientific-preparation-report.md,
scientific-reference-report.md and scientific-consumer-report.md. The final producer/core oracle has
74 passes, eight correctly refused controls and zero unresolved scientific failures. Real rapid and
Liberia preparation exactly matches prior native fields; CHIRPS auxiliary temperature/PET remains retained
and excluded from genuine reference pools. Float32 native-coordinate rounding and translated temperature
class thresholds were corrected with independent material-irregularity and nextafter controls.

Fresh WF0 exact comparisons cover 12 retained scientific/count/mask arrays, 54 source/comparison tables,
51 unaffected source/comparison temporal PNGs, and the four canonical source-map inventory. The final
counts are in wf0-parity-final.log and wf0-parity-summary.json. All scientific arrays/attributes match;
only the four added preparation/payload attributes are excluded from the old-file comparison.
Retained WF1 has nine identical native arrays, six identical CSVs, six unchanged temporal PNGs and the
exact nine-product inventory. Final corrected-caption capture: 143.82 s.

## Workflow execution, route and repair

Owned commands use `pixi run python scripts/run_workflow.py`, scratch project config and matching root.
WF1 uses `build_model --target produce_historical_map_reference --cores 3`; its dry-run and execution
schedule region, spatial units, selected ERA5, extra CHIRPS and producer, with no WF0/model/temporal jobs.
Fresh source extraction succeeded; the producer initially rejected real float32 CHIRPS coordinates.
The localized precision fix reused extraction and reran only producer successfully in 62 s.

WF0 uses `analyze_climate --cores 3`. Extraction, computation and producer succeeded, then data-drive
catalog access disappeared during rendering. Current Python-visible root/DEM access recovered; the owned
runner resumed with `--cores 2`, scheduling only four remaining jobs and retaining six up-to-date rules.
Resume completed in 4 min 39 s. Logs: wf0-candidate.log and wf0-candidate-resume.log.

repair-and-cost-evidence.md records executed source and catalog-backed DEM preserved-mtime mutations.
Reference-only rebuilds reject stale fields before any save; rebuilding both produces exact fresh reopened
arrays and digests. A newly valid pair installed after drawing is refused by the captured-reference guard.
Matched input bytes in separate shared-factory roots produce identical canonical records; this supplements
actual rule-directive equality and the fresh WF1-only execution, not a claim of two fresh extraction files
having identical NetCDF bytes. Direct WF1 publication-race injection was not performed.

## Cost, limitations and remaining batch gates

Measured private rapid input scope: 6,210 days, ERA5 2×3 cells, CHIRPS 5×6 cells, 2,086,436-byte DEM.
Source/DEM hashing takes 0.0022/0.0051 s; full/repeated ERA5 preparation 5.68–8.35 s; two-candidate
reference build 26.23–36.32 s; current-reference validation 10.23 s; actual-field validation 0.0162 s.
Sampled maximum process RSS is 383.02 MiB at a nominal 50 ms interval. Nested timings overlap, include
loaded libraries/retained allocations and are not additive or a guaranteed instantaneous peak.
No performance acceptability, basin-size scaling or cost-savings claim is made. Extraction costs are
retained separately in the fresh workflow benchmark parts; they are not included in preparation timings.

Scientific display equivalence does not establish climate-product accuracy or source/model PET equivalence.
The full software suite and fresh all-five execution remain owed at approved batch landing after branch
synchronization. No landing, pushing, release, external package publication or stale-baseline acceptance
is authorized or performed.

## Final renders and allocation

Coordinator inspected source and forcing map PNGs and the final CHIRPS captioned variant. The independent
validator inspected all three forcing maps, all four ordinary source maps and all optional captioned
source variants. Common frames/ticks, scales, overlay/gauge labels, missing/white support and complete
captions are legible without observed clipping. Real model temperature exceedance matches the reported
145 strictly over cells. Optional source captures declare three ERA5 and one CHIRPS map plus their
captioned counterparts, preserving the fresh workflow root. Three scratch capture-harness issues were
fixed: output-root mapping, staged result metadata and explicit captioned output keys. Their failed logs
remain; no source defect is claimed from them.

Economical allocation reused one python-engineer for serial implementation and the isolated repair/cost
packet, with one independent model-validator for scientific/visual acceptance. Coordinator handled wiring,
tests, docs and Git. Requested worker settings were 6.1 Sol/medium and Astra/high respectively; internal
effective settings and total worker token consumption are not independently verified. No fallback or
nested dispatch was needed. No allocation savings or billing claim is made.
