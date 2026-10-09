# Export mechanics rendering plan and evidence

Pre-change revision: `dbe6cbe6`, branch `refactor/t2610082103-shared-plotting`, session-1.
All generated output stays beneath this scratch root; production data and prior captures are read-only.

## Bounded plan

Reuse the frozen 36 WF2 ordinary/captioned figures and six WF1 station/basin figures in
`../candidate/`. Do not repeat the 116 WF0 diagnostic or nine forcing figures: their direct saves are
outside this packet. Reuse earlier retained input hashes and prepared-value provenance.

Capture seven additional baseline PNGs and two PDFs: spatial elevation, legacy model elevation,
categorical land cover, continuous clay content, and three precipitation-only legacy climate figures
from the existing deterministic test fixture. The thematic production API supplies both PNG and PDF;
elevation wrappers supply PNG only. Use default production DPI and styling, with scratch destinations.

Source/Pixi identity is in `baseline-source-hashes.json`. The new baseline driver will hash every
retained spatial/model input it reads and preserve its synthetic fixture and export inventory.
After the parent signals source-ready, rerender the 42 reused figures and nine new export files with
the same adapters, compare inventories, geometry, captions, prepared evidence and inspect PNG/PDF
representatives. No pytest, Ruff, broad gates or source/board/Git modifications are owned here.

Planned commands, from the worktree root:

```powershell
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/render-distinct.py baseline *> .tmp/scratchpad/shared-rendering/export-mechanics/baseline.log
```

Baseline command passed: seven PNGs and two PDFs, exactly the planned bounded set.
The generated synthetic legacy fixture is saved as `baseline/synthetic_legacy_inputs.nc`.
`baseline/input-hashes.json` identifies retained spatial/model data; `baseline/inventory.json` and
`baseline/export-metadata.json` record exported files, PNG pixels/DPI/metadata, PDF page counts and
MediaBox dimensions. The source branch and full revision were confirmed read-only after capture.

```powershell
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/compare.py *> .tmp/scratchpad/shared-rendering/export-mechanics/baseline-inventory.log
```

Baseline inventory inspection passed. Spatial elevation and categorical land-cover PNGs were opened and
readable, retaining their existing coordinates, gauge labels, legends and source footnotes.
Vector review is deliberately bounded: Pixi provides no Poppler, pypdf, PyMuPDF or pdfplumber.
No dependency was installed. PDF checks cover readable header/trailer, MediaBox, page count and supplied
metadata plus visual review of the paired production PNG. PDF rasterized visual parity is unverified.
The parent accepted this explicit gap. The current-figure legacy path writes three outputs and drains
its production figure bundles before return, as recorded in `baseline.log`.

## Candidate acceptance

The parent signalled source-ready before candidate execution. Candidate source hashes are in
`candidate-source-hashes.json` and `final-source-hashes.json`; their contents match exactly, confirming
that rendering sources and Pixi lock stayed stable through the checks. Environment remains Python
3.12.13, Matplotlib 3.11.0, Pixi default, Agg. No source edits or dependency installation occurred here.

```powershell
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/render-distinct.py candidate *> .tmp/scratchpad/shared-rendering/export-mechanics/candidate-distinct.log
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/render-wf2.py *> .tmp/scratchpad/shared-rendering/export-mechanics/candidate-wf2.log
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/render-evaluation.py --evaluation *> .tmp/scratchpad/shared-rendering/export-mechanics/candidate-evaluation.log
pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/compare.py *> .tmp/scratchpad/shared-rendering/export-mechanics/comparison.log
```

All commands passed. Candidate renders were run in parallel. The distinct driver's initial aggregate
summary included files concurrently written by the other drivers; its corrected scoped inventory lists
exactly nine distinct export files. The definitive comparison enumerates 51 affected export pairs:
49 PNGs and two PDFs. Neither the 116 WF0 direct-save figures nor the nine forcing direct-save figures
was rerendered. The 42 WF1/WF2 baseline products were reused without overwriting their frozen tree.

`comparison.json` and `pairs.json` record these results:

- All 49 PNG pixel dimensions, DPI and supplied metadata match.
- Both PDFs preserve PDF-1.4 headers, complete trailers, one-page counts, MediaBox dimensions and
  creator/producer metadata; CreationDate remains omitted as requested by the production API.
- Eight caption, record, metric, input-hash and cell-weight artifacts are identical.
- New spatial/model input hashes, synthetic legacy fixture values, and reused station input/prepared
  hashes match. No new numerical method or independent model validation is claimed.
- Production spatial/legacy and WF2 log rows match after normalizing timestamps and output roots.
- Assert-bearing comparison command exited zero. No image-byte comparison is an acceptance oracle.

The agent opened baseline spatial elevation and land cover; both clay-map PNGs; candidate legacy
precipitation annual series, station hydrograph and captioned WF2 change cloud. No visible export
regression appeared. The clay colorbar title meets/clips the upper canvas edge identically on both sides;
this inherited composition issue is retained, outside export mechanics. PDF rasterized appearance remains
unverified because the approved environment has no PDF rasterizer; paired PNG review and the explicit
structural checks above are the bounded evidence, accepted by the coordinator.
The coordinator additionally inspected all 49 PNG pairs on nine contact sheets plus the full clay map
and captioned WF2 cloud, reporting no new visual regression and confirming inherited clay-title clipping.

New export pairs use identical relative paths beneath `baseline/` and `candidate/`; reused products
compare `../candidate/{wf1/evaluation,wf2/plots}/` with the corresponding directories in this packet's
`candidate/`. `pairs.json` records exact before/after paths for the coordinator's comparison page.
No additional renders are needed. Preserve this scratch tree for user review. No pytest, Ruff, full
suite, fresh workflows, source edits, Git operations or task-board edits were performed by this agent.
