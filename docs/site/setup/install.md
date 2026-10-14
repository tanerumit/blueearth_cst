# Installing BlueEarth-CST (Windows)

Step-by-step setup for running the BlueEarth Climate Stress Test toolbox on a
fresh Windows machine. Use **Windows PowerShell** for every command below.

Before starting, install Git for Windows so you can clone the project in Step 4:

```powershell
winget install --id Git.Git --exact --source winget
```

Close and reopen PowerShell, then check that `git --version` reports a version.

Steps 1–3 are a one-time machine setup. Steps 4–7 install the project itself.

## Step 1 — Install pixi

pixi manages the project's Python and R tools inside a self-contained folder, so
nothing clutters the rest of your system.

Open PowerShell and run:
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```
Close and reopen PowerShell afterward so it can find the `pixi` command.

## Step 2 — Let Julia install without interference

The hydrological model (Wflow) runs on Julia. Julia's installer downloads files
to a temporary folder and then moves them into place. Windows Defender's
real-time scanning sometimes locks those files mid-move, which makes the install
fail with errors like *"Access is denied"* or *"directory not empty"*.

To prevent this, tell Defender to leave Julia alone. Open PowerShell **as
Administrator** (right-click PowerShell → *Run as administrator*) and run:
```powershell
Add-MpPreference -ExclusionProcess "julia.exe"
Add-MpPreference -ExclusionProcess "juliaup.exe"
```
This is a one-time step and only affects these two programs.

## Step 3 — Install Julia (version 1.11.7)

Install juliaup (the Julia version manager), then the exact Julia version the
project needs:
```powershell
winget install Julialang.Juliaup
juliaup add 1.11.7
```
Using the full name `Julialang.Juliaup` avoids the "multiple packages found"
prompt — do not pick plain "Julialang.Julia".

The version must be exactly **1.11.7**. The project is pinned to it, and a newer
1.11.x will not work. Confirm it installed:
```powershell
julia +1.11.7 --version
```
You should see `julia version 1.11.7`.

## Step 4 — Download the project

```powershell
git clone https://github.com/tanerumit/blueearth_cst.git
cd blueearth_cst
```
Run all the remaining steps from inside this `blueearth_cst` folder.

## Step 5 — Install the Python and R tools

```powershell
pixi install
```
This downloads everything the project needs into a local `.pixi` folder. The
first run can take several minutes.

## Step 6 — Install the weather generator and hydrological model

```powershell
pixi run install
```
This adds two more pieces on top of step 5:

- **weathergenr** — the R weather generator (pinned to `v2.0.1`)
- **Wflow.jl** — the Julia hydrological model and its dependencies (~130 packages)

The Julia part downloads a lot, so give it time. If it stops partway with a
*"directory not empty"* error, simply run `pixi run install` again — it resumes
where it left off. (If it keeps failing here, go back and do step 2.)

## Step 7 — Check that it works

Run the quick check inside the project environment (without opening a separate
shell):
```powershell
pixi run pytest tests/test_cli.py
```
On success, pytest ends with a summary like `20 passed in 12.34s` (the time
varies). A `FAILED` or `ERROR` summary means the check did not pass; read the
error above it before continuing.
This is fast but only checks that the workflows are wired correctly — it does not
actually run them.

The workflow runs below require access to the Deltares P-drive; `git clone` and
`pixi install` do not download its HydroMT data. The supplied project catalogs
expect `P:\wflow_global\hydromt`. Check that it is mounted before running a model:

```powershell
Test-Path 'P:\wflow_global\hydromt'
```

If this returns `False`, mount the Deltares P-drive, or select a catalog for
data available on this machine. The model will fail at Rule 1.01 with
`None of the specified roots were found` until the data are available.

For a full end-to-end check that runs all five workflows to completion on the
small rapid test basin, in a fresh temporary project folder (requires the
Deltares P-drive, Julia, `pixi run install`, and internet access for the
CMIP6 data; expect tens of minutes):
```powershell
pixi run test-e2e
```

Or run the small test model directly:
```powershell
pixi run python scripts/run_workflow.py build_model --config test_case/project_config_baseline.yml --project-dir test_case/test_local --cores 1
```

## Session runtimes

Session creation preserves separate Git worktrees, fixture copies and approval-based landing, but
does not provision a runtime automatically. Existing `.pixi` environments are left in place. Start a
task through the configured Git workflow launcher; use `--no-reseed` only when deliberately retaining
the session's existing fixture snapshot. Session allocation and runtime selection are separate choices.

For a clean, detached slot allocated by the user, run from the primary checkout (replace the skill
directory and task name with the resolved local values), then enter the worktree reported by the tool:

```powershell
$gitWorkflow = '<resolved git-workflow skill directory>'
& .pixi/envs/default/python.exe "$gitWorkflow/scripts/worktree-session.py" task-start --task example --session session-2 --base main --no-launch
Set-Location 'C:/Users/taner/workspace/.worktrees/blueearth_cst/session-2'
```

Do not claim an occupied slot. All three kinds of work below start this way; select the runtime only
after entering the session. Artifact work needing no tools stops before installation or borrowing.

| Work | Runtime |
|---|---|
| Text, task records, or artifacts needing no executable checks | No installation |
| Source checks/artifacts; unchanged dependencies | Borrow a stable runtime, or use the existing local one |
| Dependency changes, install tests, incompatible contracts, workflow qualification | Isolated environment |

### Borrow a stable runtime for development checks

The owner of the lending checkout owns all installation state: Pixi packages, the out-of-lock R
`weathergenr` installation, Graphviz aliases and Julia package/artifact installation. Before lending,
the owner finishes `pixi install --locked`, `pixi run install`, activation and
`pixi run python dev/scripts/check_env.py`. Keep that checkout's dependency files and installation
unchanged until all borrowers finish. Coordinate that interval with its owner; never lend a checkout
whose owner is changing dependencies. A verified primary checkout can be the lender between upgrades.

From the **borrowing session's root**, using PowerShell:

```powershell
$runtime = 'C:/Users/taner/workspace/blueearth_cst'
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime -- python -m pytest tests/test_cli.py
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime -- ruff check .
```

Use the corresponding `<runtime>/.pixi/envs/default/bin/python` bootstrap on Linux. The bootstrap runs
only standard-library coordination code; the child receives Pixi activation. The helper compares
TOML values in `pixi.toml` and both Julia project files, and newline-normalized text in `pixi.lock`,
the R installer and Windows activation script. Any difference fails before Pixi is invoked. This conservative
check also rejects task-only manifest changes. It checks contract equality, not the health of an
arbitrarily modified installation; the owner's provisioning and verification remain prerequisites.

TOML comments and formatting do not affect compatibility.
The helper runs an **executable**, so spell checks out as `python -m pytest ...`, `ruff ...`, or
`Rscript --vanilla ...`; Pixi task names such as `test-fast` are not expanded. It uses
`pixi run --as-is --executable --manifest-path <runtime>/pixi.toml`, preserving the session's working
directory and preventing lock updates and installations. It prints the actual imported Python source
path and rejects imports outside the session. `blueearth_cst` is not an editable installation.
Do not use a lending checkout's named Pixi task directly: named tasks normally execute at that
checkout's manifest root. Pixi documents these flags in its
[run reference](https://pixi.sh/latest/reference/cli/pixi/run/).

`PYTHONPATH` points at the session, user Python packages and bytecode writes are disabled, and the
intended Julia project is the session's `Project.toml`. Use `--project=.` for Julia commands, as the
workflow already does. Julia writes caches into a session-local first depot and reads installed
packages/artifacts from the existing depots. R uses the lending Pixi library; invoke it with
`--vanilla` to avoid personal startup files. The helper clears ambient `R_LIBS`/`R_LIBS_SITE` and disables the
personal R library. Matplotlib, XDG/Cartopy, Numba, PROJ and Ruff caches live in
`.tmp/session-runtime/`; pytest retains
its existing unique, session-local `.tmp/pytest/run-*` directories. Give application outputs explicit
session-local paths. External data mirrors remain external resources and must not be modified by
checks. Existing fixture copies remain independent; do not execute workflows into another session's
`test_local` tree.

Borrowing is cooperative development tooling, not a filesystem sandbox. The helper blocks common
installer commands, but arbitrary Python/R/Julia code can still write to installed packages. Do not
run installers, package-manager APIs, or dependency-mutating checks through it. Do not use borrowed
checks as evidence that a session installs successfully. Full workflow qualification continues to
use an isolated session environment and the validation ladder's required execution coverage.

### Use or return to isolated execution

No `.pixi` link, environment relocation, or persistent shell change is made by borrowing. From the
session root, use the ordinary commands to switch back:

```powershell
pixi install --locked
pixi run install
pixi run python dev/scripts/check_env.py
pixi run pytest tests/test_cli.py
```

For an intentional dependency change, edit the session's manifest, run `pixi install` to solve its
lock, and retain both in the same change. R install changes stay in that session's Pixi library.
Julia's default depot is machine-wide even with an isolated Pixi prefix: when testing Julia
installation itself, set `JULIA_DEPOT_PATH` to a fresh ignored session-local directory **before**
`pixi run install-julia`, and retain it while checking that installation. Never edit shared Julia
packages in place. After dependency work is accepted, only the runtime owner upgrades the lending
environment, with no active borrowers; reverify before lending again.

Keep the configured session capacity; unprovisioned slots are cheap compared with installed runtimes.
A separate lightweight dependency set would add another lock/qualification burden. Pixi's detached
environment setting relocates prefixes; it does not by itself make workspaces share one environment.
Conda hard links can already share package bytes with the machine cache, so logical prefix sizes
overstate marginal disk cost, while every prefix still adds directory entries and private files.
Do not copy or junction `.pixi` directories. See the retained worktree-runtime task evidence for the
measured sizes and limitations; no existing environment, fixture, output or worktree is removed.

## Troubleshooting

- **`Python was not found`** when running a workflow command → prefix it with
  `pixi run`, as in Step 7. Python is installed in the project environment.
- **`None of the specified roots were found`** in Rule 1.01 → the HydroMT data
  root expected by the project's catalog is unavailable. Run the `Test-Path`
  check in Step 7, then mount the P-drive or select a catalog for its location.
- **R says Rtools is required** during `pixi run install` → no separate Rtools
  installation is needed for this toolbox. The pinned `weathergenr` package is
  pure R, and pixi supplies its dependencies. Let the install finish; investigate
  only if it ends with an error.
- **PowerShell says running scripts is disabled** when entering `pixi shell` →
  run commands with `pixi run`, as shown in Step 7. This does not require a
  change to your PowerShell execution policy.
- **"`1.11.7` is not installed"** when running a workflow → you have a different
  Julia version. Run `juliaup add 1.11.7`.
- **"Access is denied" or "directory not empty"** during a Julia install → do
  step 2 (the Defender exclusion), then retry the command.
- **Re-running is safe.** Both `pixi install` and `pixi run install` skip work
  that is already done, so you can rerun them anytime.
- **weathergenr location.** `pixi run install` puts the R weather generator in
  the project's own environment (`.pixi/envs/default/lib/R/library`), so it
  follows the checkout rather than your user account. If you also have a
  separately installed R, its personal library (under `AppData\Local\R`) may
  hold another copy — the project never reads that one, so a version mismatch
  between the two is expected and harmless. Re-run `pixi run install` after
  pulling: it reinstalls whenever the installed version is not the pinned one.
- **Certificate messages from Julia.** If you run Julia by hand and see repeated
  `curl_easy_setopt: 4` messages, they come from a Windows certificate setting.
  The project's install step works around this automatically, so you can ignore
  them.
