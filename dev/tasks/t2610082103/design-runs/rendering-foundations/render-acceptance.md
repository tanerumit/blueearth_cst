# Candidate rendering acceptance

Result: appearance-preserving extraction passes the captured normal cases and bounded supplemental cases.
No additional normal renders are needed. Keep this scratch tree for user review alongside `baseline/`.

Identity: baseline Git revision `07288e94`; candidate is the implemented working-tree extraction of
approved design-v2. `identity.json` records design, Pixi lock and core SHA256; `final-core-identity.json`
records the core again after rendering. Python 3.12.13, Matplotlib 3.11.0, Agg, Pixi default environment.
The candidate scripts are baseline copies with output destinations changed only. Source modules,
baseline outputs, production inputs, Git and task-board files were never edited by this agent.

## Commands

Run from the session-1 worktree; each output is redirected to the corresponding owned log file.

```powershell
pixi run python .tmp/scratchpad/shared-rendering/candidate/render-baseline.py *> .tmp/scratchpad/shared-rendering/candidate/wf0-wf1.log
pixi run python .tmp/scratchpad/shared-rendering/candidate/render-wf2.py *> .tmp/scratchpad/shared-rendering/candidate/wf2.log
pixi run python .tmp/scratchpad/shared-rendering/candidate/inventory.py --evaluation *> .tmp/scratchpad/shared-rendering/candidate/evaluation.log
pixi run python .tmp/scratchpad/shared-rendering/candidate/supplemental.py *> .tmp/scratchpad/shared-rendering/candidate/supplemental.log
pixi run python .tmp/scratchpad/shared-rendering/candidate/inventory.py *> .tmp/scratchpad/shared-rendering/candidate/inventory.log
pixi run python .tmp/scratchpad/shared-rendering/candidate/compare.py *> .tmp/scratchpad/shared-rendering/candidate/comparison.log
```

All final commands passed. The supplemental fixture initially needed an explicit UTF-8 source read;
its corrected rerun reused completed forcing/subbasin outputs. Its second synthetic future window was
given distinct values to make connecting multi-period lines visible. Those are labelled synthetic values,
without a climate interpretation or modified method.

## Matching evidence

Normal total: 167 PNGs, matching every baseline path, pixel dimensions and DPI. WF0: 116; WF2: 36;
WF1 forcing: nine; WF1 evaluation: six. No ordinary/captioned inventory differences.

`comparison.json` records equal 86 retained WF0/WF2 input hashes, 77 WF0 prepared table/series hashes,
91 evaluation input hashes, 73 combined WF0/WF1 source/prepared CSV hashes, and two prepared station
series hashes. Absolute scratch output prefixes are normalized before prepared-file comparison.
All nine WF1 prepared map fields, counts and masks are identical through Xarray, including coordinates
and attributes. Fifteen normal caption/record/metric/weight artifacts are identical. No image-byte
comparison is used as an acceptance oracle.

WF2 uses the same retained-table adapter as baseline. Its four scenarios and 13 models supply dense
coverage without subsampling. The one-window production adapter continues to omit the unavailable
multi-period product; the supplemental fixture explicitly exercises that renderer.

Supplemental total: 20 before/after pairs, with matching dimensions/DPI and four caption inventories.
Pre-change implementations are loaded from Git into scratch-only modules; candidate modules are imported
normally. Shared style and label-box aliases retain object identity, and a process-local style mutation
propagates to the WF0 alias and is restored.

- Nine forcing figures per side: all-missing precipitation, constant temperature/PET and one missing PET cell.
- Three optional WF0 subbasin figures and three captioned copies per side: retained ERA5 tables relabelled
  as one fixture subbasin, explicitly layout coverage rather than a new spatial analysis.
- Four long-series/short-or-long-caption figures per side: synthetic 1800–2150 values and measured axes.
- One multi-period cloud per side: existing deterministic fixture, two future identities and distinct values.

Canvas dimensions, axes boxes in inches and tick positions match exactly for the measured short-caption,
long-caption and multi-period probes. `supplemental/geometry.json` preserves these measurements.

## Visual inspection and inherited limitations

This agent opened both normal performance sheets, candidate captioned comparison climatology,
candidate WF2 sign-agreement matrix, before/after long-caption probes, candidate all-missing forcing map,
candidate captioned optional subbasin climatology and candidate synthetic multi-period cloud.
No visible extraction regression appeared. The coordinator independently inspected all 167 normal pairs
on 21 contact sheets plus representative full-size figures; its report is `../visual-review.md`.

Two pre-existing layout limitations remain deliberately unchanged: adding a short caption increases
physical axes height by 0.02946 inches, and a long caption by 0.29462 inches in this probe. The 351-year
fixed-width synthetic series crowds its decade labels. Both limitations reproduce before and after;
they are follow-up layout issues, outside this exact extraction. All-missing maps remain gray with an
otherwise uninformative default scale, matching pre-change behavior.

Omissions: no genuine retained multi-period ensemble was available; its coverage is synthetic.
Optional subbasin comparison recomputation and a 20+ model case were not run. The normal 13-model,
four-scenario case meets the stated 10–20-model density range. No independent numerical model validation,
fresh workflow execution, pytest, Ruff, broad suites or commits were performed by this agent; focused
checks belong to the implementation worker. Baseline retained-data and optional-overlay caveats still apply.

Pair paths: normal products have identical relative paths beneath `baseline/` and `candidate/`.
`normal-png-pairs.json` enumerates all 167. Supplemental products use identical relative paths beneath
`candidate/supplemental/before/` and `candidate/supplemental/after/`.
