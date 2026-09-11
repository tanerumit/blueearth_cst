# P2 portable preparation handoff

**ACCEPT — bounded GF-31 physical preparation**, 2026-09-11.
Reviewer: Astra `model-validator` (`/root/model_validator_p2`). This permits
integration of the reviewed preparation binding, not acceptance of all P2.

The real NetCDF readers extract calendar, endpoints, timestep, coordinate/CRS
identity, effective units and native missing-value encoding. Native elevation
files can lack embedded CRS; the descriptor records that absence while the
packaged catalog retains its CRS declaration. Values and native metadata are not
converted. The producer packages the selected elevation bytes and original
reader/adapters. The consumer validates the retained collection before writing
its temporary catalog, then obtains PET and elevation from persisted context.

## Comparison and independent review

The [retained probe source](portable-preparation-probe.txt) used one frozen P0
ERA5 generated member, constant synthetic source-grid elevation and simplified
catalogs. The model was copied into scratch. It compared the existing and
portable preparation paths for ERA5, CHIRPS, CHIRPS-global and the dormant E-OBS
Makkink branch. Original fixture directories were renamed before portable
consumption. Legacy preparation ran in a child process so Windows closed its
file handles before that rename. The initial same-process attempt stopped at
the rename; it supplied no completed comparison.

[Machine-readable comparisons](portable-preparation-comparison.json) identify
each retained old/new artifact. All four passed `xr.testing.assert_identical`.
Each prepared array has 3,287 daily steps × 16 latitude × 24 longitude.
The probe reported an allowed `input.path_forcing` exclusion, but independent
review found that pointer identical too: **complete parsed TOMLs match**.

The reviewer independently repeated all four array/TOML comparisons and all four
`read_collection` validations, including hashes and physical descriptors. An
in-memory +1 mm precipitation perturbation failed equality, demonstrating that
the numerical comparator is discriminating. Original `live` paths were absent.
Changed-ancillary tests establish refusal before temporary catalog creation;
the same pre-output validation rejects missing files, descriptor drift and
unconfined or uninventoried catalog targets.

The independent checks read existing artifacts only. A GDAL data-location
warning appeared; assertions completed successfully. No new tolerance or owner
approval gate was introduced. Verification posture: rapid / numerical affected.

## Commands and limits

Executed in the existing Pixi environment:

```text
pixi run --as-is python .tmp/scratchpad/2026-09-11_0010/probe-portable-preparation.py
exit 0; all four branches PASS
```

Artifacts and full log remain under `.tmp/scratchpad/2026-09-11_0010/`:
`gf31-physical-2/` and `gf31-physical-2.log`. A separate read-only resolver probe
successfully resolved the actual ERA5 catalog and its 10,718-byte native elevation
file (`real-preparation-plan.log`); that is not an actual-catalog preparation
comparison.

Acceptance establishes fixture-based preparation portability. It does not
establish production source/code/environment inventory completeness, generator
identity, actual CHIRPS climate numerical equivalence, E-OBS production support,
Wflow response equivalence or full P2 acceptance. E-OBS retains its existing WF1
refusal. Native metadata inconsistencies remain documented in the P1 unit
handoff. No observational validation, predictive uncertainty or held-out model
skill is claimed.
