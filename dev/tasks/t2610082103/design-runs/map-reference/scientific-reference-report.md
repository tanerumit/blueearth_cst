# Historical map-reference scientific checkpoint

**The scientific checkpoint passes after the second bounded class-threshold correction.**
All 54 narrow correction checks pass, including strict next-representable endpoints. Prior executed
scientific support, payload integrity and renderer-meaning cases also pass. Consumers remain outside this
checkpoint. The independent probe completed on pinned, unchanged source and lock bytes.

Approved design SHA-256: `4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
Tested `map_reference.py`: `402ebdaa27f11a48b8c44390a0262316ed6782cac25d043cf92fdf3b7493ad21`.
Tested `prepared_maps.py`: `fb407e14d43c49542a4227b6426f6cb12443ca5ceb65adb13b2415dd7e827595`.
The log includes all reference/preparation closure and lock hashes, before and after execution.

## Final correction verdict

Final corrected `map_reference.py` SHA-256:
`00d12496d6681dfd845b4cd58ba75b7f38e73240e3cb855d82f3ccb2a3cdc332`.
`source_map_fields.py` remains `52024bde2d80bbe3158dff175f31d108f7ebd1285d628700da4f6eb677abe763`;
the portable renderer remains unchanged. The second correction applies the endpoint guard to both
subtraction branches, resolving the two failures below without widening the threshold.

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-probe.py classes > .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-classes-r2.log 2>&1
```

Exit 0: **54 passing checks, zero failures**. All source/lock bytes are unchanged between run start and
completion. Exact translated 1.6-degree spans `20→21.6` and `−2.1→−0.5` select 0.2-degree steps;
their next representable upper endpoints select 0.5. Exact 4-degree spans `20.1→24.1` and `−0.1→3.9`
select 0.5-degree steps; their next representable upper endpoints select 1.0. Materially larger spans,
the original constant/boundary cases and actual artist endpoint/under/over checks also pass.

This is a demonstrated red/green correction with retained failed logs. No tolerance in the oracle was
widened. The checkpoint reuses the unchanged pooling, role, integrity and unscaled-rendering findings
instead of rerunning expensive unrelated preparation. The producer's new identity-return plumbing is
recorded as a code-closure delta; its engineering acceptance and integrated consumers remain root-owned.

## First correction: narrow rerun

The original defect is fixed in `map_reference.py` SHA-256
`0377f49a8508db9f995ec1da6ff78fc5724455ecb3a0e4c22152649af8d2b8dd`.
The closure delta from the first pinned run is exactly two paths: `shared/map_reference.py` (threshold
correction and producer identity handoff) and `climate_analysis/source_map_fields.py` (explicit preparation
identity return, SHA-256 `52024bde2d80bbe3158dff175f31d108f7ebd1285d628700da4f6eb677abe763`).
The scientific preparation algorithms, renderer, other closure files and locks are unchanged.

The rerun adds translated exact thresholds and their next representable upper endpoints at positive and
negative/cross-zero locations, plus materially wider spans. Source/lock bytes remained unchanged during
the rerun. Positive translated controls pass; these two strict wider-span controls fail:

| Lower value | Upper value | Rounded subtraction | Expected step | Actual step |
|---|---|---|---|---|
| −2.1 | `nextafter(-0.5, +inf)` = −0.49999999999999994 | 1.6 | 0.5 | 0.2 |
| −0.1 | `nextafter(3.9, +inf)` = 3.9000000000000004 | 4.0 | 1.0 | 0.5 |

Their exact endpoints −0.5 and 3.9 correctly select the narrower step. The early `span <= threshold`
branch still bypasses the new endpoint guard when subtraction rounds a slightly wider interval to the
threshold. This is fresh diagnostic evidence about the incomplete correction, not a repeated identical
failure. Root and engineer were informed; no reviewer source edits occurred.

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-probe.py classes > .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-classes-r1.log 2>&1
```

Exit 1: 52 checks pass and 2 fail. Targeted scratch Ruff lint and format checks pass.
The prior independent pool/canonical/render
meaning results remain bounded evidence for unchanged behavior; they were not needlessly repeated.

## Initial defect and retained red evidence

`scale_record("temp", 20.0, 21.6)` returns boundaries `[20, 20.5, 21, 21.5, 22]`.
The approved 1.6-degree span calls for 0.2-degree classes:
`[20, 20.2, 20.4, 20.6, 20.8, 21, 21.2, 21.4, 21.6]`.
The translated case `[0, 1.6]` passes. Floating subtraction yields
`21.6 - 20.0 == 1.6000000000000014`, selecting the next step incorrectly.

Classification: numerical implementation defect affecting displayed classes, not source-field science.
It changes the number of classes and outer scale boundary. Root and engineer received the exact falsifier.
No source fix was made by this reviewer. The narrow class-only red/green reruns above verify its correction;
unchanged pooling and integrity checks were not repeated merely because code identity changed.

## Executed independent known answers

The scratch producer inputs are 365 daily values in 2001, on explicitly declared EPSG:4326 native grids.
Expected amounts are daily constants multiplied by 365. Expected intersection populations are obtained
from hand-enumerated cell rectangles, not from production intersection results. No real data were sampled.

| Claim | Independent expectation | Actual result |
|---|---|---|
| Selected 2 × 2 CHIRPS frame | `[0, 2, 0, 2]`; aspect `1/cos(1°)` | Exact |
| Selected precipitation | 365, 730, 1095 mm/year; one unavailable cell | Exact |
| Unequal extra descending 4 × 7 grid | 16 closed-frame intersections, all finite | Exact |
| Combined finite pool | 3 + 16 = 19 cells; extrema 365 and 3650 | Exact |
| Boundary-only corner cell | Rectangle `[2,3] × [2,3]` contributes 3650 | Included |
| Larger disjoint cell | Rectangle `[3,4] × [2,3]`, value 365000 | Excluded |
| Entirely disjoint extra source | No scale expansion; 3 finite cells, extrema 365–1095 | Exact |
| All-missing selected source | Unavailable scale, no boundaries, zero finite pool | Exact |
| One-cell source with explicit resolution | Edge touch included; 0.0001° separation excluded | Exact |
| Descending native coordinates | Preserved descending cell edges | Exact |
| Missing/negative one-cell resolution, irregular grid | Rejected | Rejected |

Selected CHIRPS retains its synthetic auxiliary 99 degC temperature field and 364635 mm/year PET field,
including their counts/masks. Both auxiliary reference pools remain unavailable with count zero because
of the precipitation-only source role. The scientific preparation entry agrees with the producer's
record and passes `validate_fields`. These auxiliaries test ownership; they are not physically plausible
climate or PET estimates. Reference building used actual preparation and identity functions without mocks.

## Payload integrity and canonicalization

Actual sealed payload mutation, followed by `validate_fields`, rejects fractional eligible count 0.5,
unavailable-mask value 2, wrong precipitation units, altered longitude resolution and altered reporting
period start. This tests actual arrays/attributes, not only stored digest text. All five corruptions
are rejected; the three geometry rejections above account for eight deliberate refusal checks in total.

Canonical payload checks pass: positive and negative zero hash equally; different NaN bit patterns and
NaN signs hash equally; positive and negative infinity hash differently. No source/forcing infinity
semantics were unified. This checkpoint checks payload identity, not a new physical interpretation of
nonfinite values.

## Classes and rendering meaning

Actual rendered mesh normalization agrees with independently evaluated left-closed intervals at every
tested boundary and its adjacent floating values (`nextafter` below/above). The exact final upper endpoint
uses the final class; strictly greater values use the explicit over color. Strict under values use the
under color. Constant precipitation and temperature scales use their darkest single-class colors.
All class boundaries are colorbar ticks; colorbars have both rectangular extensions. The failed translated
1.6-degree case still classifies values correctly within its incorrect class set; that does not rescue
the step-selection defect.

The unscaled renderer probe has two finite inside cells, two missing inside cells, a finite outside cell,
a missing outside cell and uncovered frame area. Artist inspection confirms exactly two neutral hatches,
gray missing cells, white outside/uncovered areas and no numerical colorbar. Input arrays are unchanged.
The saved `scientific-reference-cases/unscaled-meaning.png` was opened: those meanings are visually clear,
with no clipped labels. This is a mechanism check under the core's default style, not acceptance of final
workflow typography, captions, overlays or all map products.

## Commands and bounded verdict

```powershell
pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-probe.py > .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-final.log 2>&1
pixi run ruff check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-probe.py
pixi run ruff format --check --no-force-exclude .tmp/scratchpad/shared-rendering/map-reference/scientific-reference-probe.py
```

Completed probe: exit 1, **73 passing checks, 1 failed check, 8 required refusals**. The failed check is
the class-step case above. The first attempt, retained in `scientific-reference-probe.log`, stopped at a
scratch color-inspection error because a Matplotlib scalar RGBA return was a tuple; the scratch probe was
corrected without changing production code. Final targeted Ruff lint/format checks passed before the
subsequent addition of the narrow rerun mode. No permanent tests, Git commands, workflows, installations,
network calls or production edits occurred.

Numerical verification is targeted and affected; physical model validation, observation errors and
structural uncertainty are not estimated. Source preparation and native pooling satisfy these cases,
and the class-step correction passes its independent oracle. Consumer captions, strict support counts in captions,
paired workflow routes, stale-field repair, final visual/inventory acceptance and full gates remain
parent-owned pending work. This evidence is tied to the pinned bytes above, not mutable future code.
