# Installation (pixi-based, from scratch)

Quick step-by-step for setting up `blueearth_cst` on a fresh machine.

## Prerequisites (one-time, machine-wide)

### 1. Install pixi

Windows (PowerShell):
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

Linux/macOS:
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Restart your shell so `pixi` is on `PATH`.

### 2. Install Julia 1.11.x

Use juliaup — conda-forge has no `win-64` Julia build, and Wflow.jl 1.0.x hangs under Julia 1.12.x (see `Project.toml` pin).

Windows:
```powershell
winget install julia
juliaup add 1.11
juliaup default 1.11
```

Linux/macOS:
```bash
curl -fsSL https://install.julialang.org | sh -s -- --default-channel 1.11
```

Verify:
```bash
julia --version    # expect 1.11.x
```

## Repo install

### 3. Clone

```bash
git clone https://github.com/tanerumit/blueearth_cst.git
cd blueearth_cst
```

### 4. Install Python + R toolchain

```bash
pixi install
```

Resolves everything declared in `pixi.toml` from conda-forge into a local `.pixi/` env.

### 5. Install weathergenr (R) + Wflow.jl (Julia)

```bash
pixi run install
```

Runs two tasks defined in `pixi.toml`:

- `install-rdeps` → `Rscript dev/scripts/install_weathergenr.R` (idempotent; installs `tanerumit/weathergenr@v1.2.0` via pak)
- `install-julia` → `julia --project=. -e 'using Pkg; Pkg.instantiate()'` (locks Wflow.jl + ~130 deps from `Manifest.toml`)

### 6. Activate the env

```bash
pixi shell
```

Python, R, Julia, and Snakemake are now on `PATH`.

## Smoke test

Cheapest sanity check (Snakefile `--dry-run` for all three workflows):
```bash
pytest tests/test_cli.py
```

Or run the test workflow end-to-end:
```bash
snakemake all -c 1 -s Snakefile_model_creation --configfile config/snake_config_model_test.yml
```

## Notes

- Re-running `pixi run install` is safe — both subtasks short-circuit if already done.
- On Windows, `weathergenr` lands in the user R library (`~/AppData/Local/R/win-library/<R-ver>`) rather than the pixi env's R site-lib. This dodges a Mingw-w64 byte-compile crash; see the header of `dev/scripts/install_weathergenr.R` for details.
- Linux/Docker replication is currently deferred (`dev/roadmap.md` → "Deferred: Linux replication"). The `Dockerfile` builds but is not exercised end-to-end.
