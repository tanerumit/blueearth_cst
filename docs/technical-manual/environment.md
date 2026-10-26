---
title: "Environment and runtime ownership"
format: html
---

Pixi owns the Python/R environment through `pixi.toml` and `pixi.lock`. Julia is managed by juliaup and must
be available on `PATH`; `Project.toml` and `Manifest.toml` describe the Julia project. Do not install Julia
into Pixi or edit generated locks by hand. Use the [installation guide](../guide/install.md) for setup.

## Language boundaries

| Runtime | Operations | Authoritative files |
|---|---|---|
| Python | Runners, configuration, HydroMT preparation, reductions and plots | `pixi.toml`, `pixi.lock` |
| R | `weathergenr` and its generation scripts | `dev/scripts/install_weathergenr.R`, Pixi tasks |
| Julia | Wflow execution | `Project.toml`, `Manifest.toml`, `config/advanced_settings.yml` |
| Snakemake | Workflow scheduling | Five root `.smk` entry points and included rule files |

`config/advanced_settings.yml` declares runtime pins and default resources. Its closed schema is implemented
in `blueearth_cst/shared/advanced_settings.py`. `tests/test_julia_runtime.py` checks Julia pin consistency.
The installed generator revision is owned by the installation script, rather than a separately maintained
package list in this manual.

Run supported commands with `pixi run`. Snakemake Python steps read `snakemake.input`, `output` and `params`.
R workflow scripts use `Rscript --vanilla` and positional arguments. netCDF carries gridded climate and
forcing between languages. WF4 retains native Wflow CSV responses with explicit interpretation metadata.

## Availability and provenance

Installing the runtime does not install the external forcing or model datasets. Catalog roots, network
access, storage and project write access are separate prerequisites. Successful runtime checks do not
establish data coverage, scientific suitability or a qualified model.

Configuration snapshots and collection/simulation/indicator records capture environment and source
identities for their respective consumers. These identities detect incompatible reuse; they do not recreate
an environment on another machine. WF2 bundles likewise record lock hashes and toolbox revision without
installing dependencies. See [execution records](execution-and-provenance.md) and
[results transfer](results-transfer.md).

Developer runtime borrowing and maintenance procedures belong to
[`dev/scripts/environment-notes.md`](../../dev/scripts/environment-notes.md), outside the offline manual.
