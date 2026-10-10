# Final scientific map checkpoint

The final reference producer, native drawing core and tested consumer science pass this checkpoint.
The retained WF1 maps pass numerical, inventory and visual acceptance. Fresh WF0 source figures also
pass the final visual checkpoint below. Route equivalence, repair/publication behavior and cost
acceptance remain coordinator-owned.
This is implementation acceptance against approved scientific semantics, not physical climate or
hydrological validation against observations.

Approved design SHA-256: `4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
Executed 2026-10-10 using the existing Pixi environment. No source edits, Git operations, installs,
workflows, nested delegation or external transmissions were performed by this reviewer.

## Candidate and prior evidence reuse

Final tested core hashes:

| Path suffix | SHA-256 |
|---|---|
| shared/map_reference.py | `2ed1a9b87ebf2be69a4d5ebed6eae007f0a422d8591d0a1c9c0427ae7902fc24` |
| climate_analysis/source_map_fields.py | `9ee77e5f089fc6c721edead7c2ac55da8ae9e843d159c7cf4cdb484a3ecd6193` |
| plotting/prepared_maps.py | `35e185111061f9f0d3d66e6035c0468e1722965af8dd58c4371f50c7fc0b0b1f` |
| climate_analysis/diagnostic_render.py | `a1c9b0d5d4561bced8f8d4bd10536a9557edc2afb9bf08d47f6fb326bf8531a5` |
| model/forcing_figures.py | `f45046a5ec27298c64f274e2999c060a981de5e0f655b7d37323ca1de55c902a` |

Each phase logs the complete preparation/rendering closure and proves it unchanged during execution.
The full reference probe additionally records the unchanged Pixi/Julia lock hashes. The final closure
includes the explicit verified preparation-identity return and the dtype-aware native-edge correction.
Relative to the source-preparation checkpoint, those changes concern identity and edges; annual
scientific calculations are unchanged. Retirement of unused artists in diagnostic_maps.py preserves
annual_fields verbatim. The last caption changes affect diagnostic_render.py/forcing_figures.py,
outside the preparation/reference identity closure, and received targeted caption checks below.

Reuse scientific-report.md for independent calendar known answers and scientific-preparation-report.md
for complete exact native-field comparisons, unit/PET gates and retained auxiliary fields. Those reports
remain unmodified and explicitly state their earlier checkpoint boundaries. The reference checkpoint's
previous decimal-threshold failures and the corrections remain in its original logs/report.

## Executed final checks

All commands below use prefix `pixi run python` and script paths relative to this scratch directory.
Logs are retained here; every listed final command exited 0.

| Command suffix | Evidence log | Outcome |
|---|---|---|
| scientific-reference-probe.py | scientific-reference-final-closure.log | 74 passing checks, 8 required refusals |
| scientific-consumer-probe.py precision | scientific-consumer-precision.log | Three complete real CHIRPS grids |
| scientific-consumer-probe.py real-pool | scientific-consumer-real-pool-final.log | Independent real producer pools |
| scientific-consumer-probe.py raw-inputs | scientific-consumer-raw-inputs-final.log | Exact ERA5 semantic identity |
| scientific-consumer-probe.py adapters | scientific-consumer-adapters-final.log | Support, infinity, nonoverlap, unscaled |
| scientific-consumer-probe.py caption-branches | scientific-consumer-caption-branches.log | Actual bounded caption branches |
| scientific-consumer-probe.py retained | scientific-consumer-retained-support.log | Full retained parity and scalar counts |

The scratch probe was formatted with `pixi run ruff format --isolated --no-cache` and checked using
`pixi run ruff check --isolated --no-cache --select E,F --ignore E501` on its exact path: pass.
Initial default Ruff calls skipped ignored scratch; they are not counted as checks. Broader isolated
lint reported scratch-only exec/noqa/style findings; the intentional bounded AST execution is documented.

The complete producer/core probe independently exercises selected enriched CHIRPS auxiliary retention
and exclusion from temperature/PET pools, closed boundary-touch pooling, disjoint/unequal/descending
and one-cell grids, constant/all-missing scales, exact and adjacent class endpoints, visible under/over
artists, finite unscaled hatching, corruption of fractional counts/mask=2/scientific attributes, canonical
signed zero/NaNs, and distinct signed infinities. It passed on the final code closure.

Actual CHIRPS coordinate vectors from fresh before-project (5x6), existing rapid (7x8), and retained
Liberia (40x39) were checked in full. Both axis-edge arrays equal the independent old arithmetic
exactly, including float32 dtype; actual core renders succeed. The same quantized coordinates cast
to float64 and a materially irregular float64 sequence are refused. No coordinate subsampling occurred.

## Fresh real producer oracle

Reference: candidate-wf1-only/data/climate/historical/_engine/map_reference.json.
Reference ID: `637d200ae97fcab9c14246b004a6644b40667e0eb8b2affa29063246e6f056b1`.
The selected ERA5 frame equals independent old edges, `[9.375, 10.125, 0.125, 0.625]`.
Scalar closed rectangles, without frame_intersection, independently reproduce the following pools.

| Variable | Finite population | Minimum | Maximum |
|---|---:|---:|---:|
| Precipitation | 35 | 2360.604248046875 | 2936.814453125 |
| Temperature | 6 | 25.04983139038086 | 25.912567138671875 |
| Source PET | 6 | 1032.9930419921875 | 1157.6995849609375 |

CHIRPS contributes 29 finite of 30 intersecting precipitation cells; ERA5 contributes all six cells
to each variable. All retained scientific-field payload digests exactly equal the producer record.
CHIRPS extraction bytes match the before capture. ERA5 extraction bytes differ, but
`xarray.testing.assert_identical` passes for the entire 6,210-day dataset, seven variables, coordinates
and all scientific attributes. That semantic equality permits this numerical oracle; it does not
establish byte identity or route-equivalent reference IDs. No provenance rule was relaxed.

## Consumer scientific meaning and retained WF1

A controlled actual prepared_map call contains six displayed cells: four finite, two unavailable,
eligible count range [1,1], one strictly under and one strictly over. The exact upper endpoint remains
in the last class. Reference completeness 27/1000 is reported literally. A finite field against an
unavailable historical scale uses neutral hatching and no numerical colorbar.

An actual all-infinity daily dataset produces annual count 1 but unavailable annual values. This
discriminates the earlier false no-eligible-years wording. The corrected caption states that gray
cells have no finite annual climatology. A disjoint field has eight native finite cells and zero
displayed cells; the caption explicitly states that no native support intersects the frame.

Verbatim bounded AST execution of the current consumer caption branches confirms no-intersection
availability takes priority over missing/unscaled in both adapters. Producer role names are exactly
`temperature-carrier` and `precipitation-only`; ERA5 PET gets the de Bruin statement, while CHIRPS
auxiliary PET/temperature get the retained-field/excluded-pool statement. This is actual branch
execution plus the actual prepared_map calls above, not a claim of a full new synthetic WF0 render.

Against before-retained/wf1, candidate-retained/wf1 has exact xarray identity for all nine native
scientific/count/mask arrays on the complete 16x24 grid, six byte-identical CSVs, six byte-identical
temporal PNGs, and the exact nine canonical forcing PNG inventory. No fields/cells/years were dropped.
Independent old-edge scalar rectangles plus the static basin mask reproduce the map metadata:

| Field | Displayed/finite/unavailable | Eligible years | Strict under/over |
|---|---|---|---|
| Precipitation | 257 / 257 / 0 | 7 / 7 | 0 / 0 |
| Temperature | 257 / 257 / 0 | 7 / 7 | 3 / 145 |
| Model PET | 257 / 257 / 0 | 7 / 7 | 0 / 0 |

Captions distinguish forcing 2010-2016 from historical reference 2000-2016, preserve forcing 3/15
completeness, report actual eligibility and support, and retain source/model PET method distinctions.
All three retained map PNGs were opened and visually inspected: common viewport/ticks, visible gauge
labels and overlays, gray missing/white exterior semantics, class bars with both rectangular extensions,
and no observed clipping/overlap. Temperature's extensive over-color agrees with 145 over cells.
The wide white surroundings follow the selected coarse ERA5 reference frame and are intentional.

## Verdict and remaining coverage

Fit for the approved display-comparability purpose within the tested native EPSG:4326 rectilinear
grids, annual-completeness policies and source roles. Evidence supports unchanged scientific arrays,
honest missing/nonoverlap/under-over interpretation and a reproducible shared display reference.
It does not establish climate-product accuracy, observation agreement, source/model PET equivalence,
or hydrological predictive adequacy. No observational or ensemble uncertainty was estimated; this
deterministic preservation review cannot quantify those uncertainties.

Coordinator still owns workflow route equivalence under matched bytes, repair/publication guards,
execution costs and final gate reconciliation. The source/consumer checkpoints are complete and should
not be represented as those remaining gates.

## Final fresh WF0 visual checkpoint

All four ordinary fresh source maps and all four optional captioned variants were opened and inspected.
Ordinary products are under candidate-wf0/data/climate/historical/{era5,chirps}_20000101_20161231/plots/;
captioned products are under candidate-retained/wf0-captioned/{era5,chirps}/captioned/.
The inventory is ERA5 precipitation, temperature and PET, plus CHIRPS precipitation.

Visual verdict: pass. The four source maps share the selected ERA5 viewport and geographic ticks.
Their native 2x3 and 5x6 grids remain visibly distinct, with identical precipitation class encoding.
CHIRPS's one gray unavailable cell is distinct from white outside raster coverage. Gauge labels and
basin/subbasin overlays are legible, and class bars retain both rectangular extensions. The captioned
variants keep complete wrapped captions below the coordinate-axis labels without overlap or clipping.
The source PET caption explicitly identifies de Bruin preparation and possible difference from model PET.

The final coordinator parity evidence (wf0-parity.log and wf0-parity-summary.json) covers 12 native
scientific/count/mask arrays, 54 CSV tables and 51 unchanged temporal PNGs, with four ordinary maps.
These final totals supersede the earlier source-only interim counts of 36 CSVs and 34 temporal PNGs.
I read this completed evidence; the coordinator executed the full comparison. Independently reviewed
map metadata agrees with the scientific pool oracle: CHIRPS 30 displayed, 29 finite, one unavailable;
all three ERA5 maps six displayed/finite, zero unavailable. All have [17,17] eligible years, 0/0 strict
under/over counts, 2000-2016 periods and 3/15 completeness.

A suspected absence of CHIRPS axis labels in my preview interpretation was investigated and rejected.
scientific-image-label-probe.py performs read-only pixel checks on the exact ordinary and captioned
files. CHIRPS and ERA5 precipitation have identical left coordinate-label strips and identical bottom
coordinate-axis strips in each variant; the left strips contain 5,725 dark pixels ordinary and 6,557
captioned. The coordinator independently opened the exact images and confirmed all labels. No source
change occurred. This was a preview-reading error, not a rendering defect.

The label evidence log records complete file SHA-256 values. In particular, final captioned CHIRPS is
`c0e906040471ba73cc4300ffca592c823e62d3da3c71050982b94196eb007465`; ordinary CHIRPS is
`947d683a1ae30ba1ff07c851529603113cb4f17e8b60a99f7e5abda4c15b9f97`.
The final caption capture log source-captioned-declared.log reports three ERA5 and one CHIRPS pair.
Earlier scratch capture failures arose from staging output roots/metadata/declarations and did not
indicate source defects. Consumer source hashes still equal the table above.

This completes scientific preservation and visual acceptance for the affected source and forcing map
rendering functions, including ordinary and captioned source output. No additional Liberia figure
regeneration is needed for this checkpoint: its complete native science was separately compared, while
the four fresh source and three retained forcing maps exercise the affected render functions.
