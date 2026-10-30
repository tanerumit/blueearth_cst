# CIESM source-quality investigation and exclusion verification

Date: 2026-10-30. Retained evidence for the complete CMIP6 `THU/CIESM` exclusion.
The current behavior is documented in
[WF2's technical manual](../../../docs/technical-manual/workflow-analyze-projections.md).

## Source diagnosis

The retained Egypt run `wrt-egypt-v2`, under `data/climate/projections/cmip6/`, has a CIESM
1985–2004 reference mean of 0.1115142195 mm/year (0.0003055184 mm/day). Its annual anomalies
are marked dry while absolute values remain finite. The historical scalar mean is
0.0003073052 mm/day; other retained models range from 0.0633794 to 0.4782602 mm/day.

The tiny scale already occurs in the acquisition cache, before spatial reduction:
0.0003087567 mm/day for historical, 0.0003160028 for SSP126, 0.0002959391 for SSP245,
and 0.0002987023 for SSP585. These are spatial/time means, not weighted basin reference means.

Direct metadata reads and first-month global fields from all four pinned public Zarr stores
confirmed that the anomaly predates WF2. Each declares `kg m-2 s-1`, original name `PRECT`.
The global diagnostic was `sum(pr * cos(lat)) / sum(cos(lat)) / nlon * 86400` at time index zero.

| Experiment | Version | Global mean (mm/day) | Global maximum (mm/day) |
| --- | --- | ---: | ---: |
| historical | v20200417 | 0.0030045478 | 0.0421855077 |
| ssp126 | v20200417 | 0.0029526440 | 0.0371448435 |
| ssp245 | v20200417 | 0.0029537240 | 0.0371140540 |
| ssp585 | v20200605 | 0.0029874603 | 0.0452251621 |

Store pattern: `https://storage.googleapis.com/cmip6/CMIP6/{activity}/THU/CIESM/`
`{experiment}/r1i1p1f1/Amon/pr/gr/{version}/`; metadata is `.zmetadata`.
Activity is CMIP for historical and ScenarioMIP for SSPs. Only the first monthly field of
these four r1i1p1f1 stores was sampled (January 1850 or January 2015).

WF2's multiplication by 86400 is correct for the declared units. A missing upstream factor
of 1000 is plausible but unverified; these measurements do not justify automatic rescaling.
[Monerie (2026), section 4](https://doi.org/10.1088/2515-7620/ae661c) independently reports
CIESM precipitation as abnormally low, suspects post-processing and recommends avoiding it.
The user chose full-model exclusion for ensemble consistency; the measurements establish a
precipitation defect, not a defect in every variable.

The direct source reads completed successfully with anonymous gcsfs and xarray. An ignored
gcsfs/aiohttp shutdown callback reported a cross-event-loop error after all results were printed;
the process exited zero. Separate HTTPS metadata reads also succeeded.

## Implementation and checks

The resolver rejects every requested CIESM combination before acquisition, regardless of member
selection or overrides. Coverage and composition retain the reason. Provenance retains explicit
source-quality exclusions, and the report names them. Stage-B settings include the exclusions so
old reporting refreshes even without prior Snakemake metadata. Existing source caches remain intact.

- Regression proof: the new exclusion cases failed under both member-selection policies before repair.
- Resolution and analysis producer: 47 tests passed. The producer check compares every scientific table
  with the valid-model baseline, checks both variables, and preserves an unreadable excluded cache.
- Coverage: five existing tests passed; quality-exclusion coverage also passes in resolver tests.
- Stage-B script execution, provenance and report: 60 tests passed, including native script execution
  with identity-checked fixture series and explicit CIESM exclusion records.
- Four WF2 DAG checks passed with normal Windows permissions: ordinary WF2, shared store versions,
  mixed valid/CIESM ensemble, and CIESM-only refusal. The mixed case also checks the settings stamp.
- Scoped Ruff lint/format, Python compilation and whitespace checks passed.

The tests cover processing and declared inputs; they do not certify new remote acquisitions or a
whole-toolbox numerical baseline. The two existing xarray `drop` deprecation warnings remain.

Commands supplying the focused evidence:

```powershell
pixi run pytest tests/test_resolution.py tests/test_projection_coverage.py tests/test_derive_change_factors.py tests/test_prepare_projection_analysis.py -q
pixi run pytest tests/test_resolution.py tests/test_prepare_projection_analysis.py -q
pixi run pytest tests/test_derive_change_factors.py tests/test_provenance.py tests/test_report.py -q
pixi run pytest tests/test_cli.py -q -k 'wf2_dag_excludes_ciesm or snakefile_cli_analyze_projections or wf2_dag_accepts_shared_newest_store_pins'
```

## Independent retained-run numerical check

Reading `analysis/member_anomalies.csv` from the retained Egypt run directly with PowerShell,
without native reduction functions, gives 38 models before exclusion and 37 afterwards.
For SSP245, 2050 precipitation, the member minimum changes from 0.13770931878642045 to
14.457815910078352 mm/year when `THU/CIESM` rows are excluded. This independently confirms
the annual overview's lower-envelope effect. The regression producer compares all scientific
tables against a valid-model-only baseline for both precipitation and temperature.

The production run and its figures were not overwritten. Existing cases need WF2 rerun after
integration; the changed input set and settings stamp schedule their derived products again.
An optional full retained-table reconstruction was stopped because it repeated costly unchanged
model-local work. It is not counted as passing evidence; its scratch and logs remain local.
