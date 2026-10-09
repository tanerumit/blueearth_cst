# Pre-change WF3 reference: execution probes

- Captured: 2026-09-21, worktree `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-2`
- Source revision: `a1a97ffeccea41eed3d1bf449d94f0487121f300`
- Intended runs: isolated automatic-seed and explicit-seed (`123`) WF3 collections.

## Probe 1: direct task invocation

Command:

```text
pixi run snakemake all -c 3 -s generate_scenarios.smk --configfile .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto/config/project_config.yml --dry-run
```

Result: exit 127. Pixi reported `snakemake: command not found`, while listing
the registered Pixi tasks. This did not touch input data or generate outputs.

## Probe 2: environment check

Command:

```text
pixi run env-check
```

Result: exit 1. The environment existed and console scripts were available,
but `weathergenr` was missing (required version 2.0.1) and the Julia
environment was incomplete.

## Dependency recovery

The first `pixi run install` failed in the sandbox because it could not connect
to `api.github.com`. The approved retry completed the R dependency step:
`weathergenr` 2.0.1 was installed under this worktree's `.pixi` environment.
It then started the Julia-instantiation step; Julia is irrelevant to the WF3
weather-generation path, and no Julia-dependent WF3 command is planned.

`pixi run --help` identified the cause of the first probe: an executable that
shares no registered task name requires `-x`. A second bounded dry-run used:

```text
pixi run -x snakemake all -c 3 -s generate_scenarios.smk --configfile .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto/config/project_config.yml --dry-run
```

It printed only the default-profile notice and made no further progress for two
30-second observations. It was interrupted after 60 seconds. The result is
inconclusive rather than a data-access failure: no input path or Python/R
exception was emitted, and dry-run produced no project files beyond the
intentionally created isolated configuration directories.

## Profile-bypass diagnosis

A materially different startup probe bypassed the automatic workflow profile
and Snakemake locking:

```text
pixi run -x -- snakemake all -c 3 -s generate_scenarios.smk --workflow-profile none --nolock --configfile .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto/config/project_config.yml --dry-run --verbose
```

It emitted no output and remained active for 30 seconds before interruption.
This rules out default-profile loading and a stale Snakemake lock as the source
of the observed startup stall. The process still did not reach a DAG, rule,
input path, or exception; the available evidence cannot localize it farther
than WF3 startup/parse-time initialization. A redirect attempt is not retained
as diagnostic evidence because Pixi's task-shell argument handling dropped its
`-x` executable mode; the command above is the valid probe.

## Fixed reference inputs

| file | SHA-256 |
|---|---|
| `auto/config/project_config.yml` | `b9a459d8ebb1b4c02613433b2506f6bc24c3d73b0c2d5b35d95cdf5e5ed0f621` |
| `auto/config/generate_scenarios.yml` | `6a6777e2da47d618c2728121e8b0ec7b3387b21e703a77b6b306a575614dd03f` |
| `explicit-123/config/project_config.yml` | `37ab68a54fb7769d223ee4e62b7d5cb0680060efef6ed61e38b8cfcfe3795f06` |
| `explicit-123/config/generate_scenarios.yml` | `8a02209f16507032bd03902a111ce97f12e0086d516e2ce2f1dec4fb959eff03` |
| `blueearth_cst/experiment/generation_plan.py` | `b0379313e1081e42f70129d57ce78a1317332d245f682aac24d599886107381d` |
| `pixi.lock` | `797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b` |

Observed tools: Pixi 0.70.2, Python 3.14.6, R 4.6.0, and Snakemake 9.6.2.
`weathergenr` 2.0.1 was installed successfully in the worktree-local Pixi R
library. No retained scenario series, resolved seed, seed projection, or
scientific summary exists because neither isolated workflow reached its first
rule.

## Faulthandler localization

The scratch wrapper `faulthandler_snakemake.py` started Snakemake through
`runpy.run_module("snakemake", run_name="__main__")` with the isolated
automatic-seed dry-run arguments. Its 45-second traceback is retained as
`evidence/faulthandler-trace.log`.

It places the block in `tempfile.mkdtemp`, called by
`snakemake.sourcecache.SourceCache.__init__` while `Workflow` is constructed,
before Snakefile parsing. The wrapper then forced both `TEMP` and `TMP` to the
local `runtime-tmp/` directory. A standalone Pixi Python probe successfully
created both an explicit and default temporary directory there, but Snakemake
still timed out in the same source-cache `mkdtemp` call. Thus a simple process
temporary-directory override does not permit the reference run. The unresolved
path is Snakemake's source-cache runtime parent, whose selection is upstream
of workflow execution; no workflow, provider, seed, or source input has run.

## Source-cache routing probe

Following inspection of the installed Snakemake source, the wrapper added:

```text
--shared-fs-usage none
```

This bypassed the prior hang and reached a deterministic failure in 13 seconds:

```text
PermissionError: [WinError 5] Access is denied:
.../runtime-tmp/snakemakeh0f6o2am/source-cache
```

The failure is raised by `os.makedirs(self.cache_path, exist_ok=True)` in
`snakemake.sourcecache.SourceCache.__init__`. Snakemake then also reports an
access-denied error while cleaning that just-created `snakemake...` temporary
directory. This proves the source-cache selection hypothesis and exposes an
environment/ACL fault within the redirected Snakemake temporary subtree. It
is not safe to proceed to the reference run until this runtime-permission
condition is repaired. The traceback appeared in the controlled command
output; its salient exception and command option are recorded here.

## Elevated automatic-seed execution

The following elevated, isolated command used the source-cache setting that
passed the parent's dry-run:

```text
pixi run -x -- snakemake all -c 3 -s generate_scenarios.smk --configfile .tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/auto/config/project_config.yml --workflow-profile none --shared-fs-usage persistence input-output software-deployment sources storage-local-copies software-deployment-cache
```

It built the seven-job WF3 DAG, completed region delineation and stress-test
lookup, then started `3.02_extract_historical_climate`. It wrote
`auto/project/data/climate/historical/era5_20000101_20161231/extract_historical.nc`
(75,747 bytes, timestamp 16:22), but no `basin_cells.csv`. The rule log's last
progress event was `16:22:34 - extract - era5: saving to netCDF`; its size and
timestamp remained unchanged through the seven-minute heartbeat at 16:29.
The run was interrupted as stalled. This is a data-extraction/output-write
stall after source access, distinct from the repaired Snakemake source-cache
startup fault.

The explicit-seed fixture was not executed because it has the same historical
extraction prerequisite. There is consequently no legitimate collection ID,
resolved automatic seed, seed projection, retained series hash, or numerical
fingerprint for either reference case.
