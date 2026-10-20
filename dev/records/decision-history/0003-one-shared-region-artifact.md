# ADR 0003 — Share region and vector products without model-build dependencies

Historical decisions accepted and implemented 2026-08-02 and 2026-08-06 by Ümit Taner.
Condensed 2026-10-20; no calculations or timing probes repeated.

**Current authority:** [toolbox-spatial-foundation.md](../../reference/toolbox-spatial-foundation.md).
Current configuration names, identity encodings and capacities belong to their implementation owners.
This record preserves the reasons and measured consequences of the former changes.

## Context and decision

The model-free historical extraction and model spatial preparation originally delineated the same
region separately. On `gabon_0108`, their polygon unions and bounds were identical:
`[9.65833, 0.35, 9.85833, 0.48333]`. WF2 nevertheless depended on the historical extraction merely
to obtain its region polygon, paying for a multidecade climate read it did not otherwise consume.

The first decision created one project region producer from configuration and catalog inputs.
Climate extraction, projection reduction and spatial preparation consumed that artifact without a
built model. The extraction retained region content hash, bounds and source attributes instead of
a second `store_region.geojson`. Region cache identity followed polygon content rather than only
the configured region specification.

The second decision split vector/hydrography preparation from WF1's thematic land/soil preparation.
Shared vector consumers could bootstrap without resampling the thematic sources.
The full hydrography grid stack crossed that boundary as `hydrography.nc`, preserving one producer
per value. The model-facing catalog remained the responsibility of the thematic stage; the seam
file was deliberately not advertised as a model input.

Shared producer parameters were narrowed to their actual project/spatial inputs. A workflow-specific
config path or model settings in those parameters would have caused alternating workflow launches
to invalidate shared products unnecessarily.

## Partitioning and identifier choices

The former global automatic-subbasin budget became a per-parent ceiling. Its configuration key was
renamed rather than silently changing meaning, and the old key was explicitly rejected.
The historical default changed from 20 to 11 for per-basin figure legibility; this was not a claim
that a multibasin map with many more units would fit a single qualitative palette.

The old location IDs mixed small subbasin IDs and seven-digit additional-location IDs.
The chosen historical encoding was:

```text
wflow_id = basin_id * 1000 + local_subbasin_number * 10 + m
m = 0 for the primary; 1..9 for additional locations
```

It grouped CSV columns by basin and subbasin while preserving a readable location distinction.
The hierarchical `location_code` did not change. The old enforced equality between a primary
location's `wflow_id` and `subbasin_id` was replaced by primary identification through a final zero.
Outlet-map values retained subbasin IDs; observation CSVs and optional pinned gauge IDs needed
migration. Identifier assignments retained deterministic station/coordinate tie-breaking.

This section records the selected scheme; current code and the spatial reference govern changes,
limits and migration. It does not authorize an alternative encoding.

## Measured consequences

### Vector/raster split

The August 6 probe compared the two preparation halves on the real catalog:

| Duration | Fixture config | `config_gabon0108.yml` |
|---|---:|---:|
| Region delineation, already required | 5.58 s | 5.86 s |
| Added vector/hydrography stage | 3.65 s | 3.89 s |
| Unsplit stage would add | 13.03 s | 13.17 s |
| Thematic work avoided | 9.37 s (72.0%) | 9.28 s (70.5%) |

Region delineation was excluded from the saving comparison because it was required either way.
Both configs resolved to the **same 384-cell, 16 × 24 basin**. Fixed catalog/file-opening overhead
dominated; these were not two independent basin sizes and did not establish production scaling.
Rounded entries account for minor subtraction differences in the reported table.

Synthetic before/after hashing preserved nine product artifacts. Two serialization details mattered:
reading the seam with `mask_and_scale=False` preserved integer IDs and `_FillValue` semantics;
rebuilding coordinates first and restoring CRS from its EPSG code preserved serialization order/WKT.
Value equality alone would not have caught those type/byte differences.
The thematic-clip reprojection on a non-geographic grid remained unverified in this evidence.

### Ceiling and identity migration

The fixture's replayed partition counts were:

| Ceiling | 1 | 2 | 3 | 4 | 5–25 |
|---|---:|---:|---:|---:|---:|
| Produced subbasins | 1 | 1 | 3 | 4 | 5 |

Thus 11 and 20 produced the same fixture partition; this baseline could not test ceilings above five.
Synthetic multibasin tests instead covered independent parent ceilings and parent counts exceeding
the ceiling. That measurement justified combining the key rename and default change in one landing.

The identifier probe found two existing outlet/gauge columns both named `Q_101`, with maximum
absolute value difference zero. Pandas' de-duplication had leaked `Q_101.1` into an indicator output.
The new gauge name `Q_1010` separated columns already present; it did not add a new physical series.
The unchanged outlet anchor `Q_101` had mean `10.94766158`.

Baseline revision `ea5ac59` (2026-08-06) changed three configuration-snapshot hashes and indicator
column names; the discharge anchor, basin indicators and change-factor tables remained unchanged.
That was a dated result, not a statement that today's baseline is current.

## Alternatives and limitations

Depending on `basins.geojson` before separating the thematic stage would simply have replaced the
climate dependency with a large raster dependency. After the split, a plain region extent and an
exploded, identified basin product still had different meanings, justifying both artifacts.
Copying the region into each climate store would have recreated a drift-prone second owner.

Declaring vector inputs without their producer would have broken cold-project bootstrapping.
Adding a mandatory preparation workflow was deferred: it would remove repeated declarations but
also impose an execution prerequisite. The old “fourth shared rule or two drift failures” trigger
was a historical proposal, not a present architectural requirement.

A flat sequential basin-local gauge counter was rejected because it obscured subbasin membership
and visually overlapped the distinct subbasin-ID namespace. The selected scheme traded capacity for
readability: nine additional locations per subbasin. No real crowded gauge list was evaluated.
Overflow was rejected rather than allowed to collide; a larger encoding was discussed, not adopted.

The legacy workflow-local gauge fallback could silently yield automatic partitions after the split
unless users moved the setting to the shared owner. The tracked configs already did so.
This is migration evidence, not a continuing compatibility guarantee.

## Original section recovery

The full original, including superseded proposals and implementation chronology, is recoverable with:

```text
git show e9bbd72d:dev/records/decision-history/0003-one-shared-region-artifact.md
```

| Historical citation | Subject retained here |
|---|---|
| Decision §1–7; §5 | One region producer; removal of WF2's climate-extraction dependency |
| §8 / §8a | Vector/thematic split and full hydrography seam |
| §8b / §9 | Shared spatial-only parameters and common rule declaration |
| §10 | Reachability/consumer integration; historical gathers needed explicit completion edges |
| §11 / §11a / §11b | Per-parent ceiling, key migration and fixture saturation measurement |
| §12 / §12a / §12b | Location encoding, replaced validator invariant and observation migration |
| Landed state §8–10 | Serialization checks, complete seam and former compatibility limitation |
| Landed state §11 / §12 | Measured partition and outlet/gauge collision consequences |
| Open questions | Larger-basin scaling, crowded gauge capacity and future consumers were not established |

Earlier locations and the retired probe's recovery pin are listed in the
[decision-history migration map](../migrations/decision-history-transition-2026-10-20.md).
