# Clean pre-change WF3 scientific reference

- Captured 2026-09-21 on `refactor/workflow-layouts`, source HEAD `a1a97ffeccea41eed3d1bf449d94f0487121f300`. Repository code and catalogs were not edited.
- Both isolated fixtures completed Snakemake `all` with exit 0: automatic seed and matched explicit seed `123`. Each published a `scenario-collection/1` record with `status: ready`, two realizations, four perturbation points plus the unperturbed member, and ten retained forcing files.
- Reference owner: this P0 run. The corresponding output trees are under `.tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/{auto-c-root,explicit-123-c-root}/project/`. These are isolated scratch outputs, not `test_local` or `test_rapid`.

## Invocation and source recovery

The first retry of the original automatic fixture was blocked by an incomplete historical netCDF from the interrupted 2026-09-21 run. Adding `--rerun-incomplete` exposed a stale Snakemake workdir lock; adding `--nolock` allowed the job to run, which failed deterministically because `config/catalogs/deltares_era5_daily_zarr.yml` lists P-drive roots absent in this session. The same `meteo/era5_daily.zarr` store exists under `C:/data/wflow_global/hydromt`. The successful reference fixtures were **new** scratch fixture directories with a copied catalog in scratch; its only semantic edit was replacing the three P-root alternatives with `c:/data/wflow_global/hydromt`. The original repository catalog remains unchanged. The Zarr store identity is recorded below by root metadata and stage-file SHA-256; a full recursive hash of the large store was not computed. The successful extraction log identifies `c:\data\wflow_global\hydromt\meteo\era5_daily.zarr`, the requested period `2000-01-01..2016-12-31`, and two of 20 basin cells. No network input was needed after the root correction.

For each case, from the repository root:

```text
pixi run -x -- snakemake all -c 3 -s generate_scenarios.smk --configfile .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/<case>/config/project_config.yml --workflow-profile none --shared-fs-usage persistence input-output software-deployment sources storage-local-copies software-deployment-cache --nolock
```

`<case>` was `auto-c-root` or `explicit-123-c-root`. Standard output and error were redirected to `evidence/<case>.log` within the scratch reference directory. The full SHA-256 and numerical output listing follows. Earlier failed-attempt logs are `evidence/auto-retry.log`, `auto-retry-incomplete.log`, and `auto-retry-unlocked.log` there.

## Comparison method

For the automatic-seed fixture, verify that the pre-change `generation-seed-material/1` projection SHA, resolved seed, provider inventory, and collection identity below are recorded; the migrated `generation-seed-material/2` seed and collection ID may intentionally differ. For the explicit-123 fixture, compare decoded retained forcing values by run ID, variable, time, and cell using the same source store, input configuration, and provider versions. Require identical dimensions, coordinates, calendar, variable units, and missing-value masks. Use exact decoded equality when feasible; if a change in netCDF serialization or float conversion precludes it, report maximum absolute and relative differences for each variable and explain them before accepting. Do not treat netCDF byte inequality alone as a scientific difference. The first retained forcing file's numerical fingerprint below is a quick diagnostic; the full 10-file comparison remains a post-migration task.

## Fixed input, record, and forcing hashes

The fingerprint was produced by `pixi run -x -- python .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/fingerprint.py`; SHA-256 reads file bytes, while `SERIES_STAT` uses xarray decoded arrays and float64 accumulation over finite values. `spatial_ref` is a scalar metadata variable. Paths are relative to the repository root unless they start with `c:/`.

```text
SOURCE config/catalogs/deltares_era5_daily_zarr.yml 4fc56a9ae4fdf5ff926f9987cd7803e47140283847b56637ce9f503d9eacf65d
SOURCE .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/deltares_era5_daily_zarr_c.yml 60ee70b2699ef640a56a29555cf52f3232b642b87657cce5f9acd89a071a2c00
SOURCE c:/data/wflow_global/hydromt/meteo/era5_daily.zarr/zarr.json abd63b68fba9701d637f60eab28a15587a70ebb72f249b5c93cce717f2f2b04d
SOURCE c:/data/wflow_global/hydromt/meteo/era5_daily.zarr/.stage.json 66922ba3d2fecbcb4d8d1936e875a0f5ef5dc3ad58531177888ef58d99cb573c
CASE auto-c-root
CONFIG .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto-c-root/config/generate_scenarios.yml 921c58f6d4cd86414224f596443441c920e0879862eebb4940f790e1fe139fa5
CONFIG .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto-c-root/config/project_config.yml 49182b18fde75119b3099e499b873157fcea5be51bb98aa80d10a6f987737d30
IDENTITY {"collection_id": "77015f96a74bd57d7e9054701de18888031b9c86cf34c9f1a049076b6a2d2a90", "projection_sha256": "00a73c3dd0d98ac872bcdf07fceac36e554343ca3b8bc6f6080510b86481a02b", "schema_version": "scenario-collection/1", "seed": {"requested": "auto", "resolved": 1025369264}, "seed_resolution_id": "4c86436478e21d5fe3c26a08b59e0e03370ee0e7f55dba524d6e4cb6b1060d54"}
RECORD scenarios/collections/77015f96a74b/collection.json 641952e5b111b757ce6198c6df8fe7e509eb06ad32d250b4572bdfbe74ca5428
RECORD scenarios/collections/77015f96a74b/collection_intent.json e4ebb0910fba326f4ea4e26a29d13c2a3b41ee3e0410858ab3df12a4b84c6fdc
RECORD scenarios/collections/77015f96a74b/generation_config.json f4f9af6a3e5a5b214ca590f9e03fcdde5179839b7f737016d5ea9a5e29c8d3e6
RECORD scenarios/collections/77015f96a74b/generation_environment.json 91675bed30abc59f08deb1c9c0fe5b98aadc418248ffa4a35cac001135ea2bba
RECORD scenarios/collections/77015f96a74b/preparation_context.json 77baacaeb76b168c291bafa0f56831fba87546aff9ad734a1fc4eece8d7e17f1
RECORD scenarios/collections/77015f96a74b/provider_code_inventory.json 7fdba15e2792d594dd297e5fd71daa35c2a3f3f0165d2d69287e5c93f06844c9
RECORD scenarios/collections/77015f96a74b/source_inventory.json 5650e1c8fb784d55f511e5d5e5b757e034670f4144102393eca126ea8e4b15fb
FORCING scenarios/collections/77015f96a74b/forcing/run_01.nc 3a556028c0656ecd621ad71c26fa572991c1f908ee2d5028ae4952c41a5e840f
FORCING scenarios/collections/77015f96a74b/forcing/run_02.nc 2c8ff79383c175199adf60702b71be47fd04edcbdc41517f09697c3e3164138e
FORCING scenarios/collections/77015f96a74b/forcing/run_03.nc 1ec3ba4a17d80d9871813531943f11414e4a888ad33330c0bf6463fb35d92186
FORCING scenarios/collections/77015f96a74b/forcing/run_04.nc 21dec23ba1bce265fb658caf0cac4a0094dbfcccb916339b8b3aa80193ebbabd
FORCING scenarios/collections/77015f96a74b/forcing/run_05.nc 7fa067faf6a93afdcf2ceb67478001d44bc6e55ba6b142fb8522c03b1d1ba8e0
FORCING scenarios/collections/77015f96a74b/forcing/run_06.nc 1b047f79160bb6c22ab6c39b6b11a4d4822980224b5b38a8703bc749c9e1d346
FORCING scenarios/collections/77015f96a74b/forcing/run_07.nc 68b51e36c2c71fc49d308c237123ac428b767f8b1fe88610322e7c14a88969a4
FORCING scenarios/collections/77015f96a74b/forcing/run_08.nc 6dc9652fe4f4abd3c7e600bfa005278865eae0f867884d7ec9d3b94af6db14d9
FORCING scenarios/collections/77015f96a74b/forcing/run_09.nc ec4f5b0b34bf1354b91fb3108ecbd28fec856f5f813c200ff4831874d79ee69d
FORCING scenarios/collections/77015f96a74b/forcing/run_10.nc b49b3e0e867733208131a1505364e1c90e9255a33974c46ded8417388f4e96c4
SERIES_DIMS {"latitude": 4, "longitude": 5, "time": 16790}
SERIES_STAT kin {"count": 335800, "max": 293.15838623046875, "mean": 174.75165213580357, "min": 14.56506061553955, "sum": 58681604.787202835}
SERIES_STAT kout {"count": 335800, "max": 438.43829345703125, "mean": 415.6908236483494, "min": 384.728271484375, "sum": 139588978.58111572}
SERIES_STAT precip {"count": 335800, "max": 229.8300018310547, "mean": 7.004045143928185, "min": 0.0, "sum": 2351958.3593310844}
SERIES_STAT press_msl {"count": 335800, "max": 1018.9325561523438, "mean": 1011.7232246381659, "min": 1005.7739868164062, "sum": 339736658.8334961}
SERIES_STAT spatial_ref {"count": 1, "max": 0.0, "mean": 0.0, "min": 0.0, "sum": 0.0}
SERIES_STAT temp {"count": 335800, "max": 28.94000244140625, "mean": 25.462885726556102, "min": 19.8699951171875, "sum": 8550437.026977539}
SERIES_STAT temp_max {"count": 335800, "max": 35.3900146484375, "mean": 28.465268844595403, "min": 21.1199951171875, "sum": 9558637.278015137}
SERIES_STAT temp_min {"count": 335800, "max": 28.230010986328125, "mean": 23.360077052431635, "min": 16.230010986328125, "sum": 7844313.874206543}
CASE explicit-123-c-root
CONFIG .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/explicit-123-c-root/config/generate_scenarios.yml 8a02209f16507032bd03902a111ce97f12e0086d516e2ce2f1dec4fb959eff03
CONFIG .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/explicit-123-c-root/config/project_config.yml e1e06e1123bf9a0e376a4a6a15d6defe58c7c0744a268058544e6e57229db624
IDENTITY {"collection_id": "65651384a9fc32d957fffed48c8af6d652e589db72a6f89f5386e7f4e55fd756", "projection_sha256": "9dab2d7ff76a59d16fca21f207dcda37e6d298960b787bbc2c5d7918bf18d877", "schema_version": "scenario-collection/1", "seed": {"requested": 123, "resolved": 123}, "seed_resolution_id": "30d6102a0deeeea0e44138f7400749e1b4c55deb350e0f6a36938ee4b0c1f8fe"}
RECORD scenarios/collections/65651384a9fc/collection.json ec39b95bb853c77a548a7098d47217c13a07f69638097df25672397022d7a27f
RECORD scenarios/collections/65651384a9fc/collection_intent.json 3f94f0266b4d3f3c63cf44ee97ac63192228da64d9e0012e8fe68a408931c8f2
RECORD scenarios/collections/65651384a9fc/generation_config.json a3359334f02780e2347b823fb34eee3b898b07947750719841c1085b9eac5563
RECORD scenarios/collections/65651384a9fc/generation_environment.json 91675bed30abc59f08deb1c9c0fe5b98aadc418248ffa4a35cac001135ea2bba
RECORD scenarios/collections/65651384a9fc/preparation_context.json 77baacaeb76b168c291bafa0f56831fba87546aff9ad734a1fc4eece8d7e17f1
RECORD scenarios/collections/65651384a9fc/provider_code_inventory.json 7fdba15e2792d594dd297e5fd71daa35c2a3f3f0165d2d69287e5c93f06844c9
RECORD scenarios/collections/65651384a9fc/source_inventory.json c4eb955c7d5c7937c0cf7767bfd219bc87414f1cb596ead68bfb2032bd301601
FORCING scenarios/collections/65651384a9fc/forcing/run_01.nc 1f9748f99e0cdbf06c2f84285ccf94027fbb6a4326767f9c9704a84987f4ffc7
FORCING scenarios/collections/65651384a9fc/forcing/run_02.nc 3d3b9648a5ed059c6bd352196ca888d949143667893f6c6fe876a5abdd84f390
FORCING scenarios/collections/65651384a9fc/forcing/run_03.nc 361f1ce1ac49b9718881b39bdea7244d78b0e15ec321e334e147693e50b3ecc4
FORCING scenarios/collections/65651384a9fc/forcing/run_04.nc 7533f5b7557015e2bd15ccbd5853ac91751fdb1e1792cb09041809d233038be9
FORCING scenarios/collections/65651384a9fc/forcing/run_05.nc dd858f6acd64ebd2ba74e5bf2a1a8ad3337e018de1305c05a6e8440bfc2c4b25
FORCING scenarios/collections/65651384a9fc/forcing/run_06.nc 3eabfa0cf9250854ba94ef95343b375db78ef35209070577033e6389a4e56211
FORCING scenarios/collections/65651384a9fc/forcing/run_07.nc 692ecbd67155d05baaf2a45a81ca86b1faf127380f044b3856ce036832a1cde5
FORCING scenarios/collections/65651384a9fc/forcing/run_08.nc 17d4527a8344df772f143dd3818d203fcc0182ccb2b76ecdeba4d71855a4b7f4
FORCING scenarios/collections/65651384a9fc/forcing/run_09.nc f42274681f72b27c835b156f59dee04e9436e34ef4ee8a6d03fd422ffe0db1f8
FORCING scenarios/collections/65651384a9fc/forcing/run_10.nc a895864302447aff6c44545d4401aa2bed94e78bf05591158ce803b7f691add2
SERIES_DIMS {"latitude": 4, "longitude": 5, "time": 16790}
SERIES_STAT kin {"count": 335800, "max": 293.15838623046875, "mean": 174.46018933260987, "min": 14.56506061553955, "sum": 58583731.577890396}
SERIES_STAT kout {"count": 335800, "max": 438.43829345703125, "mean": 415.7102505662201, "min": 384.728271484375, "sum": 139595502.14013672}
SERIES_STAT precip {"count": 335800, "max": 229.8300018310547, "mean": 6.92428198265766, "min": 0.0, "sum": 2325173.889776442}
SERIES_STAT press_msl {"count": 335800, "max": 1018.9325561523438, "mean": 1011.7018531685716, "min": 1005.7739868164062, "sum": 339729482.29400635}
SERIES_STAT spatial_ref {"count": 1, "max": 0.0, "mean": 0.0, "min": 0.0, "sum": 0.0}
SERIES_STAT temp {"count": 335800, "max": 29.1199951171875, "mean": 25.490264106918616, "min": 19.8699951171875, "sum": 8559630.687103271}
SERIES_STAT temp_max {"count": 335800, "max": 35.3900146484375, "mean": 28.478442883017234, "min": 21.459991455078125, "sum": 9563061.120117188}
SERIES_STAT temp_min {"count": 335800, "max": 28.100006103515625, "mean": 23.388631558625594, "min": 16.230010986328125, "sum": 7853902.477386475}
```
