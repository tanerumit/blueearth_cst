---
title: "Troubleshooting"
subtitle: "Find the cause before changing the case or environment"
---

Start with the exact error and the execution's `summary.md`, `console.log` and affected workflow log.
Keep the configuration, toolbox revision and failed attempt's evidence when seeking help.
Do not erase outputs as a routine response to a failure.

## Python or shell command is unavailable

If PowerShell reports `Python was not found`, run the command with `pixi run` from the toolbox root.
If entering `pixi shell` is blocked by script policy, use `pixi run` directly; it does not require
changing PowerShell execution policy. Confirm installation with the [setup checks](install.md).

## Julia or weathergenr is unavailable

1. Check `julia +1.11.7 --version`. Install that version with `juliaup add 1.11.7` if it is missing.
   Julia must be on `PATH`; it is not installed inside Pixi.
2. Run `pixi run install` to complete the pinned R/Julia layers.
   The project uses its own R library, not a separately installed personal R library.
3. Read the final error if installation fails. An Rtools message alone does not establish that this
   pure-R weather-generator package needs a separate Rtools installation.

For Julia `Access is denied` or `directory not empty` errors, see the diagnosed installation fixes in
[environment maintenance](../../dev/scripts/environment-notes.md).
Use those remedies for the diagnosed symptom, not as an automatic prerequisite for every installation.

## A catalog root is missing

For `None of the specified roots were found`, inspect the catalogs named by `project.catalog`.
For the supplied P-drive catalog:

```powershell
Test-Path 'P:\wflow_global\hydromt'
```

Mount the drive or choose a catalog that points to available data, then check source names and coverage.
Installing software does not install those datasets. A different catalog is not automatically equivalent
scientific input; review the source choice before reusing results.

## A project is locked or a run was interrupted

1. Confirm no other process is using the project or checkout.
2. Resume through the same owned runner and configuration. For incomplete jobs:

   ```powershell
   pixi run python scripts/run_workflows.py --config <config> --cores 3 -- --rerun-incomplete
   ```

3. If Snakemake reports a stale lock after the active process has stopped, unlock through the runner:

   ```powershell
   pixi run python scripts/run_workflows.py --config <config> --cores 3 -- --unlock
   ```

4. Rerun and inspect the new summary. A hard stop can leave partial native responses that need diagnosis;
   reservation recovery does not repair them.

Use [experiment recovery](running.md#select-resume-or-create-an-experiment) for an interrupted reservation.
Do not recycle allocated experiment numbers or delete locks while a run is active.

## An experiment refuses changed inputs

Review the changed model, collection and simulation settings.
Use `--new-experiment` when scientific inputs changed; keep old results for provenance.
For different indicators over intact completed responses, use the
[indicators-only procedure](running.md#calculate-different-indicators-from-existing-simulations).
It does not supply missing model outputs. Check [indicator inputs](indicators.md#handle-missing-inputs).

## The preview is partial or an indicator value is missing

Checkpoint-dependent inputs may not exist until upstream producers run.
A partial dry-run is not proof that the downstream DAG was inspected.
For historical Qcrit preparation, read the complete
[crop-water requirements](../../blueearth_cst/indicators/sets/crop_water/README.md).
Distinguish `undefined` from `unavailable` using the result's status/reason and set conventions.

## Memory or performance is a concern

Lower `--cores` and inspect [benchmark/resource measurements](benchmarking.md) before increasing concurrency.
Basin size, retained variables and scenario count affect memory/disk needs.
For detailed developer diagnosis and local staging, use
[environment maintenance](../../dev/scripts/environment-notes.md), not a destructive project reset.
