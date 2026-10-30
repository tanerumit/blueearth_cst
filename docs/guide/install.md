---
title: "Install the toolbox"
subtitle: "Windows setup and data-access checks"
---

Use PowerShell from the toolbox checkout for the commands below.
Pixi supplies Python and R. Julia is managed separately through juliaup and must be on `PATH`.
Input datasets are not installed with the software.

## Install the tools

1. Install Git and reopen PowerShell:

   ```powershell
   winget install --id Git.Git --exact --source winget
   ```

2. Install Pixi and reopen PowerShell so the command is available:

   ```powershell
   iwr -useb https://pixi.sh/install.ps1 | iex
   ```

3. Install juliaup and the toolbox's pinned Julia version:

   ```powershell
   winget install Julialang.Juliaup
   juliaup add 1.11.7
   julia +1.11.7 --version
   ```

   The last command should report `julia version 1.11.7`.
   Use the pinned version rather than substituting another 1.11 release.

## Install this checkout

1. Clone the toolbox, then enter its root:

   ```powershell
   git clone https://github.com/tanerumit/blueearth_cst.git
   cd blueearth_cst
   ```

2. Install the locked Python/R environment:

   ```powershell
   pixi install
   ```

3. Install the additional weather-generator and Julia packages:

   ```powershell
   pixi run install
   ```

   This installs the pinned `weathergenr` and Wflow dependencies. Downloads can take time.
   The weather-generator installer verifies both package version and source commit; after pulling
   a toolbox update that changes this pin, rerun `pixi run install-rdeps` before WF3.
   If installation stops, inspect the error before retrying; use
   [troubleshooting](troubleshooting.md) for known symptoms.

## Check the environment and data

1. Run the workflow wiring check:

   ```powershell
   pixi run pytest tests/test_cli.py
   ```

   Read the final pytest summary. `FAILED` or `ERROR` requires diagnosis before proceeding.
   Passing this check does not run the hydrological workflows or establish basin-model accuracy.

2. Check the data catalogs selected by your project.
   The supplied rapid case expects the Deltares P-drive:

   ```powershell
   Test-Path 'P:\wflow_global\hydromt'
   ```

   If this returns `False`, mount the drive or select a catalog for data available to you.
   Check its basin/time coverage and source names. CMIP6 acquisition also needs network access.
   Neither `git clone` nor `pixi install` downloads the catalog's model inputs.

3. Follow the [quick start](quick-start.md) to preview and execute the example.
   That execution needs data, compute time and disk space; installation alone is not a complete example.

For an optional fresh-root all-workflow execution check, `pixi run test-e2e` requires the external data,
Julia, the completed additional installation and CMIP6 network access. It is not a quick installation test.
Use the [validation reference](../../dev/reference/dev-validation.md) for developer qualification work.

## Further setup help

- [Troubleshooting](troubleshooting.md): symptoms, diagnosis and recovery.
- [Environment maintenance](../../dev/scripts/environment-notes.md): developer runtimes and local fixes.
- [Create your own case](new-case.md): basin configuration and external output storage.

The toolbox has no supported Docker image. These steps describe Windows setup; Linux configuration
examples do not establish that this Windows procedure has been verified on Linux.
