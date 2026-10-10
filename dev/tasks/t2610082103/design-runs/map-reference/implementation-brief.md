# Shared map-reference implementation

Approved design: [design-v2](design-v2.md), SHA256
`4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
G2 approved 2026-10-10. No landing/push. Source start `22fbe441`; pinned session-1 branch
`refactor/t2610082103-shared-plotting`. Read the design for exact contracts; this brief delegates execution.

## Goal and constraints

Deliver a WF0-independent historical reference and portable map renderer consumed by WF0/WF1. Preserve
the approved native science, source/PET roles, existing temporal products and PNG paths. Config bounds,
common viewport/classes and honest missing/unscaled display follow the design. No upstream changes,
new dependencies, per-source cache, managed manifest or external packaging. No permanent figure tests.
Never weaken current-byte provenance to timestamps or leave placeholder identities.

Root owns integration, task records, Git, captures, configuration/DAG wiring and documentation. One
engineer writes source at a time. All workers are in a shared worktree and must preserve others' edits.
No worker may delegate, commit, broaden scope or edit another packet's files without a root handoff.

## Ordered allocation

| Packet | Role/model requested | Ceiling and ownership | Prerequisite |
|---|---|---|---|
| 0 | python-engineer; 6.1 Sol/medium | Read-only qualification; scratch report/probes | Approved design |
| 1 | Same engineer | Three files: portable map/core source preparation/old maps | Capture + qualification |
| 2 | Same engineer | Two shared producer/identity files | Packet 1 interfaces |
| 3 | Same engineer | Five WF0/WF1 consumers | Packet 2 contracts |
| 4 | model-validator; Astra/high | Read-only scientific evidence; scratch verdict | Prepared candidate |
| 5 | Root | Wiring, tests/docs, integrated checks and completion | Candidate + verdict |

Max two workers; reuse engineer serially. Requested settings are unverified unless observable. Sol/medium
is the planned execution fallback; a quota failure requires a changed condition, not repeated retries.
Scientific ambiguity returns to frontier validation. Architecture failure uses the reviewer slot for a
bounded cst-architect review. Extra paths belong to root. Root can implement uncovered changes inline.
Savings remain undetermined; record allocation diagnostics at completion.

## Ownership and worker packets

0. Qualify concrete consumed orography files through existing HydroMT descriptors, transitive local
   preparation closure, and loaded-package/lock consistency. Report facts/probes in `qualification.md`.
   Root captures affected current figures, captioned variants, retained arrays/counts/masks, metadata and
   forcing inventory before source edits. Unexposed PET dependencies return the interface gap to G1.
1. Own `blueearth_cst/plotting/prepared_maps.py`,
   `blueearth_cst/climate_analysis/source_map_fields.py` and `diagnostic_maps.py` in that same directory.
   Extract existing preparation exactly; keep old callers runnable until migration. Implement deterministic
   drawing records with no workflow IO/backend imports. Falsifiers: changed scientific arrays; imports
   needing more than NumPy/Matplotlib; wrong class final endpoint or source-selected aspect.
2. Own `blueearth_cst/shared/map_reference.py` and `produce_map_reference.py`.
   Implement resolved spec, closed config/record, canonical identities, actual payload hash and atomic
   publication from the design. Falsifiers: byte differences across matched route roots; same-mtime
   stale inputs accepted; unidentified PET inputs; mixed fields/reference accepted.
3. Own `climate_analysis/compute_climate_diagnostics.py`, `diagnostic_render.py`,
   `plot_climate_diagnostics.py`, `model/plot_map_forcing.py`, `model/forcing_figures.py` under
   `blueearth_cst/`. Validate identities before publication and implement honest captions; preserve
   temporal science and products. Falsifiers: stale retained fields render with fresh reference;
   changed temporal products; changed map/forcing inventory beyond approved metadata/reference.
4. Model-validator independently checks known-answer and pre/post cases in design section 9.1. Report
   executed science separately from argument. No source writes. Failures reopen only their packet.
5. Root owns `shared/config_composition.py`, both affected Snakefiles, appropriate contract tests,
   the four documented configuration/workflow files, two templates and `dev/reference/plot-style.md`.
   Search consumers before retiring helpers; all newly unused code must be resolved explicitly.

Ownership boundaries above are a design-derived hypothesis (2026-10-10). Before edits, remeasure using
`rg -n` for changed symbols/imports and inspect the actual rule inputs/consumers. Record unexpected paths.

## Validation schedule and evidence

Scope: shared runtime/configuration contract; scientific numbers potentially affected by extraction and
source-role pooling. Preserve local numerical methods; exact comparisons required. The stale numerical
baseline is not the map oracle. Use `.tmp/scratchpad/shared-rendering/map-reference/` for probes/logs.
Preserve needed evidence in the task home; generated project outputs remain untracked.

- Per edit: matching focused contract tests and touched Python Ruff lint/format only.
- Before code commit touching rules/signatures/inputs: `pixi run pytest tests/test_cli.py`.
- Final Python candidate: `pixi run lint` and `pixi run format-check` once.
- Producer-only DAG: existing owned wrapper with `--target produce_historical_map_reference --dry-run`;
  any temporal/model job disproves producer independence. Match both compute/reference dependencies.
- Execute WF0/WF1 affected paths and inspect all maps/captions, optional captioned variants and inventory.
  Before/candidate roots and config/input hashes are recorded; retained-input cases do not establish
  fresh-route identity. Reuse a fresh all-five root at approved landing and add a distinct WF1-only root.
- Paired-root reference equality: any differing record bytes/frame/ticks/classes under matched inputs
  disproves route independence. Include disabled WF0. Preserve all unrelated temporal products exactly.
- Incremental repair: mutate source/DEM bytes with preserved mtime, rebuild reference only and require
  stale-field rejection. Rebuild both fields/reference and compare against fresh preparation. Also check
  ordinary scheduling, corrupted payloads, missing tags, settings/catalog/code/environment changes.
- Independent known answers: all missing/full-February at 27/366 and 27/1000, reject 28, boundaries and
  adjacent values, constant/all-missing/scaleless fields, unequal/descending/one-cell grids, reporting
  years/gaps and real CHIRPS/Celsius/normalized-K/PET cases from section 9.1.
- Measure extraction/hash/reduction/validation/duplicate reduction and peak memory separately. No
  performance acceptability claim. Cost measurements include dimensions/window/candidate population.
- Full software and fresh all-five gates remain owed at approved batch landing per the live ladder;
  a full pass replaces fast. Record candidate/commands/results/environment/config hashes/output roots.

Acceptance requires implementation-backed scientific and visual verdicts, all applicable falsifiers,
focused checks and compatible inventories. Design review alone does not satisfy execution. Do not commit
failing source. No new permission gate except a genuine unresolved design qualification boundary.

## Resume index

| Phase | State | Durable marker | Blocked on | Next action |
|---|---|---|---|---|
| Qualification/capture | complete | qualification; fresh WF0 and retained captures | — | Keep before roots read-only |
| Drawing/preparation | checkpoint passed | packet1; scientific-preparation-report | — | Integrate identity result |
| Producer/identity | complete | packet2; scientific-reference-report | — | Retain evidence |
| Consumers/wiring | complete | CLI 20 passed; packet3; scientific-consumer-report | — | Retain evidence |
| Acceptance/completion | complete | implementation-evidence; commit 99939abf | — | Await approved landing |
