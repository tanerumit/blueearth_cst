# Prepared annual and monthly charts: intake

Date: 2026-10-10. Task: t2610082103. Genre: decision-record (software interface design).
Canonical home: `dev/tasks/t2610082103/design-runs/prepared-charts/` in the primary checkout on main.
Scratch staging is in session-1; the driver preserves the reviewed bytes in that canonical home.

## Request and settled direction

User: "yes, continue to next step" after completion of caption/layout foundations.
Earlier: "yes, lets go python rendering first" and "Yes, I agree with your plan. Please make sure
to save this extensive note first, then lets start the work. Please delate the work to suitable
roles/models with focused hand-offs that aims a good balance between costs (token consumption)
and effectiveness".

The approved plan is in the primary checkout at
`dev/tasks/t2610082103/landscape-and-plan.md`, Stage 2. The previous packet's completion and next-action
record are in `dev/tasks/t2610082103/caption-layout/completion.md` and the task note.
This increment supplies prepared-input annual-series and monthly-cycle interfaces for WF0 and WF1,
including hydrological summaries, with scientific preparation retained by the workflow adapters.
Source baseline: session-1 commit `4d19a377e733fc5056c480981771889736841ae0`.

## Problem, scope and constraints

WF1 constructs WF0's large `View` objects to reuse a small subset of drawing operations. Extract the
smallest useful rendering interface into `blueearth_cst/plotting/`, and migrate the active annual/monthly
callers. Preserve appearance, metadata, paths, data values, source order, gaps, fitted trends and
figure-specific choices. Keep ordinary functions and small records/settings. No new dependencies,
plugin framework, universal chart schema, external package scaffolding or scientific algorithms.
Return Matplotlib objects; exporting, captions and logging remain with their existing owners.

Scope includes `diagnostic_figures.series`, `_climatology`, `_annual_trends` and their active callers,
`model/forcing_figures.render_forcing_figures`, and `shared/func_plot_signature.plot_basavg`.
WF0 extremes also calls `_annual_trends`; preserve its existing per-metric composition without redesigning it.
Inspect callers rather than assuming these names establish the final module/API split.
Keep the WF0 `View` adapter and compatibility entry points where still used. Remove WF1 construction
of that view for these charts. Existing scientific and map dependencies need not disappear wholesale.

Explicit non-goals: changing scientific preparation, tick crowding fixes, map scales or references,
caption mechanics, WF2 specialist charts, R/WF3, interactive rendering and external distribution.
Never add persistent tests solely for terminal figure appearance. Use disposable probes and renders.
Do not edit Snakemake or runtime/configuration contracts in this packet.

## Ordinary journey and boundaries

An existing workflow runner prepares climate or model summaries using current methods. Its adapter
selects units, ordering, values, bands, retained fitted trends and their meaning. The shared renderer
draws the supplied values and styling. The adapter exports the same figure and caption products at
the same paths. Users continue running the same commands with the same configuration. Developers can
reuse the small renderer directly without constructing a WF0 diagnostic bundle. Future external reuse
is enabled by dependency direction, not promised as a packaged product in this increment.

The author must show the proposed affected repository tree, unchanged output inventory, before/after
developer calls, meaningful alternatives and compatibility in one self-contained design. No HTML sketch
is needed; an embedded dependency diagram and annotated tree suffice.

## Decision and success criteria

Prefer the smallest interface that supports actual callers, explicit statistical meaning and preserves
source ordering/gaps. Preserve hydrological tick/legend exceptions rather than normalizing appearance.
No core import from a workflow, pandas preparation module, configuration, filesystem or Snakemake.
Validation must distinguish prepared-value preservation, artist geometry/data, and visual acceptance.
Successful extraction removes duplicate drawing and WF1's View dependency without shifting algorithms.

## Evidence register

| ID | Premise / observation | Source and reproduction | Confidence |
|---|---|---|---|
| E1 | WF1 forcing constructs View for annual/monthly drawing | `forcing_figures.py:176–188,229–251`; read source | High, source |
| E2 | Hydrological summaries construct View, with distinct annual ticks/legend | `func_plot_signature.py:308–368` | High, source |
| E3 | Monthly renderer receives mean/p10/p90 tables; no percentiles computed there | `diagnostic_figures.py:386–425` | High, source |
| E4 | Annual artist uses retained slope/intercept and eligible endpoint years | `diagnostic_figures.py:987–1058` | High, source |
| E5 | Extremes shares the annual-trend drawing helper | `rg -n '_annual_trends\(' blueearth_cst` | High, source |
| E6 | Caption baseline covers WF0; earlier baseline covers WF1 forcing/summaries | Roots below; file inventory | High, files present |
| E7 | Identical appearance and values are feasible after extraction | Hypothesis; matched-input probes/renders | Unproven until implementation |

Domain content: yes, conservatively. No method change is proposed, but interfaces must preserve
aggregation, band interpretation and trend meaning. A pre-G1 model-validator lens must assess these
claims and disposition E1–E7; E7 is a feasibility hypothesis, not claimed validation success.

## Validation materialization

Follow `dev/reference/validation-ladder.md` section Planning and reusing verification. The author maps
each claim to a check, case and reusable output root. Figure-only changes need affected renders and
inspection, not a fresh hydrological run, baseline manifest check or full suite.

- Runnable now: `rg` caller inventory; `pixi run python` imports and disposable probes; touched Ruff.
- Existing pre-change WF0 root: `.tmp/scratchpad/shared-rendering/caption-layout/candidate/`.
- Existing pre-change WF1 root: `.tmp/scratchpad/shared-rendering/candidate/wf1/`.
- Existing retained WF0/WF1 inputs and render recipes: `.tmp/scratchpad/shared-rendering/candidate/`
  and `export-mechanics/` siblings. Inspect scripts before reuse; never overwrite frozen roots.
- Reusable geometry recorder: `caption-layout/capture.py`; inspect suitability for new claims.
- New evidence root: `.tmp/scratchpad/shared-rendering/prepared-charts/verification/`.
- Needs pre-change capture before editing: exact targeted artist/prepared-value signatures and any
  uncovered optional hydrological subbasin products. Baseline images alone do not prove array parity.
- Edge cases add distinct coverage: non-January month order, invalid/gapped years, all-missing and
  constant values, negative values, multiple sources, missing temperature, trend unavailable/available,
  hydrological amount versus mean summaries, and optional subbasins.
- Headless external review was available in the prior run. Recheck read-only enforcement and model
  support before dispatch; no claim that the forthcoming gate has already run.

## Derived-artifact register

After G2, driver derives the implementation handoff and updates the task next-action link from the
accepted design. Later implementation updates `dev/reference/plot-style.md` for ownership/API usage,
and retains validation evidence in this task. Authors must not edit those derived artifacts.

## Authority

One writer per artifact. Source work remains in session-1/refactor/t2610082103-shared-plotting.
Board/planning records remain on main. No source implementation before reviewed design acceptance.
No branch switch, merge or push. Root integrates and checks worker results; no nested delegation.
