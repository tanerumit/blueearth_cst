# Shared map-reference producer — intake

Owner request: "yes, lets work on the shared map-reference producer design."

## Problem and settled direction

The approved Python-first plan separates portable drawing from workflow scientific preparation.
Foundations, export, captions and prepared annual/monthly charts are implemented. This increment
designs a historical-authority map reference that WF0 and WF1 can produce from declared inputs.
Fresh WF0 followed by WF1 and fresh WF1 alone must yield the same reference under matched settings.
Source-grid and model-grid fields retain their native support and scientific preparation.
The task requires common frame, coordinate grid/ticks and color classes, pooled historical scales,
explicit under/over-range forcing display and reference identity preventing stale reuse.
This is a design packet; source implementation and landing are outside this turn's authority.

## Ordinary journey and actor boundaries

The researcher chooses historical source candidates and a selected forcing source in project config,
a historical period, reporting-year start and basin. They run WF0 to compare historical candidates,
or WF1 alone to build and inspect model forcing. Either route obtains identical historical-authority
display settings without requiring previously rendered figures. Figures retain established paths and
captions; captions explain reference support and unavailable/out-of-range values.
Shared producer rules own preparation and provenance of the reference; workflow adapters own native
field science; the plotting core receives prepared reference/field inputs and draws them.

## Scope and decision criteria

Specify the smallest coherent increment: source membership/order, selected-source frame authority,
historical pooling support, variable availability, units, completeness, color classes/ticks,
map aspect/grid rules, record identity, invalidation and producer ownership in both DAGs.
Identify extra WF1-only extraction/reduction costs and reuse that is demonstrably valid.
Include concrete repository/output trees, producer declarations, metadata audience, compatibility,
error behavior, alternatives, migration and claim-to-check acceptance cases.
Keep public plotting distribution, R/WF3, projection maps, arbitrary projections, broad map redesign,
re-engineered HydroMT/Wflow data handling and changes to simulation science outside scope.
No plugin system or universal plotting schema. Prefer ordinary functions and small records.

The saved requirement for pooled historical scales is settled. The concrete reference record,
producer rule, support policy and configuration ownership remain provisional for G1.
Do not infer equal scientific values from shared colors or require spatial interpolation.

## Sources and evidence register

Source candidate: session-1 commit `22fbe441`. Canonical task and plan live on main under
`dev/tasks/t2610082103-shared-climate-plot-renderers.md` and `dev/tasks/t2610082103/landscape-and-plan.md`.
Installed plot-style and validation-ladder references govern appearance and verification.
Evidence below is static source observation, not numerical equality or measured performance.

| ID | Premise / exact observation | Source | Precision and reproduction | Confidence |
|---|---|---|---|---|
| E1 | WF0 uses selected-first deduplicated climate.sources | analyze_climate.smk | Inspect lines 95–121 | High, static |
| E2 | WF0 pools visible historical values; one-grid case uses all field cells | diagnostic_render.py | Inspect map branch | High, static |
| E3 | WF1 retains only selected climate store; forcing maps derive own finite limits | build_model.smk; forcing_figures.py | Inspect producer and map branch | High, static |
| E4 | WF1 frame comes from selected native climate cell edges | model/plot_map_forcing.py | Inspect source_nc path | High, static |
| E5 | Cellwise eligible years use dg.annual; temp means, precip/PET totals | diagnostic_maps.py | Inspect annual_fields | High, static |
| E6 | Drawing derives classes from limits, uses field latitude for aspect, auto ticks | diagnostic_maps.py | Inspect draw_map | High, static |
| E7 | Shared map policy needs WF0-independent settings | diagnostic_settings.py; Snakefiles | WF0 settings versus WF1 defaults | High, static |
| E8 | Both routes can yield identical records with declared inputs | Prospective claim | Falsify with fresh paired roots and record comparison | Hypothesis |
| E9 | Extra candidate work requires cost measurement, not an acceptability claim | G1 ruling | Measure extraction, hashing, reduction and memory separately | Unmeasured |
| E10 | Wrapper holds project-execution archive_lock across child Snakemake execution | workflow_archive_launch.py | Inspect execute path around line 650 | High, static |
| E11 | All-NaN leap-year amount returns 0 at 31/366; NaN at 3/15 | diagnostics.annual | One-time all-missing-probe.log; 366 daily values, m0=1 | Measured exact |
| E12 | At 27/366, all-missing year and wholly missing February amounts are NaN | diagnostics.annual | approved-range-probe.log; contrasts 31/366 | Measured exact |

Domain-scientific content: yes. Pooling support, missingness/completeness, physical units and
interpretation of shared classes require model-validator review before G1. Review hypotheses as
testable claims with explicit future falsifiers; do not treat an unrun test as supporting evidence.

## Gate materialization

- Static source/DAG coverage: files and Pixi task commands exist; no proposed rule executes yet.
- Future shared-contract gates: live ladder's test-full and test-e2e tasks are defined in pixi.toml.
  Data mirror, Julia and R prerequisites must be preflighted at implementation; not qualified here.
- Figure preservation requires pre-change captures of all affected source and forcing maps before
  implementation. Existing chart captures are useful inputs, not a complete map acceptance snapshot.
- Order independence requires two fresh roots using identical config/data identities; a WF1-only
  config variant adds distinct coverage beyond an all-five rapid gate. Retained historical figures
  cannot prove this property. Reuse a fresh all-five output root where the live ladder requires it.
- Identity/invalidation needs small scratch probes and DAG dry-runs against the proposed mechanism.
  Framework execution claims must be probed before acceptance, not inferred from prose review.
- Numerical baseline manifest is stale; do not use it as a gate for display settings.

## Derived artifacts and lifecycle

Design-v1 is the authoritative proposal. No duplicate sketch is needed; embed its annotated tree and
compact flow. Task progress and next-action link derive from run status after review. Implementation
brief is generated only after G2 and carries falsifiers. Plot-style/config docs change during accepted
implementation. Author may edit only design-v1 in this packet; reviews and status have separate owners.
Run lifecycle: task-owned review; immutable reviewed revisions, acceptance identity in status.
Canonical home: `dev/tasks/t2610082103/design-runs/map-reference/` on main. Scratch hosts active workers;
driver retains exact bytes there. G1 reviews the concrete draft/tree/domain findings; G2 approves
exact externally reviewed bytes. Existing broad plan approval does not approve new output contracts.
