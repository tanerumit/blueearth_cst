# Caption/layout correction — bounded brief

Task t2610082103, 2026-10-10. Source base: `480f9be5`.
Branch: `refactor/t2610082103-shared-plotting`, session-1.
Status: geometry diagnosis/prototype authorized; exact source edits follow coordinator reconciliation.

## Existing contract and scope

`dev/reference/plot-style.md` already requires captions below the image without resizing the plotting
area or changing proportions. Caption text, data treatment and metadata stay with the workflows.
Implement that existing rule with the smallest shared correction. Preserve ordinary exports, filenames,
output inventory, labels, fonts, colours, legends, colorbars and supplied scientific values.

`add_caption(fig, text)` currently increases figure height and adds a supxlabel under constrained
layout. Prior probes measured axes-height growth. WF0 maps additionally shrink figure width before
calling it; compare against the original ordinary export, not the already-resized helper entry state.
Direct calls: WF0 `diagnostic_render.py`, optional `diagnostic_subbasins.py`, WF2 `plot_proj_timeseries.py`.
WF0 `diagnostic_figures.py` preserves its compatibility alias. WF1 has no direct embedded-caption caller.
Inventory command: `rg -n 'add_caption' blueearth_cst tests -g '*.py'`, checked 2026-10-10; remeasure on edit.

A bounded repair extends an established helper and rule; a new architecture loop is not currently
required. Escalate if probes require new layout ownership, figure lifecycle or incompatible semantics.
Do not invent a generic layout framework, chart API, new dependency or configuration key.
Map-reference production, clay-title clipping, crowded year ticks and missing-map semantics are separate.

## Allocation and ownership

A planning-only `default` agent requested GPT-6 Astra/high and returned this bounded allocation.
Requested execution settings are shown below; effective settings and token costs are unreported.

| Work | Role and requested allocation | Ownership |
|---|---|---|
| Geometry diagnosis and correction | python-engineer; GPT-6.1 Sol/medium | One source writer; scratch engineering/ |
| Representative visual review | dataviz-designer; GPT-6.1 Sol/medium | Read-only figures; own review note |
| Integration and complete coverage | Coordinator | Evidence, render drivers, docs, commits |

Fallback: GPT-6 Sol/high for either worker. Maximum two execution workers; one writer.
Engineer names candidate files before source edits, ceiling five tracked files. Permanent figure tests
are excluded by repository policy; use temporary falsifiers. Coordinator owns documentation separately.
Reopen a completed packet only for a failed falsifier or a changed contract, never routine scope growth.
No nested delegation, commits, branch changes, merges, pushes or canonical board edits by workers.

## Verification budget

Scope rapid, scientific numbers unaffected. Reuse retained inputs and frozen outputs; no all-workflow
run, numerical baseline, or full suite for this terminal figure change. Geometry and visual acceptance
are both required. A draw returning successfully does not prove that layout is correct.

| Claim | Check and input | Reusable output |
|---|---|---|
| Existing defect reproduced | Short/long captions; measured physical axes before/after | engineering/ probes |
| Plot dimensions preserved | Draw and export measurements, declared tolerance | Candidate geometry record |
| Decorations preserved | Fixed-aspect map, colorbar, outside legend, multipanel | Representative PNG pairs |
| Caller compatibility | Every direct caller, optional subbasins included | WF0/WF2/subbasin renders |
| Scientific/products unchanged | Input hashes, caption/inventory/prepared records | Same affected render roots |
| Code quality | Touched Ruff; final repo lint/format once | Owned check logs |

Frozen baseline: `.tmp/scratchpad/shared-rendering/candidate/` and its supplemental after tree;
newer WF2 files are also in `export-mechanics/candidate/`. Never overwrite these.
New outputs: `.tmp/scratchpad/shared-rendering/caption-layout/`, with engineering scratch, candidate
figures and a scoped comparison page. Reuse old adapters by copying and narrowing them, not executing
their unaffected WF1 sections. Report omitted figure families and why they do not call the helper.

The visual reviewer inspects at most six pairs chosen to cover single axes, multiple panels, square or
fixed aspect, colorbar, outside legend and long caption. The coordinator covers the remaining affected
products. Compare at matching physical scale and inspect saved outputs. PNG is the current embedded
caption product; do not claim independent PDF/SVG acceptance from raster evidence.

## Acceptance and completion

Capture a failing preservation check before source edits. Implement only after its diagnosis and
proposed files are reconciled. Preserve the existing helper signature where feasible and document its
actual caller requirements. Save commands, source/input/environment identity, dimensions, findings and
uninspected formats in the existing task evidence. Source edits receive their own verified commit;
canonical task records are maintained separately on main. Neither action authorizes landing or pushing.
