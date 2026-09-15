# GF15 production Stage 1 readiness discovery

Driver retention: source-inventory.json, snapshot-result.json,
base-environment.json, study-environment-recheck.json and reader.log are copied
verbatim beside this record. Scratch references below describe their original
capture locations; the sibling copies are the durable evidence.

Subsequent driver status, 2026-09-14: [independent snapshot integrity review](snapshot-integrity-review.md)
passed, conditional on preserving the original collection anchor. References
to outstanding integrity review below describe the discovery-time handoff;
isolated setup/Linux qualification remains outstanding now.

Date: 2026-09-14. Discovery source HEAD: `33c893502e399b7446d461ee851f849058505e72`.
Authority: accepted production adapter D7–D8 and Stage 1 brief. Discovery found
the retained comparison; the driver subsequently captured its read-only
snapshot. **Independent integrity acceptance and Stage 1 setup remain
outstanding.** No solve, install, fit, workflow run, source-project mutation or
implementation was performed.

## Retained comparison found

P3 `../p3/execution-evidence.json` selects its `artifacts.direct.paths` without
timestamp inference. Let `ROOT` be
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3` and `SOURCE` be
`ROOT/.tmp/scratchpad/2026-09-11_0010/p3-final-direct`.

Current `blueearth_cst.experiment.metric_plan.read_metric_set` successfully read
`SOURCE/project/experiments/p3_final` and its recorded metric manifest: `ready`,
756 complete keys, 700 q rows and 56 gwr rows. This is retained predecessor
evidence, not candidate-C adequacy. Selected identities:

| Field | Value |
|---|---|
| Collection | `71bf34ef8db1122bb91f097ac63ff01e450cf0a16ad9a9d3cca64128fd23ba88` |
| Revision | `5c21f75dc5cc4354ee32bd9983e1a39d55fea09944eb5bc20657dd8318010885` |
| Simulation | `3a8c1fc6c633687bb95736f3c5f76cf8ac323927db32af7f767f8bde03a41a10` |
| Response inventory | `3238e59a15148e94b64c3c3d7f8639a3da9a5623cd329ec4ec9cc4afe5300eb1` |
| Metric set | `49ca015882e8396f4fd46930b9a95be3ccbd4dfcaf2d5c7840bf1b3df95aa665` |
| Metric manifest bytes | `74095313f3c83d1749a65a0a7ddafb59213e740bd69590b77e47ff5474ecad9e` |
| Metric environment bytes | `515355e0117cbc77c2d8f78644ccf90cef3a195a5ab73a48273f19efdb7e233e` |
| q table bytes | `2d9dd339ed0c0de93e9140ba0a1061fbce00925a0cbca993772c5133cd8250b7` |
| gwr table bytes | `cea695df0af5af01f962e02582786547879baa6777d360a29ec5b4c9c5947472` |

The set contains 14 return-level evidence entries and seven two-member groups:
`01/08`, `02/09`, `03/10`, `04/11`, `05/12`, `06/13`, `07/14`.
Retained per-location evidence supplies member counts, bounds, parameters and
screening counts (inspected first entry: 9 blocks per member, 18 total, required
10; 2046-01-02 through 2054-12-31). All evidence remains available in the
manifest. The old declaration is `provisional_operational`, benchmark
`not assessed`; no candidate report exists in this selected set.

Reader inspection confirms dependencies on the metric environment, unit index,
tables, response request, simulation documents/model-reference record, response
inventory, all native CSV/TOML/temporal selectors, and the collection's intent,
scenario table, forcing and ancillary artifacts. The successful read validates
this chain using the current code, without model execution. Native inventory
contains 14 artifacts and 126 series. Live model files are unnecessary for this
reader; a complete source-project copy retains them nevertheless.

**Absolute dependency:** `config/simulation.json` embeds the original absolute
collection manifest path under `SOURCE/project/scenario_collections/…`.
A byte-exact relocated experiment therefore still reads that original
collection. Do not rewrite its immutable simulation record, or claim that a
successful copied-set read proves standalone portability. Preserve and hash the
original anchor through acceptance, and validate the copied collection
separately. Establish the final retention/reader arrangement before snapshot
acceptance.

## Inventory and snapshot capture

Fresh scratch is `ROOT/.tmp/scratchpad/2026-09-14_0010/gf15-production-integration`.
`source-inventory.json` records relative paths, sizes, SHA-256 and observed link
types for **all 446 files / 657,950,010 bytes** under SOURCE, including its seven
configuration files. No file links were reported. Its byte SHA-256 is
`6483d1285b4e99c46f3587afa9c034956131d5802c77b1f02552d65f58fa7bb4`.
Inventory uses `Get-ChildItem -LiteralPath SOURCE -Recurse -File -Force` and
`Get-FileHash -LiteralPath ... -Algorithm SHA256`; it follows this evidence-selected
tree only. About 87 GB free was observed on C:.

The driver captured the complete source to
`C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/prechange/p3-final-direct`,
outside disposable scratch and output write targets. Its
`SCRATCH/snapshot-result.json` records 446 files / 657,950,010 bytes, all copy
hashes matching, and copied files read-only. Driver reports no overwrite and
source/copy verification. This discovery agent inspected that result; independent
integrity review remains outstanding. The snapshot is anchored, not portable,
for the absolute collection dependency above. A separate working copy will be
the metrics execution target. The driver will retain compact inventory/result
durably; scratch alone is not a retention commitment.

P3 source provenance is retained in `../p3/{final-source-inventory,
final-reviewed-source-inventory,commit-source-inventory}.json` and its explicit
comment/EOF reconciliations. The records landed in `868c4b7c`; their base commit
is `078f508d3ea3a2368d15602f68e7867daf400f3d`. Do not equate the later committed
source inventory to the exact executed bytes without those reconciliations.
Retain those records and exact predecessor source when freezing the snapshot.

## Commands and materialized proposed configuration

`../p3/operations-dedicated-reuse.json`, `commands[label=metrics-reuse]`, records
this exact old argv (exit 0):

```text
ROOT/.pixi/envs/default/python.exe
ROOT/scripts/simulate_system.py
--config ROOT/.tmp/scratchpad/2026-09-11_0010/p3-operations-dedicated-reuse/project_config_metrics.yml
--cores 3 --target metrics
```

Here ROOT expansion gives the exact absolute Windows paths in that JSON.
Recorded old config hash is
`27b5463a3b601f5f6c5fe481e23373d5aa84217973382ebdcff50e3ba242c218`,
workflow settings hash
`474bc8444fb04b943ef43f67466e94e3dbfbde1bbb5034f6eee834d6c41f9433`,
and log hash
`0788e4d6cca443d344d8d6a3d665f5728198d4772a98a528a7ee1eded91e61e7`.
This is a recorded complete-set reuse invocation, not a reconstructed claim
about the initial generating command.

Fresh scratch contains `project_config_gf15_metrics.yml` and
`project_config_simulate_system.yml`, copied in meaning from those retained
metrics configs. They select `operation: metrics-only`, metrics `[q, gwr]`,
experiment `p3_final`, and the explicit original collection. Proposed project
write target is `SCRATCH/working/p3-final-direct/project` (not yet copied).
Disabled workflows stay disabled. The documented future command is:

```powershell
pixi run --manifest-path <qualified-isolated-root>/pixi.toml python ROOT/scripts/simulate_system.py --config SCRATCH/project_config_gf15_metrics.yml --cores 3 --target metrics
```

This is unexecuted; executable, isolated manifest root and retained working-copy
home must be resolved before launch. No invented metrics-only CLI flag is used.
Candidate code/environment will select distinct metric-plan/set identities.
Allowed additional bookkeeping is project `config/runs/invocations/simulation-<id>.json`
and declared attempt logs; preserve native and collection bytes. Detached CSVs
remain estimator-ambiguous: comparisons must retain the manifest and context.

## D7 setup findings and next actions

The current base executable reports Python 3.12.13, NumPy 2.4.6, SciPy 1.18.0,
xclim 0.60.0, pandas 3.0.3, xarray 2026.4.0, netCDF4 1.7.4, pyproj 3.7.2 and
PyYAML 6.0.3 (`base-environment.json`). Existing study venv freshly reports
Python 3.12.13 / NumPy 2.4.6 / SciPy 1.18.0 / lmoments3 1.0.8
(`study-environment-recheck.json`). It remains study-only, not a qualified
production environment. Windows build: conda-forge Python, MSC v.1944 AMD64.

Retained study `wheels/lmoments3-1.0.8-py3-none-any.whl` is present (48,163 bytes)
and freshly matches D7
`984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e`.
Loaded study sources also freshly match D7:

- `__init__.py`: `1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2`
- `distr.py`: `f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee`

Windows NumPy 2.4.6 and SciPy 1.18.0 cp312 wheels are retained alongside it.
That proves local artifacts exist; it does not prove a complete Pixi solve or
Linux artifact availability. `pixi.toml` declares both win-64 and linux-64, with
no lmoments3 dependency yet. A separate non-aliased setup root with copied
manifest/lock and required activation helper is feasible. Resolve Pixi there,
add the D7 dependency/pins, solver-generate both-platform lock, install only
there, and retain actual distribution/native closure plus parity evidence.
Never install into the existing project environment or silently relax targets.

Pixi executable remains unresolved: no PATH command; no executable at
`C:/Users/taner/.pixi/bin/pixi.exe`, `.cargo/bin/pixi*`, Scoop shims, WinGet Links
or checked WinGet package/Local Programs candidates. `.pixi/bin` contains Python
exposure trampolines only; its global manifest exposes Python only.
`docs/install.md` documents Pixi acquisition, not an alternative installed
executable. Next action: provision/identify Pixi explicitly for the isolated
setup. No arbitrary system-wide search or acquisition was attempted.

`wsl --list --quiet` exits 1 and explicitly states Windows Subsystem for Linux
is not installed. No Docker command is on PATH. Therefore no usable local Linux
runtime was established. Practical choices are provisioning local WSL/Linux,
or using an existing authorized Linux runner with the isolated setup and
source-qualified controls. The latter avoids local system installation but
needs an identified execution/transfer route; no data upload is authorized or
performed here. Neither choice establishes exact target package availability
until solved and checked. Linux parity cannot be inferred from Windows.

## Validation boundary and handoff

Verification budget: rapid, numerical unaffected, no new tests. Read-only
reader invocation used the existing environment's `python.exe -B -c` to load
P3 execution evidence and call `read_metric_set(experiment, metric_manifest)`;
the complete returned summary is `SCRATCH/reader.log`. Python metadata and
SHA-256 checks were read-only; imports disabled bytecode writing. No pytest,
lint, numerical fits, workflow, baseline or full-suite gate was warranted or run
for this discovery. Full logs were retained rather than piped through tail.

**Verdict:** a complete usable retained comparison exists and the driver captured
its read-only snapshot; independent integrity acceptance remains unperformed. Pixi acquisition,
isolated solver/install qualification and Linux execution are unresolved
prerequisites. Complete independent integrity review and resolve environment
execution without altering D7 targets. Stage 2 must not
start from this discovery record alone.
